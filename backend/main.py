from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from backend.auth import (
    DEFAULT_EMAIL,
    DEFAULT_PASSWORD,
    TERMS_VERSION,
    accept_terms,
    create_session,
    create_user,
    drop_session,
    public_user,
    seed_owner,
    set_password,
    user_by_email,
    user_from_token,
    verify_password,
)
from backend.calc.commercial import snapshot
from backend.db import audit, connect, init, now, uid
from backend.documents.extract import UnreadableDocument, extract_bytes
from backend.rules.engine import parse_sow
from backend.seed import seed_if_empty
from backend.services.analyze import run_analysis

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

app = FastAPI(title="RaoGuard", version="0.1.0")


COOKIE = "rg_session"
PUBLIC_API = ("/api/health", "/api/demo/", "/api/auth/", "/api/chat", "/api/plans")


class AuthGate(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/api/") and not any(path.startswith(p) or path == p.rstrip("/") for p in PUBLIC_API):
            user = user_from_token(request.cookies.get(COOKIE))
            if not user:
                return JSONResponse({"detail": "Sign in required"}, status_code=401)
            if not user.get("terms_accepted_at") or user.get("terms_version") != TERMS_VERSION:
                if path != "/api/auth/me":
                    return JSONResponse(
                        {"detail": "Accept the Terms of Use and Privacy Policy to continue."},
                        status_code=403,
                    )
            request.state.user = user
        return await call_next(request)


app.add_middleware(AuthGate)


@app.on_event("startup")
def startup():
    init()
    seed_owner()
    seed_if_empty()


def set_session_cookie(response, token: str) -> None:
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
        path="/",
    )


class SettingsIn(BaseModel):
    agency_name: str | None = None
    owner_name: str | None = None
    currency: str | None = None
    client_rate: float | None = None
    internal_rate: float | None = None
    tone: str | None = None
    groq_enabled: bool | None = None
    plan: str | None = None


class ProjectIn(BaseModel):
    name: str = ""
    client_name: str = ""
    sow_text: str
    client_rate: float | None = None
    internal_rate: float | None = None


class ScopePatch(BaseModel):
    kind: str | None = None
    title: str | None = None
    body: str | None = None


class RequestIn(BaseModel):
    body: str
    source: str = "paste"


class CommercialIn(BaseModel):
    estimated_hours: float
    client_rate: float | None = None
    internal_rate: float | None = None
    timeline_impact_days: float | None = None


class DecideIn(BaseModel):
    action: str
    note: str = ""


class ProjectPatch(BaseModel):
    name: str | None = None
    client_name: str | None = None
    client_rate: float | None = None
    internal_rate: float | None = None
    status: str | None = None


def settings_row() -> dict:
    conn = connect()
    row = dict(conn.execute("select * from settings where id=1").fetchone())
    conn.close()
    row["groq_enabled"] = bool(row["groq_enabled"])
    row["plan"] = row.get("plan") or "free"
    return row


def require_plan(action: str) -> None:
    from backend.services.plans import get_plan, limit_message, usage_snapshot

    s = settings_row()
    msg = limit_message(action, get_plan(s.get("plan")), usage_snapshot())
    if msg:
        raise HTTPException(402, msg)


def project_bundle(pid: str) -> dict:
    conn = connect()
    p = conn.execute("select * from projects where id=?", (pid,)).fetchone()
    if not p:
        conn.close()
        raise HTTPException(404, "Project not found")
    project = dict(p)
    items = [dict(r) for r in conn.execute("select * from scope_items where project_id=? order by id", (pid,))]
    reqs = [dict(r) for r in conn.execute("select * from requests where project_id=? order by created_at desc", (pid,))]
    analyses = []
    for a in conn.execute("select * from analyses where project_id=? order by created_at desc", (pid,)):
        d = dict(a)
        d["result"] = json.loads(d.pop("payload"))
        analyses.append(d)
    conn.close()
    recovered = sum(
        float(a["result"].get("client_price") or 0)
        for a in analyses
        if a["status"] in ("approved", "invoiced") and a["result"].get("requires_change_order")
    )
    at_risk = sum(
        float(a["result"].get("client_price") or 0)
        for a in analyses
        if a["status"] == "new" and a["result"].get("requires_change_order")
    )
    project["recovered"] = recovered
    project["at_risk"] = at_risk
    project["scope_items"] = items
    project["requests"] = reqs
    project["analyses"] = analyses
    return project


@app.get("/api/health")
def health():
    return {"ok": True, "product": "RaoGuard", "mode": "rules-first"}


@app.get("/api/plans")
def list_plans():
    from backend.services.plans import catalog

    return {
        "plans": catalog(),
        "billing": "No payment is collected in this local copy. Choosing a paid plan here only lifts the caps so you can evaluate them. A real invoice would be by hand.",
    }


class LoginIn(BaseModel):
    email: str
    password: str
    accept_terms: bool = False


class RegisterIn(BaseModel):
    name: str = ""
    email: str
    password: str
    accept_terms: bool = False


class PasswordIn(BaseModel):
    current_password: str
    new_password: str


@app.get("/api/auth/config")
def auth_config():
    return {"terms_version": TERMS_VERSION}


@app.get("/api/auth/me")
def auth_me(request: Request):
    user = user_from_token(request.cookies.get(COOKIE))
    if not user:
        return {"user": None, "terms_version": TERMS_VERSION}
    return {"user": public_user(user), "terms_version": TERMS_VERSION}


@app.post("/api/auth/login")
def auth_login(body: LoginIn):
    user = user_by_email(body.email)
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Email or password is wrong.")
    needs_terms = (not user.get("terms_accepted_at")) or user.get("terms_version") != TERMS_VERSION
    if needs_terms and not body.accept_terms:
        raise HTTPException(403, "Accept the Terms of Use and Privacy Policy to sign in.")
    if body.accept_terms:
        accept_terms(user["id"])
        user = user_by_email(body.email)
    token = create_session(user["id"])
    out = JSONResponse({"ok": True, "user": public_user(user)})
    set_session_cookie(out, token)
    return out


@app.post("/api/auth/register")
def auth_register(body: RegisterIn):
    email = (body.email or "").strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(400, "Use a real email address.")
    if len(body.password or "") < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")
    if not body.accept_terms:
        raise HTTPException(400, "Accept the Terms of Use and Privacy Policy to create an account.")
    if user_by_email(email):
        raise HTTPException(409, "That email is already registered. Sign in instead.")
    require_plan("seat")
    user = create_user(email, body.name, body.password)
    token = create_session(user["id"])
    out = JSONResponse({"ok": True, "user": public_user(user)})
    set_session_cookie(out, token)
    return out


@app.post("/api/auth/logout")
def auth_logout(request: Request):
    drop_session(request.cookies.get(COOKIE))
    out = JSONResponse({"ok": True})
    out.delete_cookie(COOKIE, path="/")
    return out


@app.post("/api/auth/accept-terms")
def auth_accept_terms(request: Request):
    user = user_from_token(request.cookies.get(COOKIE))
    if not user:
        raise HTTPException(401, "Sign in required")
    accept_terms(user["id"])
    user = user_by_email(user["email"])
    return {"ok": True, "user": public_user(user)}


@app.post("/api/auth/password")
def auth_password(body: PasswordIn, request: Request):
    user = user_from_token(request.cookies.get(COOKIE))
    if not user:
        raise HTTPException(401, "Sign in required")
    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(400, "Current password is wrong.")
    if len(body.new_password or "") < 8:
        raise HTTPException(400, "New password must be at least 8 characters.")
    set_password(user["id"], body.new_password)
    return {"ok": True}


class DemoIn(BaseModel):
    body: str


class ChatTurn(BaseModel):
    role: str
    content: str = ""


class ChatIn(BaseModel):
    message: str
    history: list[ChatTurn] = Field(default_factory=list)


@app.post("/api/chat")
def assistant_chat(body: ChatIn, request: Request):
    msg = (body.message or "").strip()
    if len(msg) < 2:
        raise HTTPException(400, "Type a question.")
    if len(msg) > 800:
        raise HTTPException(400, "Keep questions under 800 characters.")
    user = user_from_token(request.cookies.get(COOKIE))
    signed = bool(user) and user.get("terms_accepted_at") and user.get("terms_version") == TERMS_VERSION
    from backend.services.assistant import answer

    return answer(msg, [t.model_dump() for t in body.history], signed)


@app.post("/api/demo/analyze")
def demo_analyze(body: DemoIn):
    """Northstar dry-run — does not persist."""
    bundle = project_bundle("prj_northstar")
    s = settings_row()
    result = run_analysis(
        body.body,
        bundle["scope_items"],
        bundle["sow_text"],
        bundle["client_rate"] or s["client_rate"],
        bundle["internal_rate"] or s["internal_rate"],
        s["tone"],
    )
    return {"result": result}


@app.post("/api/demo/report")
def demo_report(body: DemoIn):
    """Printable analyzer sheet for the public Northstar dry-run. Does not persist."""
    from backend.services.docs import analysis_inner, slug, wrap_document

    bundle = project_bundle("prj_northstar")
    s = settings_row()
    result = run_analysis(
        body.body,
        bundle["scope_items"],
        bundle["sow_text"],
        bundle["client_rate"] or s["client_rate"],
        bundle["internal_rate"] or s["internal_rate"],
        s["tone"],
    )
    inner = analysis_inner(s, bundle, {"body": body.body}, result, "demo")
    title = result.get("change_order_title") or "Analyzer report"
    filename = f"analyzer-{slug(title)}.html"
    return {"html": inner, "document": wrap_document(title, inner), "title": title, "filename": filename}


@app.get("/api/settings")
def get_settings():
    from backend.services.plans import public_status

    s = settings_row()
    s["groq_configured"] = bool(__import__("os").environ.get("GROQ_API_KEY"))
    s["data_notice"] = (
        "Rules-only by default. If you add a Groq key, we send the request text and retrieved "
        "SOW clauses (not necessarily the full PDF) to Groq in the US. Nothing is auto-sent to clients."
    )
    s["billing"] = public_status(s.get("plan"))
    return s


@app.put("/api/settings")
def put_settings(body: SettingsIn):
    from backend.services.plans import PLANS

    s = settings_row()
    data = s | {k: v for k, v in body.model_dump().items() if v is not None}
    if data.get("plan") and data["plan"] not in PLANS:
        raise HTTPException(400, "Unknown plan.")
    started = s.get("plan_started_at")
    if data.get("plan") and data["plan"] != s.get("plan"):
        started = now()
    conn = connect()
    conn.execute(
        """update settings set agency_name=?, owner_name=?, currency=?, client_rate=?,
           internal_rate=?, tone=?, groq_enabled=?, plan=?, plan_started_at=? where id=1""",
        (
            data["agency_name"],
            data["owner_name"],
            data["currency"],
            data["client_rate"],
            data["internal_rate"],
            data["tone"],
            1 if data.get("groq_enabled") else 0,
            data.get("plan") or "free",
            started,
        ),
    )
    conn.commit()
    conn.close()
    return get_settings()


@app.get("/api/dashboard")
def dashboard():
    from backend.services.plans import public_status

    s = settings_row()
    projects = list_projects()
    recovered = sum(p["recovered"] for p in projects)
    at_risk = sum(p["at_risk"] for p in projects)
    conn = connect()
    analyses = []
    for a in conn.execute("select * from analyses"):
        d = dict(a)
        d["result"] = json.loads(d["payload"])
        analyses.append(d)
    counts: dict[str, int] = {}
    for a in analyses:
        k = a["result"].get("classification") or "UNKNOWN"
        counts[k] = counts.get(k, 0) + 1
    conn.close()
    return {
        "agency_name": s["agency_name"],
        "owner_name": s["owner_name"],
        "recovered": recovered,
        "at_risk": at_risk,
        "project_count": len(projects),
        "request_count": sum(p["request_count"] for p in projects),
        "by_class": counts,
        "projects": projects,
        "disclaimer": "Estimates only. Not a legal opinion. Human approval required.",
        "billing": public_status(s.get("plan")),
    }


@app.get("/api/projects/{pid}/precedents")
def precedents(pid: str, q: str = ""):
    bundle = project_bundle(pid)
    from backend.rules.engine import jaccard, tokenize

    qtok = tokenize(q or "")
    rows = []
    for a in bundle["analyses"]:
        req = next((r for r in bundle["requests"] if r["id"] == a["request_id"]), None)
        body = (req or {}).get("body") or ""
        score = jaccard(qtok, tokenize(body)) if qtok else 0.2
        rows.append(
            {
                "analysis_id": a["id"],
                "status": a["status"],
                "request": body,
                "classification": a["result"].get("classification"),
                "price": a["result"].get("client_price") or 0,
                "title": a["result"].get("change_order_title"),
                "score": round(score, 3),
            }
        )
    rows.sort(key=lambda r: r["score"], reverse=True)
    return {"project_id": pid, "items": rows[:12], "note": "History, not a rule. This agency’s past decisions only."}


@app.get("/api/projects")
def list_projects():
    conn = connect()
    rows = [dict(r) for r in conn.execute("select * from projects order by created_at desc")]
    out = []
    for p in rows:
        b = project_bundle(p["id"])
        out.append(
            {
                "id": b["id"],
                "name": b["name"],
                "client_name": b["client_name"],
                "contract_value": b["contract_value"],
                "client_rate": b["client_rate"],
                "status": b["status"],
                "created_at": b["created_at"],
                "recovered": b["recovered"],
                "at_risk": b["at_risk"],
                "request_count": len(b["requests"]),
                "scope_count": len(b["scope_items"]),
            }
        )
    conn.close()
    return out


@app.post("/api/projects/upload")
async def create_project_from_file(
    file: UploadFile = File(...),
    client_name: str = Form(""),
    name: str = Form(""),
):
    data = await file.read()
    try:
        text = extract_bytes(data, file.filename or "file.txt")
    except UnreadableDocument as e:
        raise HTTPException(400, str(e))
    return create_project(ProjectIn(sow_text=text, client_name=client_name, name=name))


@app.patch("/api/projects/{pid}")
def patch_project(pid: str, body: ProjectPatch):
    conn = connect()
    row = conn.execute("select * from projects where id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Project not found")
    d = dict(row)
    name = body.name if body.name is not None else d["name"]
    client_name = body.client_name if body.client_name is not None else d["client_name"]
    client_rate = body.client_rate if body.client_rate is not None else d["client_rate"]
    internal_rate = body.internal_rate if body.internal_rate is not None else d["internal_rate"]
    status = body.status if body.status is not None else d["status"]
    if status not in ("active", "closed"):
        conn.close()
        raise HTTPException(400, "status must be active or closed")
    conn.execute(
        "update projects set name=?, client_name=?, client_rate=?, internal_rate=?, status=? where id=?",
        (name, client_name, client_rate, internal_rate, status, pid),
    )
    audit(conn, "project_updated", pid, {"status": status})
    conn.commit()
    conn.close()
    return project_bundle(pid)


@app.get("/api/projects/{pid}/audit")
def project_audit(pid: str):
    project_bundle(pid)
    conn = connect()
    rows = [
        dict(r)
        for r in conn.execute(
            "select * from audit_events where project_id=? order by created_at desc limit 50",
            (pid,),
        )
    ]
    conn.close()
    return {"items": rows}


@app.post("/api/projects")
def create_project(body: ProjectIn):
    sow = (body.sow_text or "").strip()
    if len(sow) < 40:
        raise HTTPException(400, "Paste a real Statement of Work (at least a few clauses).")
    require_plan("project")
    parsed = parse_sow(sow)
    s = settings_row()
    pid = uid("prj")
    conn = connect()
    conn.execute(
        """insert into projects
           (id, name, client_name, contract_value, currency, timeline_weeks,
            client_rate, internal_rate, sow_text, status, created_at)
           values (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            pid,
            body.name or parsed.title,
            body.client_name or parsed.client,
            parsed.fee,
            s["currency"],
            parsed.weeks,
            body.client_rate or parsed.rate or s["client_rate"],
            body.internal_rate or parsed.internal_rate or s["internal_rate"],
            sow,
            "active",
            now(),
        ),
    )
    for it in parsed.items:
        conn.execute(
            """insert into scope_items
               (id, project_id, kind, title, body, source_text, section_label,
                quantity_value, quantity_unit, created_at)
               values (?,?,?,?,?,?,?,?,?,?)""",
            (
                uid("si"),
                pid,
                it.kind,
                it.title,
                it.body,
                it.source_text,
                it.section_label,
                it.quantity_value,
                it.quantity_unit,
                now(),
            ),
        )
    audit(conn, "scope_extracted", pid, {"items": len(parsed.items)})
    conn.commit()
    conn.close()
    return project_bundle(pid)


@app.get("/api/projects/{pid}")
def get_project(pid: str):
    return project_bundle(pid)


@app.post("/api/projects/{pid}/documents")
async def upload_document(pid: str, file: UploadFile = File(...)):
    data = await file.read()
    try:
        text = extract_bytes(data, file.filename or "file.txt")
    except UnreadableDocument as e:
        raise HTTPException(400, str(e))
    parsed = parse_sow(text)
    conn = connect()
    p = conn.execute("select * from projects where id=?", (pid,)).fetchone()
    if not p:
        conn.close()
        raise HTTPException(404, "Project not found")
    conn.execute("delete from scope_items where project_id=?", (pid,))
    conn.execute(
        "update projects set sow_text=?, contract_value=?, timeline_weeks=? where id=?",
        (text, parsed.fee, parsed.weeks, pid),
    )
    for it in parsed.items:
        conn.execute(
            """insert into scope_items
               (id, project_id, kind, title, body, source_text, section_label,
                quantity_value, quantity_unit, created_at)
               values (?,?,?,?,?,?,?,?,?,?)""",
            (uid("si"), pid, it.kind, it.title, it.body, it.source_text, it.section_label, it.quantity_value, it.quantity_unit, now()),
        )
    audit(conn, "document_uploaded", pid, {"filename": file.filename, "items": len(parsed.items)})
    conn.commit()
    conn.close()
    return project_bundle(pid)


@app.patch("/api/scope-items/{sid}")
def patch_item(sid: str, body: ScopePatch):
    conn = connect()
    row = conn.execute("select * from scope_items where id=?", (sid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Scope item not found")
    d = dict(row)
    kind = body.kind or d["kind"]
    title = body.title or d["title"]
    text = body.body if body.body is not None else d["body"]
    conn.execute(
        "update scope_items set kind=?, title=?, body=?, source_text=? where id=?",
        (kind, title, text, text, sid),
    )
    audit(conn, "scope_item_edited", d["project_id"], {"id": sid})
    conn.commit()
    row = conn.execute("select * from scope_items where id=?", (sid,)).fetchone()
    conn.close()
    return dict(row)


@app.post("/api/projects/{pid}/requests")
def create_request(pid: str, body: RequestIn):
    if len((body.body or "").strip()) < 8:
        raise HTTPException(400, "Paste a client request.")
    require_plan("analyze")
    conn = connect()
    p = conn.execute("select * from projects where id=?", (pid,)).fetchone()
    if not p:
        conn.close()
        raise HTTPException(404, "Project not found")
    project = dict(p)
    items = [dict(r) for r in conn.execute("select * from scope_items where project_id=?", (pid,))]
    s = settings_row()
    result = run_analysis(
        body.body,
        items,
        project["sow_text"],
        project["client_rate"] or s["client_rate"],
        project["internal_rate"] or s["internal_rate"],
        s["tone"],
    )
    rid = uid("req")
    aid = uid("an")
    conn.execute(
        "insert into requests (id, project_id, source, body, created_at) values (?,?,?,?,?)",
        (rid, pid, body.source, body.body, now()),
    )
    conn.execute(
        "insert into analyses (id, request_id, project_id, payload, status, created_at) values (?,?,?,?,?,?)",
        (aid, rid, pid, json.dumps(result), "new", now()),
    )
    audit(conn, "analyzed", pid, {"analysis_id": aid, "classification": result["classification"]})
    conn.commit()
    conn.close()
    return {"request_id": rid, "analysis_id": aid, "result": result, "status": "new"}


@app.post("/api/analyses/{aid}/commercial")
def edit_commercial(aid: str, body: CommercialIn):
    conn = connect()
    row = conn.execute("select * from analyses where id=?", (aid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Analysis not found")
    a = dict(row)
    result = json.loads(a["payload"])
    p = dict(conn.execute("select * from projects where id=?", (a["project_id"],)).fetchone())
    s = settings_row()
    cr = body.client_rate if body.client_rate is not None else (p["client_rate"] or s["client_rate"])
    ir = body.internal_rate if body.internal_rate is not None else (p["internal_rate"] or s["internal_rate"])
    days = body.timeline_impact_days
    snap = snapshot(body.estimated_hours, cr, ir, days if days is not None else result.get("timeline_impact_days") or 0)
    result.update(snap)
    result["edited_by_human"] = True
    from backend.rules.engine import client_reply

    result["client_reply"] = client_reply(result, s["tone"])
    conn.execute("update analyses set payload=? where id=?", (json.dumps(result), aid))
    audit(conn, "commercial_edited", a["project_id"], {"analysis_id": aid})
    conn.commit()
    conn.close()
    return result


@app.post("/api/analyses/{aid}/decide")
def decide(aid: str, body: DecideIn):
    if body.action not in ("approve", "reject", "edit", "clarify"):
        raise HTTPException(400, "action must be approve|reject|edit|clarify")
    conn = connect()
    row = conn.execute("select * from analyses where id=?", (aid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Analysis not found")
    a = dict(row)
    status = {"approve": "approved", "reject": "dismissed", "edit": "new", "clarify": "clarifying"}[body.action]
    conn.execute("update analyses set status=? where id=?", (status, aid))
    conn.execute(
        "insert into decisions (id, analysis_id, action, note, created_at) values (?,?,?,?,?)",
        (uid("dec"), aid, body.action, body.note, now()),
    )
    audit(conn, "decided", a["project_id"], {"analysis_id": aid, "action": body.action})
    conn.commit()
    conn.close()
    return {"ok": True, "status": status}



def _analysis_pack(aid: str) -> tuple[dict, dict, dict, dict, dict]:
    conn = connect()
    row = conn.execute("select * from analyses where id=?", (aid,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Analysis not found")
    a = dict(row)
    result = json.loads(a["payload"])
    p = dict(conn.execute("select * from projects where id=?", (a["project_id"],)).fetchone())
    req = dict(conn.execute("select * from requests where id=?", (a["request_id"],)).fetchone())
    conn.close()
    return settings_row(), p, req, result, a


@app.get("/api/analyses/{aid}/change-order")
def change_order(aid: str):
    from backend.services.docs import change_order_inner, slug, wrap_document

    s, p, req, result, _a = _analysis_pack(aid)
    inner = change_order_inner(s, p, req, result)
    title = result.get("change_order_title") or "Change order"
    filename = f"change-order-{slug(title)}.html"
    return {
        "html": inner,
        "document": wrap_document(title, inner),
        "title": title,
        "filename": filename,
        "price": result.get("client_price"),
    }


@app.get("/api/analyses/{aid}/sheet")
def analysis_sheet(aid: str):
    from backend.services.docs import analysis_inner, slug, wrap_document

    s, p, req, result, a = _analysis_pack(aid)
    inner = analysis_inner(s, p, req, result, a.get("status") or "new")
    title = result.get("change_order_title") or "Analyzer report"
    filename = f"analyzer-{slug(title)}.html"
    return {"html": inner, "document": wrap_document(title, inner), "title": title, "filename": filename}


@app.get("/api/projects/{pid}/report")
def project_report(pid: str):
    from backend.services.docs import project_report_inner, slug, wrap_document

    bundle = project_bundle(pid)
    s = settings_row()
    inner = project_report_inner(s, bundle, bundle.get("analyses") or [], bundle.get("requests") or [])
    title = f"Report — {bundle.get('name') or pid}"
    filename = f"report-{slug(bundle.get('name') or pid)}.html"
    return {"html": inner, "document": wrap_document(title, inner), "title": title, "filename": filename}


if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    html = (FRONTEND / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
