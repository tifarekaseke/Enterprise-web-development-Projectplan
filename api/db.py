# api/db.py
from pathlib import Path
import sqlite3

def get_conn(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn