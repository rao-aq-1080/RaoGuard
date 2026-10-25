import re


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def quote_is_grounded(quote: str, source_text: str, body: str = "") -> bool:
    q = normalize(quote)
    if len(q) < 8:
        return False
    return q in normalize(source_text) or q in normalize(body)
