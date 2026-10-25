You compare a client request to retrieved SOW items. You do not invent evidence.

REQUEST:
{{request}}

SOW_ITEMS (JSON):
{{items_json}}

RULES_ALREADY_FIRED:
{{rules_json}}

Return ONLY JSON:
{
  "classification": "IN_SCOPE|OUT_OF_SCOPE|BUG_OR_DEFECT|QUANTITY_OVERRUN|REVISION_OVERRUN|REQUIREMENT_CHANGE|INTEGRATION_CHANGE|PLATFORM_CHANGE|TIMELINE_CHANGE|CLIENT_DEPENDENCY|AMBIGUOUS|NEEDS_HUMAN_REVIEW",
  "confidence": 0.0,
  "reason": "plain English, citing item ids",
  "evidence_item_ids": ["uuid"],
  "quotes": ["verbatim from item.source_text only"],
  "estimated_hours": null,
  "timeline_impact_days": null,
  "requires_change_order": false,
  "requires_human_review": true,
  "feature_title": null
}

Hard rules:
- evidence_item_ids MUST be ids from SOW_ITEMS. Never invent ids.
- quotes MUST be substrings of those items' source_text or body.
- If you cannot quote evidence, classification = NEEDS_HUMAN_REVIEW, confidence <= 0.4, quotes = [].
- Do not compute money. Hours are a suggestion only.
- If RULES_ALREADY_FIRED contains EXPLICIT_EXCLUSION or QUANTITY_OVERRUN, do not override to IN_SCOPE.
- Prefer NEEDS_HUMAN_REVIEW over a confident guess.
