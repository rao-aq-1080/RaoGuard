"""Local owner auth. Stdlib password hashing. No paid IdP."""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

from backend.db import connect, now, uid

TERMS_VERSION = "2026-09-20"
DEFAULT_EMAIL = "founder@raoguard.local"
DEFAULT_PASSWORD = "RaoGuard2026"
DEFAULT_NAME = "Muhammad Abdullah"
SESSION_DAYS = 30
PBKDF2_ROUNDS = 200_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ROUNDS)
    return f"{salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), PBKDF2_ROUNDS
    )
    return hmac.compare_digest(dk.hex(), dk_hex)


def seed_owner() -> None:
    conn = connect()
    n = conn.execute("select count(*) as c from users").fetchone()["c"]
    if n:
        conn.close()
        return
    conn.execute(
        """insert into users
           (id, email, name, password_hash, role, terms_version, terms_accepted_at,
            password_changed, created_at)
           values (?,?,?,?,?,?,?,?,?)""",
        (
            uid("usr"),
            DEFAULT_EMAIL,
            DEFAULT_NAME,
            hash_password(DEFAULT_PASSWORD),
            "owner",
            None,
            None,
            0,
            now(),
        ),
    )
    conn.commit()
    conn.close()


def public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"],
        "role": row["role"],
        "terms_version": row["terms_version"],
        "terms_accepted": bool(row["terms_accepted_at"]) and row["terms_version"] == TERMS_VERSION,
        "terms_accepted_at": row["terms_accepted_at"],
        "password_changed": bool(row["password_changed"]),
    }


def user_by_email(email: str) -> dict | None:
    conn = connect()
    row = conn.execute(
        "select * from users where lower(email)=?", ((email or "").strip().lower(),)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def user_from_token(token: str | None) -> dict | None:
    if not token:
        return None
    conn = connect()
    row = conn.execute(
        """select u.*, s.expires_at as session_expires
           from sessions s join users u on u.id = s.user_id
           where s.token=?""",
        (token,),
    ).fetchone()
    if not row:
        conn.close()
        return None
    d = dict(row)
    if d["session_expires"] < datetime.now(timezone.utc).isoformat():
        conn.execute("delete from sessions where token=?", (token,))
        conn.commit()
        conn.close()
        return None
    conn.close()
    return d


def create_session(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires = (datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)).isoformat()
    conn = connect()
    conn.execute(
        "insert into sessions (id, token, user_id, expires_at, created_at) values (?,?,?,?,?)",
        (uid("ses"), token, user_id, expires, now()),
    )
    conn.commit()
    conn.close()
    return token


def drop_session(token: str | None) -> None:
    if not token:
        return
    conn = connect()
    conn.execute("delete from sessions where token=?", (token,))
    conn.commit()
    conn.close()


def accept_terms(user_id: str) -> None:
    conn = connect()
    conn.execute(
        "update users set terms_version=?, terms_accepted_at=? where id=?",
        (TERMS_VERSION, now(), user_id),
    )
    conn.commit()
    conn.close()


def set_password(user_id: str, password: str) -> None:
    conn = connect()
    conn.execute(
        "update users set password_hash=?, password_changed=1 where id=?",
        (hash_password(password), user_id),
    )
    conn.commit()
    conn.close()


def create_user(email: str, name: str, password: str) -> dict:
    conn = connect()
    uid_ = uid("usr")
    conn.execute(
        """insert into users
           (id, email, name, password_hash, role, terms_version, terms_accepted_at,
            password_changed, created_at)
           values (?,?,?,?,?,?,?,?,?)""",
        (
            uid_,
            email.strip().lower(),
            name.strip() or email.split("@")[0],
            hash_password(password),
            "member",
            TERMS_VERSION,
            now(),
            1,
            now(),
        ),
    )
    conn.commit()
    row = dict(conn.execute("select * from users where id=?", (uid_,)).fetchone())
    conn.close()
    return row
