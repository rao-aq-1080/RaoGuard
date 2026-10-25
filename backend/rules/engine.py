"""Deterministic SOW parser + request classifier.

Rules fire before any LLM. Citations must be substrings of stored source_text.
Python does not invent clause numbers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

STOP = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with", "our",
    "your", "we", "you", "will", "be", "is", "are", "this", "that", "from", "by",
    "as", "at", "it", "its", "into", "than", "then", "can", "just", "also", "need",
    "please", "would", "could", "should", "have", "has", "been", "was", "were",
    "not", "but", "if", "so", "up", "out", "all", "any", "per", "via", "using",
}

HEADER = re.compile(
    r"^\s*(?:(?:\d+|[ivx]+)[\.\)]\s*|#{1,3}\s+|section\s+\d+[:.\s]+)?"
    r"(scope of work|in[- ]scope|deliverables?|explicitly out of scope|"
    r"out[- ]of[- ]scope|exclusions?|not included|assumptions?|commercials?|"
    r"fees? &? ?timeline|commercial terms|timeline|change orders?|"
    r"acceptance criteria|payment terms|project overview)\s*:?\s*$",
    re.I,
)

KIND_FROM_HEADER = {
    "scope of work": "deliverable",
    "in-scope": "deliverable",
    "in scope": "deliverable",
    "deliverable": "deliverable",
    "deliverables": "deliverable",
    "explicitly out of scope": "exclusion",
    "out-of-scope": "exclusion",
    "out of scope": "exclusion",
    "exclusion": "exclusion",
    "exclusions": "exclusion",
    "not included": "exclusion",
    "assumption": "assumption",
    "assumptions": "assumption",
    "commercial": "commercial",
    "commercials": "commercial",
    "fees & timeline": "commercial",
    "fees timeline": "commercial",
    "commercial terms": "commercial",
    "timeline": "timeline",
    "change order": "other",
    "change orders": "other",
    "acceptance criteria": "other",
    "payment terms": "commercial",
    "project overview": "deliverable",
}

FEATURES = [
    {"keys": ["loyalty", "points program", "rewards program", "stamp card", "stamps"], "hours": 40, "title": "Custom loyalty / points program"},
    {"keys": ["mobile app", "ios app", "android app", "react native", "flutter", "native app"], "hours": 160, "title": "Native mobile application"},
    {"keys": ["wholesale", "b2b", "net pricing", "trade portal", "dealer portal", "wholesale login"], "hours": 80, "title": "B2B / wholesale portal"},
    {"keys": ["netsuite", "sap ", "erp", "dynamics 365", "odoo"], "hours": 64, "title": "ERP integration"},
    {"keys": ["salesforce", "hubspot crm", "dynamics crm"], "hours": 32, "title": "CRM integration"},
    {"keys": ["amazon", "ebay", "marketplace", "walmart marketplace"], "hours": 48, "title": "Marketplace integration"},
    {"keys": ["headless", "hydrogen", "storefront api"], "hours": 120, "title": "Headless storefront"},
    {"keys": ["multilingual", "multi-language", "i18n", "localization", "second language", "translation"], "hours": 28, "title": "Additional language / locale"},
    {"keys": ["multi-currency", "currency switcher"], "hours": 16, "title": "Multi-currency support"},
    {"keys": ["apple pay", "google pay"], "hours": 16, "title": "Wallet / alternative checkout"},
    {"keys": ["custom checkout", "checkout extension"], "hours": 36, "title": "Custom checkout extensibility"},
    {"keys": ["photography", "photo shoot", "product photos"], "hours": 20, "title": "Photography production"},
    {"keys": ["copywriting", "copy deck", "brand identity", "logo design"], "hours": 24, "title": "Copy / brand identity"},
    {"keys": ["gift card", "store credit"], "hours": 12, "title": "Gift cards / store credit"},
    {"keys": ["algolia", "searchspring"], "hours": 20, "title": "Enhanced search"},
    {"keys": ["extra revision", "another round", "one more round", "additional revision"], "hours": 8, "title": "Additional revision round"},
]

CREEP = [
    "can you also", "can we also", "can you just", "can we just",
    "while you're at it", "while you are at it", "one more thing",
    "real quick", "quick add", "small change", "shouldn't take long",
    "should not take long", "won't take long", "in addition", "we forgot",
    "we also need", "also need", "would be great if", "was implied",
    "obviously included", "thought that was included",
]

BUG = [
    "bug", "broken", "overlap", "overflow", "error", "500", "404", "crash",
    "doesn't work", "does not work", "not working", "cannot click",
    "console error", "alignment", "regression", "layout",
]

QTY_RE = re.compile(
    r"(\d[\d,]*)\s*(skus?|products?|pages?|screens?|templates?|revisions?|languages?|locales?|integrations?|hours?|weeks?|users?)",
    re.I,
)


@dataclass
class Quantity:
    n: float
    unit: str


@dataclass
class ScopeItem:
    id: str
    kind: str
    title: str
    body: str
    source_text: str
    section_label: str = ""
    quantity_value: Optional[float] = None
    quantity_unit: Optional[str] = None
    tokens: list[str] = field(default_factory=list)
    page_hint: Optional[int] = None


@dataclass
class ParsedSow:
    title: str
    client: str
    fee: Optional[float]
    rate: Optional[float]
    internal_rate: Optional[float]
    weeks: Optional[float]
    items: list[ScopeItem]
    raw: str


def tokenize(s: str) -> list[str]:
    s = re.sub(r"[^a-z0-9+.# ]", " ", (s or "").lower())
    return [w for w in s.split() if len(w) > 2 and w not in STOP]


def jaccard(a: list[str], b: list[str]) -> float:
    if not a or not b:
        return 0.0
    A, B = set(a), set(b)
    return len(A & B) / len(A | B)


def extract_quantities(text: str) -> list[Quantity]:
    out = []
    for m in QTY_RE.finditer(text or ""):
        out.append(Quantity(n=float(m.group(1).replace(",", "")), unit=m.group(2).lower()))
    # "400 SKUs but now need 620" — second number has no unit
    if out:
        unit = out[0].unit
        nums = [float(x.replace(",", "")) for x in re.findall(r"\b(\d[\d,]*)\b", text or "")]
        known = {q.n for q in out}
        for n in nums:
            if n not in known and 0 < n < 100000:
                out.append(Quantity(n=n, unit=unit))
    return out


def _money(text: str) -> Optional[float]:
    m = re.search(r"\$\s?([\d,]+(?:\.\d{2})?)", text)
    return float(m.group(1).replace(",", "")) if m else None


def _rate(text: str) -> Optional[float]:
    m = (
        re.search(r"blended rate[^\d$]{0,24}\$?\s?([\d,]+)", text, re.I)
        or re.search(r"\$\s?([\d,]+)\s*/\s*h(?:ou)?r", text, re.I)
        or re.search(r"([\d,]+)\s*(?:usd\s*)?/\s*h(?:ou)?r", text, re.I)
    )
    return float(m.group(1).replace(",", "")) if m else None


def _internal_rate(text: str) -> Optional[float]:
    m = re.search(r"internal(?: cost)? rate[^\d$]{0,24}\$?\s?([\d,]+)", text, re.I)
    return float(m.group(1).replace(",", "")) if m else None


def _weeks(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*weeks?", text, re.I)
    return float(m.group(1)) if m else None


def _line_meta(text: str, label: str) -> str:
    m = re.search(rf"{label}\s*:\s*(.+)", text, re.I)
    return m.group(1).split("\n")[0].strip() if m else ""


def _header_kind(label: str) -> str:
    k = re.sub(r"\s+", " ", label.lower()).strip()
    return KIND_FROM_HEADER.get(k, "deliverable")


def _split_items(block: str) -> list[str]:
    lines = [
        re.sub(r"^\s*[-*•]\s+", "", re.sub(r"^\s*\d+[\.\)]\s+", "", l)).strip()
        for l in (block or "").split("\n")
    ]
    lines = [l for l in lines if l]
    items, buf = [], ""
    for line in lines:
        if re.match(r"^[-*•]", line) or len(line) < 180:
            if buf:
                items.append(buf)
            buf = re.sub(r"^[-*•]\s*", "", line)
        else:
            buf = f"{buf} {line}" if buf else line
    if buf:
        items.append(buf)
    return [x for x in items if len(x) > 8]


def parse_sow(text: str) -> ParsedSow:
    raw = (text or "").replace("\r", "").strip()
    sections: list[tuple[str, str, str]] = []
    current = None
    for line in raw.split("\n"):
        h = HEADER.match(line)
        if h:
            if current:
                sections.append(current)
            current = (_header_kind(h.group(1)), h.group(1).strip(), "")
        elif current:
            kind, title, body = current
            current = (kind, title, body + ("\n" if body else "") + line)
    if current:
        sections.append(current)

    items: list[ScopeItem] = []
    n = 0

    def add(kind: str, title: str, body: str):
        nonlocal n
        n += 1
        qs = extract_quantities(body)
        k = kind
        if qs and ("up to" in body.lower() or "limit" in body.lower() or kind == "deliverable"):
            if qs and kind == "deliverable" and any(q.unit.startswith("sku") or q.unit.startswith("rev") for q in qs):
                pass
        start = raw.find(body[: min(80, len(body))])
        items.append(
            ScopeItem(
                id=f"si_{n:03d}",
                kind=k,
                title=title,
                body=body.strip(),
                source_text=body.strip(),
                section_label=title,
                quantity_value=qs[0].n if qs else None,
                quantity_unit=qs[0].unit if qs else None,
                tokens=tokenize(body),
            )
        )

    if not sections:
        for i, body in enumerate(_split_items(raw), start=1):
            add("deliverable", f"Item {i}", body)
    else:
        for kind, title, body in sections:
            chunks = _split_items(body)
            if not chunks and body.strip():
                add(kind, title, body.strip())
            else:
                for chunk in chunks:
                    add(kind, title, chunk)

    return ParsedSow(
        title=_line_meta(raw, "project") or "Untitled engagement",
        client=_line_meta(raw, "client") or "Client",
        fee=_money(raw),
        rate=_rate(raw),
        internal_rate=_internal_rate(raw),
        weeks=_weeks(raw),
        items=items,
        raw=raw,
    )


def find_feature(request: str):
    r = f" {request.lower()} "
    best = None
    for f in FEATURES:
        hits = sum(1 for k in f["keys"] if k in r)
        if hits and (best is None or hits > best["hits"] or (hits == best["hits"] and f["hours"] > best["hours"])):
            best = {**f, "hits": hits}
    return best


def creep_score(request: str) -> int:
    r = request.lower()
    return sum(1 for p in CREEP if p in r)


def is_bug(request: str) -> bool:
    r = request.lower()
    return any(b in r for b in BUG)


def feature_hit(text: str, request: str) -> bool:
    t, r = (text or "").lower(), (request or "").lower()
    for f in FEATURES:
        if any(k in r for k in f["keys"]) and any(k in t for k in f["keys"]):
            return True
    return False


def best_item(items: list[ScopeItem], tokens: list[str], kind: Optional[str] = None):
    best = None
    for it in items:
        if kind and it.kind != kind:
            continue
        score = jaccard(it.tokens, tokens)
        if best is None or score > best[1]:
            best = (it, score)
    return best


def quantity_conflict(items: list[ScopeItem], request: str):
    req_q = extract_quantities(request)
    if not req_q:
        return None
    for it in items:
        if it.quantity_value is None or not it.quantity_unit:
            continue
        for rq in req_q:
            same = rq.unit[:3] == it.quantity_unit[:3]
            if same and rq.n > it.quantity_value:
                return {
                    "item": it,
                    "from_n": it.quantity_value,
                    "to_n": rq.n,
                    "extra": rq.n - it.quantity_value,
                    "unit": it.quantity_unit,
                }
    return None


def hours_for_quantity(unit: str, extra: float) -> float:
    u = (unit or "").lower()
    if u.startswith("sku") or u.startswith("prod"):
        return max(4, round((extra / 50) * 4))
    if u.startswith("page") or u.startswith("screen") or u.startswith("temp"):
        return extra * 6
    if u.startswith("rev"):
        return extra * 8
    return extra * 4


def timeline_days(hours: float) -> float:
    if hours <= 0:
        return 0
    return round(max(1, hours / 8) * 1.25, 1)


def _clip(s: str, n: int) -> str:
    t = re.sub(r"\s+", " ", s or "").strip()
    return t if len(t) <= n else t[: n - 1] + "…"


def client_reply(result: dict, tone: str = "professional") -> str:
    cls = result["classification"]
    hours = result.get("estimated_hours") or 0
    price = result.get("client_price") or 0
    ev = result.get("evidence") or []
    quote = f' The signed SOW states: “{_clip(ev[0]["quote"], 160)}”' if ev else ""
    feature = result.get("feature_title") or "this extra work"
    money = f"${price:,.0f}"

    if cls in ("IN_SCOPE", "BUG_OR_DEFECT"):
        if tone == "direct":
            return f"Reviewed against the SOW — this is in current scope.{quote} We’ll take it in the current sprint. No change order."
        if tone == "friendly":
            return f"Thanks for flagging this — we checked the SOW and it’s covered.{quote} We’ll fold it into the current work, no extra fee."
        return f"Thank you. We reviewed this against the current Statement of Work and confirm it falls within the signed scope.{quote} We will handle it in the current sprint with no change to fees."

    if cls in ("AMBIGUOUS", "NEEDS_HUMAN_REVIEW"):
        return (
            f"Thank you for the request. Some of this may sit at the edge of the current SOW.{quote} "
            f"Before the team starts, we should confirm in writing. If it is extra, a change order would be "
            f"approximately {hours:g} hours ({money})."
        )

    if tone == "direct":
        return (
            f"This sits outside the current SOW ({feature}).{quote} "
            f"Happy to do it as a change order: ~{hours:g}h, {money}. Clock starts after you sign."
        )
    if tone == "friendly":
        return (
            f"Love that idea. It falls outside the current scope ({feature.lower()}).{quote} "
            f"I can put a change order together: about {hours:g} hours, {money}, plus a small timeline add. "
            f"Want me to send it over before the team touches it?"
        )
    return (
        f"Thank you for the request. {feature} is not included in the existing Statement of Work.{quote} "
        f"Estimated effort: {hours:g} hours. Additional cost: {money}. "
        f"Estimated timeline impact: {result.get('timeline_impact_days') or 0:g} working days. "
        f"We can prepare the change order for approval before development begins."
    )


def analyze(
    request: str,
    items: list[ScopeItem],
    sow_text: str,
    client_rate: float = 165,
    internal_rate: float = 80,
    tone: str = "professional",
) -> dict:
    request = (request or "").strip()
    tokens = tokenize(request)
    feature = find_feature(request)
    creep = creep_score(request)
    bug = is_bug(request)
    qty = quantity_conflict(items, request)
    excl = best_item(items, tokens, "exclusion")
    deliv = best_item(items, tokens, "deliverable")
    rules: list[str] = []

    classification = "AMBIGUOUS"
    confidence = 0.58
    reason = "Not enough overlap with a specific SOW clause to call this cleanly."
    matched: list[ScopeItem] = []
    hours = float(feature["hours"]) if feature else 12.0
    title = feature["title"] if feature else "Out-of-scope request"
    requires_co = False
    requires_human = True

    if not items:
        classification = "NEEDS_HUMAN_REVIEW"
        confidence = 0.2
        reason = "No scope baseline is loaded. Upload or paste a signed SOW first."
        rules.append("NO_SCOPE")
        hours = 0
        title = "Missing scope"
    elif bug and deliv and deliv[1] >= 0.04:
        classification = "BUG_OR_DEFECT"
        confidence = 0.88
        reason = "Reads as a defect / QA item on work already in the SOW, not a new deliverable."
        matched = [deliv[0]]
        hours = 0
        title = "In-scope defect"
        requires_human = False
        rules.append("INCLUDED_BROKEN")
    elif qty:
        classification = "QUANTITY_OVERRUN"
        confidence = 0.86
        reason = (
            f"SOW caps {qty['unit']} at {qty['from_n']:g}. The request asks for {qty['to_n']:g} "
            f"({qty['extra']:g} over). Quantity inflation is a change order."
        )
        matched = [qty["item"]]
        hours = hours_for_quantity(qty["unit"], qty["extra"])
        title = f"Increase {qty['unit']} from {qty['from_n']:g} to {qty['to_n']:g}"
        requires_co = True
        requires_human = False
        rules.append("QUANTITY_OVERRUN")
    else:
        exclusion_hit = None
        if feature:
            for it in items:
                if it.kind == "exclusion" and feature_hit(it.body, request):
                    exclusion_hit = it
                    break
        if feature and exclusion_hit:
            classification = "OUT_OF_SCOPE"
            confidence = 0.94
            reason = f"“{feature['title']}” is named in the exclusions. Starting this without a change order is unbilled work."
            matched = [exclusion_hit]
            hours = float(feature["hours"])
            title = feature["title"]
            requires_co = True
            requires_human = False
            rules.append("EXPLICIT_EXCLUSION")
        elif feature:
            named_out = any(
                it.kind == "exclusion"
                and (jaccard(it.tokens, tokens) > 0.06 or feature_hit(it.body, request))
                for it in items
            )
            in_deliv = any(it.kind == "deliverable" and feature_hit(it.body, request) for it in items)
            if not in_deliv and (named_out or creep > 0 or not deliv or deliv[1] < 0.18):
                classification = "OUT_OF_SCOPE"
                confidence = 0.92 if named_out else (0.84 if creep else 0.76)
                reason = (
                    f"“{feature['title']}” matches an explicit exclusion."
                    if named_out
                    else f"“{feature['title']}” is not a signed deliverable."
                    + (" The request also uses classic scope-creep language." if creep else "")
                )
                matched = []
                if excl and excl[1] > 0.04:
                    matched.append(excl[0])
                if deliv and deliv[1] > 0.04:
                    matched.append(deliv[0])
                hours = float(feature["hours"])
                title = feature["title"]
                requires_co = True
                requires_human = False
                rules.append("EXPLICIT_EXCLUSION" if named_out else "UNLISTED_FEATURE")

        if classification == "AMBIGUOUS":
            if feature and any(it.kind == "exclusion" and feature_hit(it.body, request) for it in items):
                classification = "OUT_OF_SCOPE"
                confidence = 0.91
                reason = f"Exclusions already call out this work (“{feature['title']}”)."
                matched = [it for it in items if it.kind == "exclusion" and feature_hit(it.body, request)]
                hours = float(feature["hours"])
                title = feature["title"]
                requires_co = True
                requires_human = False
                rules.append("EXPLICIT_EXCLUSION")
            elif deliv and deliv[1] >= 0.22 and not feature:
                classification = "IN_SCOPE"
                confidence = min(0.90, 0.60 + deliv[1])
                reason = "Strong overlap with a signed deliverable. Treat as current-scope unless a quantity or exclusion says otherwise."
                matched = [deliv[0]]
                hours = 0
                title = "In-scope request"
                requires_human = False
                rules.append("DELIVERABLE_OVERLAP")
            elif excl and excl[1] >= 0.16:
                classification = "OUT_OF_SCOPE"
                confidence = min(0.92, 0.70 + excl[1] * 0.8)
                reason = "Closest match is an exclusion clause, not a deliverable."
                matched = [excl[0]]
                title = feature["title"] if feature else "Excluded work"
                hours = float(feature["hours"]) if feature else 16
                requires_co = True
                rules.append("EXCLUSION_SIMILARITY")
            elif feature and (not deliv or deliv[1] < 0.14):
                classification = "OUT_OF_SCOPE"
                confidence = 0.78
                reason = f"“{feature['title']}” does not appear as a deliverable in the SOW."
                matched = [deliv[0]] if deliv and deliv[1] > 0.04 else []
                hours = float(feature["hours"])
                title = feature["title"]
                requires_co = True
                rules.append("UNLISTED_FEATURE")
            elif creep > 0 and (not deliv or deliv[1] < 0.2):
                classification = "OUT_OF_SCOPE"
                confidence = 0.72
                reason = "Scope-creep phrasing plus weak overlap with signed deliverables."
                matched = [deliv[0]] if deliv and deliv[1] > 0.03 else []
                hours = float(feature["hours"]) if feature else 12
                requires_co = True
                rules.append("CREEP_LANGUAGE")

    if classification in ("OUT_OF_SCOPE", "QUANTITY_OVERRUN") and not matched:
        classification = "NEEDS_HUMAN_REVIEW"
        confidence = min(confidence, 0.40)
        requires_human = True
        requires_co = False
        rules.append("NO_EVIDENCE")
        reason = "The request looks extra, but no stored SOW excerpt could be quoted. Human review required."

    from backend.calc.commercial import snapshot

    if classification in ("IN_SCOPE", "BUG_OR_DEFECT"):
        hours = 0
        requires_co = False
        snap = snapshot(0, client_rate, internal_rate, 0)
    else:
        snap = snapshot(hours, client_rate, internal_rate, timeline_days(hours))

    evidence = []
    for it in matched:
        evidence.append(
            {
                "scope_item_id": it.id,
                "kind": it.kind,
                "section_label": it.section_label,
                "quote": it.source_text,
                "role": "supports",
            }
        )

    result = {
        "classification": classification,
        "confidence": round(confidence, 3),
        "reason": reason,
        "feature_title": feature["title"] if feature else title,
        "change_order_title": title if classification in ("IN_SCOPE", "BUG_OR_DEFECT") else f"Change order — {title}",
        "estimated_hours": snap["estimated_hours"],
        "timeline_impact_days": snap["timeline_impact_days"],
        "requires_change_order": requires_co,
        "requires_human_review": requires_human,
        "rules_fired": rules,
        "evidence": evidence,
        "groq_used": False,
        **snap,
    }
    result["client_reply"] = client_reply(result, tone)
    return result
