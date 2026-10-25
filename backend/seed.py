from __future__ import annotations

from pathlib import Path

from backend.db import connect, init, now, uid, audit
from backend.rules.engine import parse_sow
from backend.services.analyze import run_analysis

SEED = Path(__file__).resolve().parents[1] / "seeds" / "northstar_sow.txt"

DEMO_REQUESTS = [
    ("slack", "Can you also add a customer loyalty points program? Shouldn't take long, just stamps like the old Magento store."),
    ("email", "Finance wants this synced to NetSuite for inventory. Our ops lead said that was implied in the migration."),
    ("paste", "Please add a wholesale login so retailers can see net pricing."),
    ("jira", "Can we migrate 620 SKUs instead of 400? Catalog grew over summer."),
    ("jira", "The Add to Cart button doesn't work in Safari on iPhone 12. Ticket NS-184."),
]


def seed_if_empty() -> None:
    init()
    conn = connect()
    n = conn.execute("select count(*) as c from projects").fetchone()["c"]
    if n:
        conn.close()
        return

    sow = SEED.read_text(encoding="utf-8")
    parsed = parse_sow(sow)
    pid = "prj_northstar"
    conn.execute(
        """insert into projects
           (id, name, client_name, contract_value, currency, timeline_weeks,
            client_rate, internal_rate, sow_text, status, created_at)
           values (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            pid,
            parsed.title,
            parsed.client,
            parsed.fee or 48000,
            "USD",
            parsed.weeks or 10,
            parsed.rate or 165,
            parsed.internal_rate or 80,
            sow,
            "active",
            now(),
        ),
    )
    for it in parsed.items:
        conn.execute(
            """insert into scope_items
               (id, project_id, kind, title, body, source_text, section_label,
                quantity_value, quantity_unit, created_at)
               values (?,?,?,?,?,?,?,?,?,?)""",
            (
                it.id if it.id.startswith("si_") else uid("si"),
                pid,
                it.kind,
                it.title,
                it.body,
                it.source_text,
                it.section_label,
                it.quantity_value,
                it.quantity_unit,
                now(),
            ),
        )

    item_rows = [dict(r) for r in conn.execute("select * from scope_items where project_id=?", (pid,))]
    for i, (source, body) in enumerate(DEMO_REQUESTS):
        rid = uid("req")
        conn.execute(
            "insert into requests (id, project_id, source, body, created_at) values (?,?,?,?,?)",
            (rid, pid, source, body, now()),
        )
        result = run_analysis(body, item_rows, sow, 165, 80, "professional")
        aid = uid("an")
        status = "approved" if i == 0 and result["classification"] == "OUT_OF_SCOPE" else "new"
        conn.execute(
            "insert into analyses (id, request_id, project_id, payload, status, created_at) values (?,?,?,?,?,?)",
            (aid, rid, pid, __import__("json").dumps(result), status, now()),
        )
        if status == "approved":
            conn.execute(
                "insert into decisions (id, analysis_id, action, note, created_at) values (?,?,?,?,?)",
                (uid("dec"), aid, "approve", "Seeded recovered change order", now()),
            )

    audit(conn, "seeded", pid, {"project": "northstar"})
    conn.commit()
    conn.close()
