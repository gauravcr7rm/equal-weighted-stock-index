from app.db.database import get_db_connection
from typing import List, Dict, Any
from datetime import date

def store_stock_metadata(metadata_list: List[Dict[str, Any]]):
    """
    Store stock metadata in the database.
    
    Args:
        metadata_list (List[Dict[str, Any]]): List of stock metadata
    """
    conn = get_db_connection()
    
    # Prepare data for insertion
    data = []
    for metadata in metadata_list:
        data.append((
            metadata['ticker'],
            metadata['name'],
            metadata['sector'],
            metadata['exchange']
        ))
    
    # Insert data with UPSERT logic
    conn.executemany("""
    INSERT OR REPLACE INTO stocks (ticker, name, sector, exchange)
    VALUES (?, ?, ?, ?)
    """, data)
    
    conn.close()

def store_stock_prices(prices_list: List[Dict[str, Any]]):
    """
    Store stock prices in the database.
    
    Args:
        prices_list (List[Dict[str, Any]]): List of stock prices
    """
    conn = get_db_connection()
    
    # Prepare data for insertion
    data = []
    for price in prices_list:
        data.append((
            price['date'],
            price['ticker'],
            price['open'],
            price['high'],
            price['low'],
            price['close'],
            price['volume'],
            price['market_cap']
        ))
    
    # Insert data with UPSERT logic
    conn.executemany("""
    INSERT OR REPLACE INTO stock_prices (date, ticker, open, high, low, close, volume, market_cap)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    
    conn.close()

def store_index_composition(compositions: List[Dict[str, Any]]):
    """
    Store index compositions in the database.
    
    Args:
        compositions (List[Dict[str, Any]]): List of index compositions
    """
    conn = get_db_connection()
    
    # Prepare data for insertion
    data = []
    for comp in compositions:
        data.append((
            comp['date'],
            comp['ticker'],
            comp['weight'],
            comp['rank']
        ))
    
    # Insert data with UPSERT logic
    conn.executemany("""
    INSERT OR REPLACE INTO index_compositions (date, ticker, weight, rank)
    VALUES (?, ?, ?, ?)
    """, data)
    
    conn.close()

def store_index_performance(performances: List[Dict[str, Any]]):
    """
    Store index performance in the database.
    
    Args:
        performances (List[Dict[str, Any]]): List of index performances
    """
    conn = get_db_connection()
    
    # Prepare data for insertion
    data = []
    for perf in performances:
        data.append((
            perf['date'],
            perf['daily_return'],
            perf['cumulative_return']
        ))
    
    # Insert data with UPSERT logic
    conn.executemany("""
    INSERT OR REPLACE INTO index_performance (date, daily_return, cumulative_return)
    VALUES (?, ?, ?)
    """, data)
    
    conn.close()

def get_top_stocks_by_market_cap(date_str: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get top stocks by market cap for a specific date.
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        limit (int): Number of stocks to return (default: 100)
        
    Returns:
        List[Dict[str, Any]]: List of top stocks with market cap
    """
    conn = get_db_connection()
    
    # Query to get top stocks by market cap
    result = conn.execute("""
    SELECT sp.ticker, sp.market_cap, s.name, s.sector, s.exchange
    FROM stock_prices sp
    JOIN stocks s ON sp.ticker = s.ticker
    WHERE sp.date = ?
    ORDER BY sp.market_cap DESC
    LIMIT ?
    """, (date_str, limit)).fetchall()
    
    conn.close()
    
    # Format the result
    stocks = []
    for row in result:
        stocks.append({
            'ticker': row[0],
            'market_cap': row[1],
            'name': row[2],
            'sector': row[3],
            'exchange': row[4]
        })
    
    return stocks

def get_stock_prices_for_date(date_str: str, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get stock prices for a specific date and list of tickers.
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        tickers (List[str]): List of stock tickers
        
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of stock prices by ticker
    """
    conn = get_db_connection()
    
    # Create placeholders for the SQL query
    placeholders = ', '.join(['?'] * len(tickers))
    
    # Query to get stock prices
    result = conn.execute(f"""
    SELECT ticker, close, market_cap
    FROM stock_prices
    WHERE date = ? AND ticker IN ({placeholders})
    """, (date_str, *tickers)).fetchall()
    
    conn.close()
    
    # Format the result
    prices = {}
    for row in result:
        prices[row[0]] = {
            'close': row[1],
            'market_cap': row[2]
        }
    
    return prices

def get_trading_dates(start_date: str, end_date: str) -> List[str]:
    """
    Get all trading dates in the database between start_date and end_date.
    
    Args:
        start_date (str): Start date string in YYYY-MM-DD format
        end_date (str): End date string in YYYY-MM-DD format
        
    Returns:
        List[str]: List of trading dates
    """
    conn = get_db_connection()
    
    # Query to get distinct dates
    result = conn.execute("""
    SELECT DISTINCT date
    FROM stock_prices
    WHERE date BETWEEN ? AND ?
    ORDER BY date
    """, (start_date, end_date)).fetchall()
    
    conn.close()
    
    # Format the result
    dates = [row[0] for row in result]
    
    return dates

def get_index_composition(date_str: str) -> List[Dict[str, Any]]:
    """
    Get index composition for a specific date.
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of stocks in the index
    """
    conn = get_db_connection()
    
    # Query to get index composition
    result = conn.execute("""
    SELECT ic.ticker, ic.weight, ic.rank, s.name, s.sector, s.exchange
    FROM index_compositions ic
    JOIN stocks s ON ic.ticker = s.ticker
    WHERE ic.date = ?
    ORDER BY ic.rank
    """, (date_str,)).fetchall()
    
    conn.close()
    
    # Format the result
    composition = []
    for row in result:
        composition.append({
            'ticker': row[0],
            'weight': row[1],
            'rank': row[2],
            'name': row[3],
            'sector': row[4],
            'exchange': row[5]
        })
    
    return composition

def get_index_performance(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get index performance between start_date and end_date.
    
    Args:
        start_date (str): Start date string in YYYY-MM-DD format
        end_date (str): End date string in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of daily performance data
    """
    conn = get_db_connection()
    
    # Query to get index performance
    result = conn.execute("""
    SELECT date, daily_return, cumulative_return
    FROM index_performance
    WHERE date BETWEEN ? AND ?
    ORDER BY date
    """, (start_date, end_date)).fetchall()
    
    conn.close()
    
    # Format the result
    performance = []
    for row in result:
        performance.append({
            'date': row[0],
            'daily_return': row[1],
            'cumulative_return': row[2]
        })
    
    return performance

def get_composition_changes(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Get composition changes between start_date and end_date.
    
    Args:
        start_date (str): Start date string in YYYY-MM-DD format
        end_date (str): End date string in YYYY-MM-DD format
        
    Returns:
        List[Dict[str, Any]]: List of composition changes
    """
    conn = get_db_connection()
    
    # Get all dates in the range
    dates = get_trading_dates(start_date, end_date)
    
    if len(dates) <= 1:
        return []
    
    changes = []
    
    # Compare each date with the previous date
    for i in range(1, len(dates)):
        prev_date = dates[i-1]
        curr_date = dates[i]
        
        # Get compositions for both dates
        prev_comp = conn.execute("""
        SELECT ticker
        FROM index_compositions
        WHERE date = ?
        """, (prev_date,)).fetchall()
        
        curr_comp = conn.execute("""
        SELECT ticker
        FROM index_compositions
        WHERE date = ?
        """, (curr_date,)).fetchall()
        
        # Convert to sets for easy comparison
        prev_tickers = set([row[0] for row in prev_comp])
        curr_tickers = set([row[0] for row in curr_comp])
        
        # Find added and removed tickers
        added = curr_tickers - prev_tickers
        removed = prev_tickers - curr_tickers
        
        # If there are changes, add to the result
        if added or removed:
            changes.append({
                'date': curr_date,
                'added': list(added),
                'removed': list(removed)
            })
    
    conn.close()
    
    return changes
