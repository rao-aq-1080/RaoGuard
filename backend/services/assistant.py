"""Corner assistant. Groq for prose. Workspace facts from SQLite, never full SOWs."""
from __future__ import annotations

import json

from backend.ai.groq_client import chat as groq_chat
from backend.db import connect
from backend.calc.commercial import format_money

PRODUCT = (
    "RaoGuard is a commercial control layer for software agencies. "
    "Paste a signed SOW, drop a client request, get a quoted clause and an estimated change order. "
    "Python owns hours × rate. Humans approve. Nothing is auto-sent to clients. "
    "Plans: Free trial ($0 — 1 live project, 20 SOW checks), then Starter $29/mo, Studio $59/mo, Agency $89/mo — priced for Pakistan software houses, USD invoices, PKR by arrangement. "
    "Founder: Muhammad Abdullah, Pakistan. Working name, not a filed trademark. "
    "Estimates only. Not legal advice."
)


def _workspace_facts() -> str:
    conn = connect()
    s = conn.execute("select agency_name, owner_name, currency from settings where id=1").fetchone()
    projects = [dict(r) for r in conn.execute("select id, name, client_name, contract_value, status from projects order by created_at desc")]
    lines = [
        f"Agency: {s['agency_name'] if s else '—'}. Owner: {s['owner_name'] if s else '—'}.",
        f"{len(projects)} project(s).",
    ]
    cur = (s["currency"] if s else "USD")
    for p in projects[:8]:
        recovered = 0.0
        at_risk = 0.0
        nreq = conn.execute("select count(*) as c from requests where project_id=?", (p["id"],)).fetchone()["c"]
        for a in conn.execute("select payload, status from analyses where project_id=?", (p["id"],)):
            result = json.loads(a["payload"])
            price = float(result.get("client_price") or 0)
            if a["status"] in ("approved", "invoiced") and result.get("requires_change_order"):
                recovered += price
            if a["status"] == "new" and result.get("requires_change_order"):
                at_risk += price
        recent = []
        for a in conn.execute(
            "select payload, status from analyses where project_id=? order by created_at desc limit 4",
            (p["id"],),
        ):
            result = json.loads(a["payload"])
            recent.append(
                f"{result.get('classification') or a['status']} {format_money(result.get('client_price') or 0, cur)} ({a['status']})"
            )
        lines.append(
            f"- {p['name']} / {p['client_name']}: SOW {format_money(p.get('contract_value') or 0, cur)}, "
            f"at risk {format_money(at_risk, cur)}, recovered {format_money(recovered, cur)}, "
            f"{nreq} requests. Recent: {', '.join(recent) or 'none'}."
        )
    conn.close()
    return "\n".join(lines)


def _local_reply(message: str, facts: str | None) -> str:
    m = (message or "").lower()
    if any(k in m for k in ("price", "pricing", "plan", "package", "fee", "rs", "pkr", "dollar", "trial", "free", "starter", "studio", "agency")):
        return (
            "Free trial: $0, 1 live project, 20 SOW checks — the real workflow, with limits. "
            "Then Starter $29/mo, Studio $59/mo, Agency $89/mo. USD invoices; PKR by arrangement."
        )
    if any(k in m for k in ("how", "work", "sow", "change order", "scope")):
        return (
            "Fence the signed SOW, paste a client request, get a quoted clause and an estimated change order. "
            "You approve. Nothing is emailed automatically."
        )
    if facts and any(k in m for k in ("project", "northstar", "client", "recover", "risk", "dashboard", "request")):
        return "From this workspace:\n" + facts
    if facts:
        return "I can help with this workspace and with how RaoGuard works. Ask about a project, recovered fees, or a plan.\n\n" + facts
    return (
        "I can explain RaoGuard, the Free trial, pricing ($29 / $59 / $89), and how change orders work. "
        "Sign in to ask about your live projects."
    )


def answer(message: str, history: list[dict] | None, signed_in: bool) -> dict:
    facts = _workspace_facts() if signed_in else None
    system = (
        "You are the RaoGuard in-app assistant. Short, professional, no emoji. "
        "Use only the product notes and workspace facts below. Never invent SOW clauses or dollar figures. "
        "Never offer to email a client. If asked for legal advice, refuse. "
        "If the facts do not contain the answer, say so.\n\n"
        f"PRODUCT\n{PRODUCT}\n"
    )
    if facts:
        system += f"\nWORKSPACE FACTS (no full SOW text)\n{facts}\n"
    else:
        system += "\nThe visitor is not signed in. Do not claim access to private project data.\n"
    groq = groq_chat(system, message, history)
    if groq:
        return {"reply": groq, "groq": True}
    return {"reply": _local_reply(message, facts), "groq": False}
