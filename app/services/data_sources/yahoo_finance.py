import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any

def get_sp500_tickers() -> List[str]:
    """
    Get the list of S&P 500 tickers as a proxy for top US stocks.
    
    Returns:
        List[str]: List of stock tickers
    """
    # Use yfinance to get S&P 500 components
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500['Symbol'].tolist()

def get_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Get stock data for a single ticker.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        
    Returns:
        Dict[str, Any]: Stock data including metadata and price history
    """
    try:
        # Get stock info
        stock = yf.Ticker(ticker)
        
        # Get stock metadata
        try:
            info = stock.info
            metadata = {
                'ticker': ticker,
                'name': info.get('shortName', ''),
                'sector': info.get('sector', ''),
                'exchange': info.get('exchange', '')
            }
        except Exception as e:
            print(f"Error getting metadata for {ticker}: {e}")
            metadata = {
                'ticker': ticker,
                'name': '',
                'sector': '',
                'exchange': ''
            }
        
        # Get historical data
        hist = stock.history(start=start_date, end=end_date + timedelta(days=1))
        
        if hist.empty:
            return {
                'metadata': metadata,
                'prices': []
            }
        
        # Reset index to make date a column
        hist = hist.reset_index()
        
        # Convert date to string format
        hist['Date'] = hist['Date'].dt.date
        
        # Calculate market cap
        hist['MarketCap'] = hist['Close'] * stock.info.get('sharesOutstanding', 0)
        
        # Format price data
        prices = []
        for _, row in hist.iterrows():
            prices.append({
                'date': row['Date'],
                'ticker': ticker,
                'open': float(row['Open']),
                'high': float(row['High']),
                'low': float(row['Low']),
                'close': float(row['Close']),
                'volume': int(row['Volume']),
                'market_cap': float(row['MarketCap'])
            })
        
        return {
            'metadata': metadata,
            'prices': prices
        }
    
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return {
            'metadata': {
                'ticker': ticker,
                'name': '',
                'sector': '',
                'exchange': ''
            },
            'prices': []
        }

def get_top_stocks_data(start_date: datetime, end_date: datetime, limit: int = 100) -> Dict[str, Any]:
    """
    Get data for top US stocks.
    
    Args:
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        limit (int): Number of stocks to fetch (default: 100 to ensure we have enough data)
        
    Returns:
        Dict[str, Any]: Stock data for all tickers
    """
    # Get S&P 500 tickers as a proxy for top US stocks
    tickers = get_sp500_tickers()
    
    # Limit the number of tickers to fetch
    tickers = tickers[:limit]
    
    all_data = {
        'metadata': [],
        'prices': []
    }
    
    # Fetch data for each ticker with rate limiting
    for i, ticker in enumerate(tickers):
        print(f"Fetching data for {ticker} ({i+1}/{len(tickers)})")
        
        stock_data = get_stock_data(ticker, start_date, end_date)
        
        all_data['metadata'].append(stock_data['metadata'])
        all_data['prices'].extend(stock_data['prices'])
        
        # Rate limiting to avoid API restrictions
        if i % 10 == 0 and i > 0:
            print("Pausing to avoid rate limits...")
            time.sleep(2)
    
    return all_data
