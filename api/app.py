# api/app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

from etl.load_db import export_dashboard_json
from etl.load_db import get_conn
from etl.load_db import init_db  # if you want to ensure schema on boot
from etl.load_db import export_dashboard_json
from etl.load_db import get_conn
from etl.load_db import init_db
from etl.load_db import export_dashboard_json
from etl.load_db import get_conn
from etl.load_db import init_db

from etl.load_db import get_conn
from etl.load_db import init_db
from etl.load_db import export_dashboard_json

from api.db import get_conn as api_get_conn
from api.schemas import Dashboard
from etl.load_db import get_conn as etl_get_conn  # alias if needed
from etl.load_db import init_db as etl_init_db

# paths you already use elsewhere
DB_PATH = Path("data/db.sqlite3")
PROCESSED_JSON = Path("data/processed/dashboard.json")

app = FastAPI(title="MoMo XML Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# optional: ensure DB schema exists when API starts
@app.on_event("startup")
def startup():
    conn = etl_get_conn(DB_PATH)
    etl_init_db(conn)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/transactions")
def transactions(limit: int = 50):
    conn = api_get_conn(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT date_iso, sender, counterparty, text, amount, category
        FROM transactions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    cols = ["date_iso", "sender", "counterparty", "text", "amount", "category"]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

@app.get("/analytics", response_model=Dashboard)
def analytics():
    # Serve the same JSON the frontend reads from disk
    data = json.loads(PROCESSED_JSON.read_text(encoding="utf-8"))
    return data