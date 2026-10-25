from decimal import Decimal, ROUND_HALF_UP
from typing import Any

TWOPLACES = Decimal("0.01")


def D(x: Any) -> Decimal:
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x or 0))


def money(hours: Any, rate: Any) -> Decimal:
    return (D(hours) * D(rate)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def snapshot(
    hours: Any,
    client_rate: Any,
    internal_rate: Any,
    timeline_days: Any = 0,
) -> dict:
    h = D(hours)
    cr = D(client_rate)
    ir = D(internal_rate)
    client_price = money(h, cr)
    internal_cost = money(h, ir)
    return {
        "estimated_hours": float(h),
        "client_rate": float(cr),
        "internal_rate": float(ir),
        "client_price": float(client_price),
        "internal_cost": float(internal_cost),
        "gross_profit": float(client_price - internal_cost),
        "timeline_impact_days": float(D(timeline_days or 0)),
        "is_estimate": True,
    }


def format_money(n: Any, currency: str = "USD") -> str:
    amount = float(D(n))
    symbols = {"USD": "$", "GBP": "£", "EUR": "€", "PKR": "Rs ", "AED": "AED "}
    sym = symbols.get(currency, currency + " ")
    if amount >= 0:
        return f"{sym}{amount:,.0f}"
    return f"-{sym}{abs(amount):,.0f}"
