from pydantic import BaseModel
from typing import Optional
from datetime import date

class Stock(BaseModel):
    """Stock model for stock metadata."""
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    exchange: Optional[str] = None

class StockPrice(BaseModel):
    """Stock price model for daily price data."""
    date: date
    ticker: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    market_cap: float
