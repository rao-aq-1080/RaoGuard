"""Plan catalog and local limits. No payment is collected in this copy."""
from __future__ import annotations

from datetime import datetime, timezone

from backend.db import connect

PLANS: dict[str, dict] = {
    "free": {
        "id": "free",
        "name": "Free",
        "price": 0,
        "price_label": "$0",
        "period": "",
        "badge": "Trial",
        "blurb": "Use the real workflow on one live SOW. Limits included — this is the trial.",
        "max_active_projects": 1,
        "max_analyses_total": 20,
        "max_analyses_month": None,
        "max_seats": 1,
        "white_label": False,
        "features": [
            "1 live project",
            "20 SOW checks on this machine",
            "Full loop: fence → check → draft CO → you decide",
            "Public analyzer stays unlimited",
        ],
    },
    "starter": {
        "id": "starter",
        "name": "Starter",
        "price": 29,
        "price_label": "$29",
        "period": "/mo",
        "badge": "",
        "blurb": "Solo PM / 2–6 people.",
        "max_active_projects": 3,
        "max_analyses_total": None,
        "max_analyses_month": 100,
        "max_seats": 3,
        "white_label": False,
        "features": [
            "3 live projects",
            "100 SOW checks / month",
            "3 seats",
            "Change-order PDF",
        ],
    },
    "studio": {
        "id": "studio",
        "name": "Studio",
        "price": 59,
        "price_label": "$59",
        "period": "/mo",
        "badge": "Most agencies",
        "blurb": "The one agencies actually buy.",
        "max_active_projects": None,
        "max_analyses_total": None,
        "max_analyses_month": None,
        "max_seats": None,
        "white_label": False,
        "features": [
            "Unlimited projects",
            "Unlimited SOW checks",
            "Team workspace",
            "Recovered-margin dashboard",
        ],
        "featured": True,
    },
    "agency": {
        "id": "agency",
        "name": "Agency",
        "price": 89,
        "price_label": "$89",
        "period": "/mo",
        "badge": "",
        "blurb": "Delivery lead + AM.",
        "max_active_projects": None,
        "max_analyses_total": None,
        "max_analyses_month": None,
        "max_seats": None,
        "white_label": True,
        "features": [
            "Everything in Studio",
            "White-label change orders",
            "Precedent memory",
            "Founder onboarding call",
        ],
    },
}

ORDER = ("free", "starter", "studio", "agency")


def get_plan(plan_id: str | None) -> dict:
    return PLANS.get(plan_id or "free") or PLANS["free"]


def catalog() -> list[dict]:
    return [PLANS[k] for k in ORDER]


def _month_start() -> str:
    return datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()


def usage_snapshot() -> dict:
    conn = connect()
    active = conn.execute("select count(*) as c from projects where status='active'").fetchone()["c"]
    total = conn.execute("select count(*) as c from analyses").fetchone()["c"]
    month = conn.execute(
        "select count(*) as c from analyses where created_at >= ?",
        (_month_start(),),
    ).fetchone()["c"]
    seats = conn.execute("select count(*) as c from users").fetchone()["c"]
    conn.close()
    return {
        "active_projects": int(active),
        "analyses_total": int(total),
        "analyses_month": int(month),
        "seats": int(seats),
    }


def remaining(plan: dict, usage: dict) -> dict:
    def left(cap, used):
        if cap is None:
            return None
        return max(0, int(cap) - int(used))

    return {
        "projects": left(plan.get("max_active_projects"), usage["active_projects"]),
        "checks_total": left(plan.get("max_analyses_total"), usage["analyses_total"]),
        "checks_month": left(plan.get("max_analyses_month"), usage["analyses_month"]),
        "seats": left(plan.get("max_seats"), usage["seats"]),
    }


def public_status(plan_id: str | None) -> dict:
    plan = get_plan(plan_id)
    usage = usage_snapshot()
    return {
        "plan": plan,
        "usage": usage,
        "remaining": remaining(plan, usage),
        "plans": catalog(),
        "billing": "No payment is collected in this local copy. Choosing a paid plan here only lifts the caps so you can evaluate them. A real invoice would be by hand.",
    }


def limit_message(action: str, plan: dict, usage: dict) -> str | None:
    """Return a human error if the action is over cap, else None."""
    name = plan["name"]
    if action == "project":
        cap = plan.get("max_active_projects")
        if cap is not None and usage["active_projects"] >= cap:
            if plan["id"] == "free":
                return (
                    "Free trial includes 1 live project. Close it, or move to Starter ($29/mo) "
                    "for 3 projects. Studio ($59) is unlimited."
                )
            return f"{name} includes {cap} live project(s). Close one or move up a plan."
    if action == "analyze":
        cap_t = plan.get("max_analyses_total")
        if cap_t is not None and usage["analyses_total"] >= cap_t:
            return (
                f"Free trial includes {cap_t} SOW checks on this machine "
                f"({usage['analyses_total']} used). The public analyzer stays unlimited. "
                "Starter ($29/mo) includes 100 checks a month."
            )
        cap_m = plan.get("max_analyses_month")
        if cap_m is not None and usage["analyses_month"] >= cap_m:
            return (
                f"{name} includes {cap_m} SOW checks this month "
                f"({usage['analyses_month']} used). Studio ($59) is unlimited."
            )
    if action == "seat":
        cap = plan.get("max_seats")
        if cap is not None and usage["seats"] >= cap:
            if plan["id"] == "free":
                return "Free trial is one seat. Starter ($29/mo) includes 3 seats."
            return f"{name} includes {cap} seat(s). Move up a plan to add people."
    return None
