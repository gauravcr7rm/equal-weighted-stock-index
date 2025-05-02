from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
from app.core.config import settings

def get_top_us_tickers() -> List[str]:
    """
    Get a list of top US stock tickers.
    
    Returns:
        List[str]: List of stock tickers
    """
    # Since Alpha Vantage doesn't provide a direct way to get top stocks by market cap,
    # we'll use a predefined list of major US stocks
    # In a production environment, this would be replaced with a more comprehensive solution
    
    # Use S&P 500 components as a proxy
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500['Symbol'].tolist()

def get_stock_data(ticker: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """
    Get stock data for a single ticker using Alpha Vantage.
    
    Args:
        ticker (str): Stock ticker symbol
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        
    Returns:
        Dict[str, Any]: Stock data including metadata and price history
    """
    try:
        # Initialize Alpha Vantage clients
        ts = TimeSeries(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')
        fd = FundamentalData(key=settings.ALPHA_VANTAGE_API_KEY, output_format='pandas')
        
        # Get stock metadata
        try:
            overview_data, _ = fd.get_company_overview(ticker)
            metadata = {
                'ticker': ticker,
                'name': overview_data.get('Name', [''])[0],
                'sector': overview_data.get('Sector', [''])[0],
                'exchange': overview_data.get('Exchange', [''])[0]
            }
            shares_outstanding = float(overview_data.get('SharesOutstanding', [0])[0])
        except Exception as e:
            print(f"Error getting metadata for {ticker}: {e}")
            metadata = {
                'ticker': ticker,
                'name': '',
                'sector': '',
                'exchange': ''
            }
            shares_outstanding = 0
        
        # Get historical data
        data, _ = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
        
        # Filter data for the date range
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        filtered_data = data.loc[start_str:end_str]
        
        if filtered_data.empty:
            return {
                'metadata': metadata,
                'prices': []
            }
        
        # Reset index to make date a column
        filtered_data = filtered_data.reset_index()
        
        # Calculate market cap
        filtered_data['market_cap'] = filtered_data['4. close'] * shares_outstanding
        
        # Format price data
        prices = []
        for _, row in filtered_data.iterrows():
            date_obj = row['date'].to_pydatetime().date()
            prices.append({
                'date': date_obj,
                'ticker': ticker,
                'open': float(row['1. open']),
                'high': float(row['2. high']),
                'low': float(row['3. low']),
                'close': float(row['4. close']),
                'volume': int(row['6. volume']),
                'market_cap': float(row['market_cap'])
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

def get_top_stocks_data(start_date: datetime, end_date: datetime, limit: int = 150) -> Dict[str, Any]:
    """
    Get data for top US stocks using Alpha Vantage.
    
    Args:
        start_date (datetime): Start date for data
        end_date (datetime): End date for data
        limit (int): Number of stocks to fetch (default: 150 to ensure we have enough data)
        
    Returns:
        Dict[str, Any]: Stock data for all tickers
    """
    # Get top US tickers
    tickers = get_top_us_tickers()
    
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
        
        # Rate limiting to avoid API restrictions (Alpha Vantage has a limit of 5 calls per minute for free tier)
        if i % 5 == 0 and i > 0:
            print("Pausing to avoid rate limits...")
            time.sleep(60)  # Wait for 60 seconds after every 5 calls
    
    return all_data
