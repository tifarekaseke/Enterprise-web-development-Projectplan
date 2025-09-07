# etl/load_db.py
from __future__ import annotations
from pathlib import Path
import sqlite3
import json

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS transactions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  date_iso     TEXT,                -- YYYY-MM-DD
  sender       TEXT,                -- e.g., MTN
  counterparty TEXT,                -- phone or merchant id if parsed
  text         TEXT,                -- original SMS text
  amount       REAL,                -- numeric amount
  category     TEXT                 -- CASHIN/CASHOUT/PAY/FEES/OTHER/OTHER
);

CREATE INDEX IF NOT EXISTS idx_tx_date ON transactions(date_iso);
CREATE INDEX IF NOT EXISTS idx_tx_cat  ON transactions(category);
"""

def get_conn(db_path: Path | str) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()

def insert_transactions(conn: sqlite3.Connection, rows: list[dict]) -> int:
    """
    Insert parsed+cleaned+categorized rows into the transactions table.
    For week 1/2 this is a simple INSERT. Later you can switch to UPSERT
    if you add a unique key (e.g., hash of date+text).
    """
    if not rows:
        return 0
    cur = conn.executemany(
        """
        INSERT INTO transactions (date_iso, sender, counterparty, text, amount, category)
        VALUES (:date_iso, :sender, :counterparty, :text, :amount, :category)
        """,
        rows
    )
    conn.commit()
    return cur.rowcount

def export_dashboard_json(db_path: Path | str, out_path: Path | str) -> None:
    """
    Build the aggregates your frontend reads and write to data/processed/dashboard.json
    """
    db_path = Path(db_path)
    out_path = Path(out_path)

    conn = get_conn(db_path)
    cur = conn.cursor()

    # KPIs
    cur.execute("SELECT COUNT(*), COALESCE(SUM(amount),0), COALESCE(AVG(amount),0) FROM transactions")
    total_count, total_volume, avg_amount = cur.fetchone()

    # By category
    cur.execute("SELECT category, COALESCE(SUM(amount),0) FROM transactions GROUP BY category")
    by_cat = {row[0]: row[1] for row in cur.fetchall()}

    # Daily trend
    cur.execute("""
        SELECT date_iso, COALESCE(SUM(amount),0) AS vol
        FROM transactions
        WHERE date_iso IS NOT NULL
        GROUP BY date_iso
        ORDER BY date_iso
    """)
    daily = [{"date": r[0], "volume": r[1]} for r in cur.fetchall()]

    # Recent
    cur.execute("""
        SELECT date_iso, category, counterparty, amount
        FROM transactions
        ORDER BY id DESC
        LIMIT 50
    """)
    recent = [
        {"date": r[0], "category": r[1], "counterparty": r[2], "amount": r[3]}
        for r in cur.fetchall()
    ]

    out = {
        "kpis": {
            "total_count": int(total_count or 0),
            "total_volume": float(total_volume or 0.0),
            "avg_amount": float(avg_amount or 0.0),
        },
        "by_category": by_cat,
        "daily": daily,
        "recent": recent,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")