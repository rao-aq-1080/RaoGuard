Write a client-facing reply. Do not add facts that are not in INPUT.

TONE: {{tone}}  (professional | friendly | direct | relationship-friendly)

INPUT JSON:
{{input_json}}

Return ONLY JSON: {"reply": "..."}.

The reply must:
- thank them
- state the classification in human language
- quote or closely paraphrase the SOW evidence if provided
- if a change order is needed, include hours, price, and timeline exactly as given (do not recalculate)
- say work does not start until they approve
- be <= 160 words
- not mention RaoGuard, Groq, or "the AI"
