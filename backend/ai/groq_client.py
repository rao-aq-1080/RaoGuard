"""Optional Groq layer. Never computes money. Never invents evidence ids."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def groq_enabled() -> bool:
    return bool(os.environ.get("GROQ_API_KEY")) and os.environ.get("GROQ_ENABLED", "true").lower() != "false"


def _client():
    from groq import Groq

    return Groq(api_key=os.environ["GROQ_API_KEY"])


def _models() -> tuple[str, str]:
    return (
        os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
        os.environ.get("GROQ_MODEL_FALLBACK", "llama-3.1-8b-instant"),
    )


def _read_prompt(name: str) -> str:
    p = ROOT / "prompts" / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def compare_with_groq(request: str, items: list[dict], rules: list[str]) -> dict | None:
    if not groq_enabled():
        return None
    try:
        from groq import Groq
    except ImportError:
        return None

    prompt = _read_prompt("04_compare.md")
    payload = prompt.replace("{{request}}", request)
    payload = payload.replace("{{items_json}}", json.dumps(items, ensure_ascii=False)[:8000])
    payload = payload.replace("{{rules_json}}", json.dumps(rules))

    model, fallback = _models()
    client = _client()

    def _call(m: str) -> dict:
        resp = client.chat.completions.create(
            model=m,
            messages=[
                {"role": "system", "content": "Return only valid JSON. Never invent evidence ids."},
                {"role": "user", "content": payload},
            ],
            temperature=0.1,
            max_tokens=800,
        )
        text = resp.choices[0].message.content or "{}"
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()
        return json.loads(text)

    try:
        return _call(model)
    except Exception:
        try:
            return _call(fallback)
        except Exception:
            return None


def chat(system: str, user: str, history: list[dict] | None = None) -> str | None:
    """Short assistant reply. Never used for money or evidence."""
    if not groq_enabled():
        return None
    try:
        client = _client()
    except Exception:
        return None
    model, fallback = _models()
    messages = [{"role": "system", "content": (system or "")[:4000]}]
    for h in (history or [])[-6]:
        role = h.get("role")
        content = str(h.get("content") or "").strip()
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content[:800]})
    messages.append({"role": "user", "content": (user or "")[:800]})

    def _talk(m: str) -> str:
        resp = client.chat.completions.create(
            model=m,
            messages=messages,
            temperature=0.2,
            max_tokens=350,
        )
        return (resp.choices[0].message.content or "").strip()

    try:
        return _talk(model)
    except Exception:
        try:
            return _talk(fallback)
        except Exception:
            return None
