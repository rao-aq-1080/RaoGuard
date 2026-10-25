from backend.calc.commercial import money, snapshot


def test_forty_times_165():
    assert money(40, 165) == money("40", "165")
    assert float(money(40, 165)) == 6600.00


def test_human_edit_10_hours():
    s = snapshot(10, 165, 80)
    assert s["client_price"] == 1650.00
    assert s["internal_cost"] == 800.00
    assert s["gross_profit"] == 850.00


def test_sku_math_matches_northstar():
    from backend.rules.engine import hours_for_quantity

    assert hours_for_quantity("skus", 220) == 18
    assert float(money(18, 165)) == 2970.00
