"""Printable invoice-style HTML. Estimates only. Nothing is sent."""
from __future__ import annotations

from html import escape
from datetime import datetime, timezone

from backend.calc.commercial import format_money
from backend.services.plans import get_plan


def _esc(s) -> str:
    return escape("" if s is None else str(s))


def wrap_document(title: str, inner: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{_esc(title)}</title>
<style>
  @page {{ margin: 18mm; }}
  body {{ margin: 0; background: #efe6d5; color: #14110c;
         font-family: ui-sans-serif, system-ui, sans-serif; }}
  .sheet {{ max-width: 720px; margin: 16px auto; background: #f7f1e4;
            padding: 36px 40px; border: 1px solid rgba(20,17,12,.12); }}
  h1 {{ font-family: Palatino, Georgia, serif; font-size: 1.7rem; margin: .4rem 0 1rem; }}
  h3 {{ font-family: Palatino, Georgia, serif; margin: 1.2rem 0 .35rem; font-size: 1.05rem; }}
  header {{ display: flex; justify-content: space-between; gap: 1rem; }}
  .brand {{ font-family: Palatino, Georgia, serif; font-size: 1.45rem; }}
  .meta {{ font-size: 13px; color: #5c564c; text-align: right; }}
  .kicker {{ font-size: 11px; letter-spacing: .18em; text-transform: uppercase; color: #5c564c; }}
  table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 14px; }}
  th, td {{ text-align: left; padding: .55rem .4rem; border-bottom: 1px solid rgba(20,17,12,.12); }}
  th {{ font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #5c564c; }}
  blockquote {{ margin: .4rem 0; padding-left: .8rem; border-left: 2px solid #c9bba4; color: #5c564c; }}
  .muted {{ color: #5c564c; font-size: 12.5px; line-height: 1.45; }}
  .sigs {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2.6rem; }}
  .sigs div {{ border-top: 1px solid rgba(20,17,12,.4); padding-top: .4rem; font-size: 12px; color: #5c564c; }}
  .total {{ font-family: Palatino, Georgia, serif; font-size: 1.8rem; margin: .6rem 0; }}
  .stamp {{ display: inline-block; border: 2px solid #b42318; color: #b42318;
            padding: .2rem .5rem; letter-spacing: .14em; text-transform: uppercase;
            font-family: Palatino, Georgia, serif; font-size: 11px; transform: rotate(-6deg); }}
</style>
</head>
<body><div class="sheet">{inner}</div></body>
</html>
"""


def _stamp(label: str) -> str:
    return f'<span class="stamp">{_esc((label or "REVIEW").replace("_", " "))}</span>'


def _quotes(ev: list) -> str:
    if not ev:
        return "<p class='muted'>No stored excerpt could be quoted.</p>"
    return "".join(
        f"<blockquote>{_esc(e.get('quote'))}</blockquote>"
        f"<p class='muted'>{_esc(e.get('kind'))} · {_esc(e.get('section_label'))}</p>"
        for e in ev
    )


def _brand_line(settings: dict) -> str:
    if get_plan(settings.get("plan")).get("white_label"):
        return ""
    return "<p class='muted'>Drafted with RaoGuard. Not sent. Human approval required. Estimate, not a legal opinion.</p>"


def change_order_inner(settings: dict, project: dict, request: dict, result: dict) -> str:
    ev = result.get("evidence") or []
    cur = settings.get("currency") or "USD"
    fee = format_money(result.get("client_price") or 0, cur)
    rate = format_money(result.get("client_rate") or 0, cur)
    hours = result.get("estimated_hours") or 0
    issued = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""
    <header>
      <div>
        <div class="kicker">Change order · estimate</div>
        <div class="brand">{_esc(settings.get("agency_name"))}</div>
      </div>
      <div class="meta">
        {_stamp(result.get("classification"))}<br>
        {issued}<br>
        {_esc(project.get("client_name"))}<br>
        {_esc(project.get("name"))}
      </div>
    </header>
    <h1>{_esc(result.get("change_order_title") or "Change order")}</h1>
    <h3>Requested work</h3>
    <p>“{_esc(request.get("body"))}”</p>
    <h3>Why this is outside the SOW</h3>
    <p>{_esc(result.get("reason"))}</p>
    {_quotes(ev)}
    <table>
      <tr><th>Hours</th><th>Client rate</th><th>Fee (estimate)</th></tr>
      <tr><td>{_esc(hours)}</td><td>{_esc(rate)}</td><td>{_esc(fee)}</td></tr>
    </table>
    <div class="total">{_esc(fee)}</div>
    <p class="muted">Internal cost (estimate): {_esc(format_money(result.get("internal_cost") or 0, cur))}
    · Potential gross profit: {_esc(format_money(result.get("gross_profit") or 0, cur))}
    · Timeline: +{_esc(result.get("timeline_impact_days") or 0)} working days
    · Original SOW: {_esc(format_money(project.get("contract_value") or 0, cur))}.</p>
    <p class="muted">Work does not begin until both parties sign. Figures are estimates, not a guaranteed engineering quote. This is not an invoice until you send it.</p>
    {_brand_line(settings)}
    <div class="sigs"><div>Agency · {_esc(settings.get("agency_name"))}</div><div>Client · {_esc(project.get("client_name"))}</div></div>
    """


def analysis_inner(settings: dict, project: dict, request: dict, result: dict, status: str) -> str:
    ev = result.get("evidence") or []
    cur = settings.get("currency") or "USD"
    issued = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""
    <header>
      <div>
        <div class="kicker">Analyzer report</div>
        <div class="brand">{_esc(settings.get("agency_name"))}</div>
      </div>
      <div class="meta">
        {_stamp(result.get("classification"))}<br>
        Status: {_esc(status)}<br>
        {issued}<br>
        {_esc(project.get("client_name"))}<br>
        {_esc(project.get("name"))}
      </div>
    </header>
    <h1>{_esc(result.get("change_order_title") or "Scope check")}</h1>
    <p class="muted">{int(round((result.get("confidence") or 0) * 100))}% · rules: {_esc(", ".join(result.get("rules_fired") or []) or "rules")}</p>
    <h3>Client request</h3>
    <p>“{_esc(request.get("body"))}”</p>
    <h3>Finding</h3>
    <p>{_esc(result.get("reason"))}</p>
    {_quotes(ev)}
    <table>
      <tr><th>Hours</th><th>Rate</th><th>Client fee</th><th>Internal cost</th><th>Gross profit</th></tr>
      <tr>
        <td>{_esc(result.get("estimated_hours") or 0)}</td>
        <td>{_esc(format_money(result.get("client_rate") or 0, cur))}</td>
        <td>{_esc(format_money(result.get("client_price") or 0, cur))}</td>
        <td>{_esc(format_money(result.get("internal_cost") or 0, cur))}</td>
        <td>{_esc(format_money(result.get("gross_profit") or 0, cur))}</td>
      </tr>
    </table>
    <h3>Draft reply (not sent)</h3>
    <p>{_esc(result.get("client_reply") or "—")}</p>
    <p class="muted">{_esc(result.get("disclaimer") or "Estimate. Not a legal opinion. Not a binding quote.")}</p>
    {_brand_line(settings)}
    """


def project_report_inner(settings: dict, project: dict, analyses: list[dict], requests: list[dict]) -> str:
    cur = settings.get("currency") or project.get("currency") or "USD"
    issued = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reqs = {r["id"]: r for r in requests}
    recovered = 0.0
    at_risk = 0.0
    rows = []
    for a in analyses:
        result = a.get("result") or {}
        price = float(result.get("client_price") or 0)
        if a.get("status") in ("approved", "invoiced") and result.get("requires_change_order"):
            recovered += price
        if a.get("status") == "new" and result.get("requires_change_order"):
            at_risk += price
        req = reqs.get(a.get("request_id")) or {}
        rows.append(
            "<tr>"
            f"<td>{_esc(a.get('status'))}</td>"
            f"<td>{_esc((result.get('classification') or '').replace('_', ' '))}</td>"
            f"<td>{_esc((req.get('body') or '')[:90])}</td>"
            f"<td>{_esc(result.get('estimated_hours') or 0)}</td>"
            f"<td>{_esc(format_money(price, cur))}</td>"
            "</tr>"
        )
    body = "".join(rows) or "<tr><td colspan='5'>No checks yet.</td></tr>"
    return f"""
    <header>
      <div>
        <div class="kicker">Project report</div>
        <div class="brand">{_esc(settings.get("agency_name"))}</div>
      </div>
      <div class="meta">
        {issued}<br>
        {_esc(project.get("client_name"))}<br>
        {_esc(project.get("name"))}
      </div>
    </header>
    <h1>Commercial control report</h1>
    <p class="muted">Signed SOW vs incoming requests. Hours × rate in Python. Humans decide. Nothing was sent to the client.</p>
    <table>
      <tr><th>SOW value</th><th>Rate</th><th>Recovered (approved)</th><th>At risk (not approved)</th><th>Checks</th></tr>
      <tr>
        <td>{_esc(format_money(project.get("contract_value") or 0, cur))}</td>
        <td>{_esc(format_money(project.get("client_rate") or 0, cur))}/h</td>
        <td>{_esc(format_money(recovered, cur))}</td>
        <td>{_esc(format_money(at_risk, cur))}</td>
        <td>{len(analyses)}</td>
      </tr>
    </table>
    <h3>Requests checked</h3>
    <table>
      <tr><th>Status</th><th>Class</th><th>Request</th><th>Hours</th><th>Fee</th></tr>
      {body}
    </table>
    <p class="muted">Estimates only. Not a legal opinion. Not a binding quote. Not an invoice until you send it.</p>
    {_brand_line(settings)}
    """


def slug(s: str) -> str:
    keep = "".join(ch.lower() if ch.isalnum() else "-" for ch in (s or "document"))
    while "--" in keep:
        keep = keep.replace("--", "-")
    return (keep.strip("-") or "document")[:48]
