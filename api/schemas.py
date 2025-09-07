# api/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict, List

class Transaction(BaseModel):
    date_iso: Optional[str]
    sender: Optional[str]
    counterparty: Optional[str]
    text: Optional[str]
    amount: float
    category: str

class KPIs(BaseModel):
    total_count: int
    total_volume: float
    avg_amount: float

class DailyPoint(BaseModel):
    date: str
    volume: float

class Dashboard(BaseModel):
    kpis: KPIs
    by_category: Dict[str, float]
    daily: List[DailyPoint]
    recent: list