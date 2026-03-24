"""SQLite shared memory for PolyCity Stay runs."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from polycity_stay.config import DB_PATH


def _conn() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                school TEXT NOT NULL,
                prefs_json TEXT NOT NULL,
                retrieval_output TEXT,
                analysis_output TEXT,
                verification_output TEXT,
                final_output TEXT,
                error TEXT
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id INTEGER,
                created_at TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )


def insert_run(
    school: str,
    prefs: dict[str, Any],
    retrieval: str | None = None,
    analysis: str | None = None,
    verification: str | None = None,
    final: str | None = None,
    error: str | None = None,
) -> int:
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        cur = c.execute(
            """
            INSERT INTO runs (created_at, school, prefs_json, retrieval_output, analysis_output,
                verification_output, final_output, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                school,
                json.dumps(prefs, ensure_ascii=False),
                retrieval,
                analysis,
                verification,
                final,
                error,
            ),
        )
        return int(cur.lastrowid)


def log_line(run_id: int | None, level: str, message: str) -> None:
    init_db()
    now = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        c.execute(
            "INSERT INTO logs (run_id, created_at, level, message) VALUES (?, ?, ?, ?)",
            (run_id, now, level, message),
        )


def recent_runs(limit: int = 10) -> list[dict[str, Any]]:
    init_db()
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            "SELECT id, created_at, school, prefs_json, error FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
