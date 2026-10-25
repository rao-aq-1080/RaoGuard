from __future__ import annotations

from backend.ai.validate import quote_is_grounded
from backend.calc.commercial import snapshot
from backend.rules.engine import ScopeItem, analyze as rules_analyze, client_reply, timeline_days


def items_from_rows(rows: list[dict]) -> list[ScopeItem]:
    out = []
    for r in rows:
        out.append(
            ScopeItem(
                id=r["id"],
                kind=r["kind"],
                title=r["title"],
                body=r["body"],
                source_text=r["source_text"],
                section_label=r.get("section_label") or r["title"],
                quantity_value=r.get("quantity_value"),
                quantity_unit=r.get("quantity_unit"),
                tokens=__import__("backend.rules.engine", fromlist=["tokenize"]).tokenize(r["body"]),
            )
        )
    return out


def run_analysis(
    request: str,
    item_rows: list[dict],
    sow_text: str,
    client_rate: float,
    internal_rate: float,
    tone: str = "professional",
) -> dict:
    items = items_from_rows(item_rows)
    result = rules_analyze(
        request=request,
        items=items,
        sow_text=sow_text,
        client_rate=client_rate,
        internal_rate=internal_rate,
        tone=tone,
    )

    # Optional Groq: prose only. Never money, never invented evidence, never override a hard rule.
    try:
        from backend.ai.groq_client import compare_with_groq

        groq = compare_with_groq(
            request,
            [
                {
                    "id": r["id"],
                    "kind": r["kind"],
                    "title": r["title"],
                    "body": (r["body"] or "")[:400],
                    "section_label": r.get("section_label"),
                }
                for r in item_rows[:12]
            ],
            list(result.get("rules_fired") or []),
        )
    except Exception:
        groq = None
    if groq and isinstance(groq, dict):
        result["groq_used"] = True
        if groq.get("reason") and result.get("classification") not in ("NEEDS_HUMAN_REVIEW",):
            result["reason"] = str(groq["reason"])[:900]
        if groq.get("feature_title") and not result.get("feature_title"):
            result["feature_title"] = str(groq["feature_title"])[:120]

    # Evidence must be grounded in stored source_text
    grounded = []
    by_id = {r["id"]: r for r in item_rows}
    for ev in result.get("evidence") or []:
        src = by_id.get(ev["scope_item_id"])
        if not src:
            continue
        if quote_is_grounded(ev["quote"], src["source_text"], src["body"]):
            grounded.append(ev)
    result["evidence"] = grounded

    if result["classification"] in ("OUT_OF_SCOPE", "QUANTITY_OVERRUN", "REVISION_OVERRUN") and not grounded:
        result["classification"] = "NEEDS_HUMAN_REVIEW"
        result["confidence"] = min(float(result["confidence"]), 0.40)
        result["requires_human_review"] = True
        result["requires_change_order"] = False
        result["reason"] = (
            "The request looks extra, but no stored SOW excerpt could be quoted. Human review required."
        )
        result["rules_fired"] = list(result.get("rules_fired") or []) + ["NO_EVIDENCE"]
        snap = snapshot(0, client_rate, internal_rate, 0)
        result.update(snap)
        result["estimated_hours"] = 0
        result["client_reply"] = client_reply(result, tone)
        return result

    # Recalculate money in Python (never trust a model)
    if result["classification"] in ("IN_SCOPE", "BUG_OR_DEFECT"):
        snap = snapshot(0, client_rate, internal_rate, 0)
    else:
        snap = snapshot(
            result.get("estimated_hours") or 0,
            client_rate,
            internal_rate,
            result.get("timeline_impact_days") or timeline_days(result.get("estimated_hours") or 0),
        )
    result.update(snap)
    result["client_reply"] = client_reply(result, tone)
    result["disclaimer"] = (
        "Estimate. Not a legal opinion. Not a binding engineering quote. "
        "A human must approve before this is treated as a commercial decision."
    )
    return result
