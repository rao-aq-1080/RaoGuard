from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "raoguard.db"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init() -> None:
    conn = connect()
    conn.executescript(
        """
        create table if not exists settings (
          id integer primary key check (id = 1),
          agency_name text not null default 'Harbor & Co.',
          owner_name text not null default 'Muhammad Abdullah',
          currency text not null default 'USD',
          client_rate real not null default 165,
          internal_rate real not null default 80,
          tone text not null default 'professional',
          groq_enabled integer not null default 0,
          plan text not null default 'free',
          plan_started_at text
        );
        insert or ignore into settings (id) values (1);

        create table if not exists projects (
          id text primary key,
          name text not null,
          client_name text not null,
          contract_value real,
          currency text not null default 'USD',
          timeline_weeks real,
          client_rate real,
          internal_rate real,
          sow_text text not null default '',
          status text not null default 'active',
          created_at text not null
        );

        create table if not exists scope_items (
          id text primary key,
          project_id text not null references projects(id) on delete cascade,
          kind text not null,
          title text not null,
          body text not null,
          source_text text not null,
          section_label text,
          quantity_value real,
          quantity_unit text,
          created_at text not null
        );

        create table if not exists requests (
          id text primary key,
          project_id text not null references projects(id) on delete cascade,
          source text not null default 'paste',
          body text not null,
          created_at text not null
        );

        create table if not exists analyses (
          id text primary key,
          request_id text not null references requests(id) on delete cascade,
          project_id text not null,
          payload text not null,
          status text not null default 'new',
          created_at text not null
        );

        create table if not exists decisions (
          id text primary key,
          analysis_id text not null references analyses(id) on delete cascade,
          action text not null,
          note text,
          created_at text not null
        );

        create table if not exists change_orders (
          id text primary key,
          project_id text not null,
          analysis_id text not null,
          title text not null,
          body_html text not null,
          hours real not null,
          price real not null,
          status text not null default 'draft',
          created_at text not null
        );

        create table if not exists audit_events (
          id text primary key,
          project_id text,
          event_type text not null,
          payload text not null default '{}',
          created_at text not null
        );

        create table if not exists users (
          id text primary key,
          email text not null unique,
          name text not null,
          password_hash text not null,
          role text not null default 'owner',
          terms_version text,
          terms_accepted_at text,
          password_changed integer not null default 0,
          created_at text not null
        );

        create table if not exists sessions (
          id text primary key,
          token text not null unique,
          user_id text not null references users(id) on delete cascade,
          expires_at text not null,
          created_at text not null
        );
        """
    )
    cols = {r[1] for r in conn.execute("pragma table_info(settings)")}
    if "plan" not in cols:
        conn.execute("alter table settings add column plan text not null default 'free'")
    if "plan_started_at" not in cols:
        conn.execute("alter table settings add column plan_started_at text")
    conn.execute("update settings set plan='free' where id=1 and (plan is null or plan='')")
    conn.execute(
        "update settings set plan_started_at=? where id=1 and plan_started_at is null",
        (now(),),
    )
    conn.commit()
    conn.close()


def uid(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    return dict(row)


def audit(conn: sqlite3.Connection, event_type: str, project_id: str | None = None, payload: dict | None = None):
    conn.execute(
        "insert into audit_events (id, project_id, event_type, payload, created_at) values (?,?,?,?,?)",
        (uid("aud"), project_id, event_type, json.dumps(payload or {}), now()),
    )
