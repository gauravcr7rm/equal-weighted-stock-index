from app.core.config import settings
from datetime import datetime, timedelta
from typing import Dict, Any

def get_data_source():
    """
    Get the appropriate data source based on configuration.
    
    Returns:
        module: Data source module
    """
    if settings.USE_YAHOO_FINANCE:
        from app.services.data_sources.yahoo_finance import get_top_stocks_data
        return get_top_stocks_data
    else:
        from app.services.data_sources.alpha_vantage import get_top_stocks_data
        return get_top_stocks_data

def fetch_stock_data(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Fetch stock data from the configured data source.
    
    Args:
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        
    Returns:
        Dict[str, Any]: Stock data including metadata and prices
    """
    data_source = get_data_source()
    return data_source(start_date, end_date)
