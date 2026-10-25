from pathlib import Path

from backend.rules.engine import parse_sow
from backend.services.analyze import run_analysis

SOW = (Path(__file__).resolve().parents[1] / "seeds" / "northstar_sow.txt").read_text()


def items():
    parsed = parse_sow(SOW)
    return [
        {
            "id": it.id,
            "kind": it.kind,
            "title": it.title,
            "body": it.body,
            "source_text": it.source_text,
            "section_label": it.section_label,
            "quantity_value": it.quantity_value,
            "quantity_unit": it.quantity_unit,
        }
        for it in parsed.items
    ]


def run(text):
    return run_analysis(text, items(), SOW, 165, 80)


def test_parse_extracts_exclusions_and_sku_cap():
    parsed = parse_sow(SOW)
    assert parsed.fee == 48000
    assert parsed.rate == 165
    kinds = {i.kind for i in parsed.items}
    assert "exclusion" in kinds
    assert "deliverable" in kinds
    sku = [i for i in parsed.items if i.quantity_unit and "sku" in i.quantity_unit]
    assert sku and sku[0].quantity_value == 400


def test_loyalty():
    r = run("Can you also add loyalty points?")
    assert r["classification"] == "OUT_OF_SCOPE"
    assert r["estimated_hours"] == 40
    assert r["client_price"] == 6600
    assert r["internal_cost"] == 3200
    assert r["evidence"]
    assert "loyalty" in r["evidence"][0]["quote"].lower() or "points" in r["evidence"][0]["quote"].lower()


def test_netsuite():
    r = run("Can you sync orders to NetSuite?")
    assert r["classification"] == "OUT_OF_SCOPE"
    assert r["estimated_hours"] == 64
    assert r["client_price"] == 10560
    assert r["evidence"]


def test_wholesale():
    r = run("Can you add wholesale login?")
    assert r["classification"] == "OUT_OF_SCOPE"
    assert r["estimated_hours"] == 80
    assert r["client_price"] == 13200


def test_sku_overrun():
    r = run("We originally agreed on 400 SKUs but now need 620.")
    assert r["classification"] == "QUANTITY_OVERRUN"
    assert r["client_price"] == 2970
    assert r["evidence"]


def test_safari_bug():
    r = run("The Add to Cart button doesn't work in Safari.")
    assert r["classification"] == "BUG_OR_DEFECT"
    assert r["client_price"] == 0


def test_invented_quote_rejected():
    from backend.ai.validate import quote_is_grounded

    assert not quote_is_grounded("Customer loyalty is excluded under §99.9", "Custom loyalty or points programs", "")
    assert quote_is_grounded("Custom loyalty or points programs", "Custom loyalty or points programs", "")
