from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.index import (
    IndexBuildRequest,
    IndexComposition,
    IndexPerformance,
    CompositionChange
)
from app.services.index_construction import construct_equal_weighted_index
from app.services.data_storage import (
    get_index_composition,
    get_index_performance,
    get_composition_changes
)
from app.db.redis_cache import set_cache, get_cache

router = APIRouter()

@router.post("/build-index", status_code=201)
async def build_index(request: IndexBuildRequest):
    """
    Build the equal-weighted index for the given date range.

    Args:
        request (IndexBuildRequest): Request with start_date and optional end_date

    Returns:
        dict: Result of the index construction
    """
    # If end_date is not provided, use start_date
    end_date = request.end_date if request.end_date else request.start_date

    # Construct the index
    result = construct_equal_weighted_index(request.start_date, end_date)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['message'])

    # Clear cache for the affected date range
    cache_keys = [
        f"index_performance:{request.start_date}:{end_date}",
        f"composition_changes:{request.start_date}:{end_date}"
    ]

    # Also clear cache for each date in the range
    start_dt = datetime.combine(request.start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.min.time())
    current_dt = start_dt

    while current_dt <= end_dt:
        current_date = current_dt.date()
        cache_keys.append(f"index_composition:{current_date}")
        current_dt += timedelta(days=1)

    return result

@router.get("/index-performance")
async def get_performance(
    start_date: date = Query(..., description="Start date for performance data"),
    end_date: date = Query(..., description="End date for performance data")
):
    """
    Get index performance for the given date range.

    Args:
        start_date (date): Start date
        end_date (date): End date

    Returns:
        List[IndexPerformance]: List of daily performance data
    """
    # Check cache
    cache_key = f"index_performance:{start_date}:{end_date}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    # Get performance data from database
    performance_data = get_index_performance(start_date.isoformat(), end_date.isoformat())

    if not performance_data:
        raise HTTPException(status_code=404, detail="No performance data found for the given date range")

    # Cache the result
    set_cache(cache_key, performance_data)

    return performance_data

@router.get("/index-composition")
async def get_composition(date: date = Query(..., description="Date for composition data")):
    """
    Get index composition for the given date.

    Args:
        date (date): Date for composition data

    Returns:
        List[IndexComposition]: List of stocks in the index
    """
    # Check cache
    cache_key = f"index_composition:{date}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    # Get composition data from database
    composition_data = get_index_composition(date.isoformat())

    if not composition_data:
        raise HTTPException(status_code=404, detail=f"No composition data found for {date}")

    # Cache the result
    set_cache(cache_key, composition_data)

    return composition_data

@router.get("/composition-changes")
async def get_changes(
    start_date: date = Query(..., description="Start date for changes data"),
    end_date: date = Query(..., description="End date for changes data")
):
    """
    Get composition changes for the given date range.

    Args:
        start_date (date): Start date
        end_date (date): End date

    Returns:
        List[CompositionChange]: List of composition changes
    """
    # Check cache
    cache_key = f"composition_changes:{start_date}:{end_date}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    # Get changes data from database
    changes_data = get_composition_changes(start_date.isoformat(), end_date.isoformat())

    # Cache the result (even if empty)
    set_cache(cache_key, changes_data)

    return changes_data
