from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class IndexComposition(BaseModel):
    """Index composition model for a single stock in the index."""
    date: date
    ticker: str
    weight: float
    rank: int

class IndexPerformance(BaseModel):
    """Index performance model for daily performance data."""
    date: date
    daily_return: float
    cumulative_return: float

class CompositionChange(BaseModel):
    """Model for tracking composition changes."""
    date: date
    added: List[str]
    removed: List[str]

class IndexBuildRequest(BaseModel):
    """Request model for building the index."""
    start_date: date
    end_date: Optional[date] = None

class ExportRequest(BaseModel):
    """Request model for exporting data."""
    start_date: date
    end_date: date
