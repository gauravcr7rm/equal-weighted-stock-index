import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date

from app.services.data_storage import (
    get_top_stocks_by_market_cap,
    get_stock_prices_for_date,
    get_trading_dates,
    store_index_composition,
    store_index_performance
)

# Configure logging
logger = logging.getLogger("index_construction")

def construct_equal_weighted_index(start_date: date, end_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Construct an equal-weighted index for the given date range.

    Args:
        start_date (date): Start date for the index
        end_date (date, optional): End date for the index. Defaults to start_date if None.

    Returns:
        Dict[str, Any]: Index construction results with the following keys:
            - success (bool): Whether the construction was successful
            - message (str): A message describing the result
            - trading_days (int, optional): Number of trading days processed
            - start_date (str): Start date in ISO format
            - end_date (str): End date in ISO format
    """
    try:
        # If end_date is not provided, use start_date
        if end_date is None:
            end_date = start_date

        # Convert dates to strings
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()

        logger.info(f"Constructing equal-weighted index for period {start_str} to {end_str}")

        # Get all trading dates in the range
        trading_dates = get_trading_dates(start_str, end_str)

        if not trading_dates:
            logger.warning(f"No trading data available for the period {start_str} to {end_str}")
            return {
                'success': False,
                'message': f"No trading data available for the period {start_str} to {end_str}"
            }

        logger.info(f"Found {len(trading_dates)} trading days in the specified period")

        # Process each trading date and build the index
        compositions, performances = _build_index_for_dates(trading_dates)

        if not compositions or not performances:
            logger.warning("Failed to build index: no compositions or performances generated")
            return {
                'success': False,
                'message': "Failed to build index: insufficient data"
            }

        # Store results in the database
        logger.info(f"Storing {len(compositions)} composition records")
        store_index_composition(compositions)

        logger.info(f"Storing {len(performances)} performance records")
        store_index_performance(performances)

        logger.info(f"Index construction completed successfully for {len(trading_dates)} trading days")
        return {
            'success': True,
            'message': f"Index constructed successfully for {len(trading_dates)} trading days",
            'trading_days': len(trading_dates),
            'start_date': start_str,
            'end_date': end_str
        }

    except Exception as e:
        logger.exception(f"Error constructing index: {e}")
        return {
            'success': False,
            'message': f"Error constructing index: {str(e)}"
        }

def _build_index_for_dates(trading_dates: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Build the equal-weighted index for the given trading dates.

    Args:
        trading_dates (List[str]): List of trading dates in ISO format

    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: Tuple containing:
            - List of index compositions
            - List of index performances
    """
    # Initialize results
    compositions = []
    performances = []
    cumulative_return = 0.0
    previous_portfolio = None

    # Process each trading date
    for date_str in trading_dates:
        logger.debug(f"Processing trading date: {date_str}")

        # Get top 100 stocks by market cap for the current date
        top_stocks = get_top_stocks_by_market_cap(date_str, limit=100)

        if not top_stocks:
            logger.warning(f"No top stocks found for date {date_str}, skipping")
            continue

        # Create equal-weighted portfolio
        total_stocks = len(top_stocks)
        weight = 1.0 / total_stocks

        logger.debug(f"Creating equal-weighted portfolio with {total_stocks} stocks, weight={weight:.4f}")

        # Create index composition
        current_composition = _create_index_composition(date_str, top_stocks, weight)
        compositions.extend(current_composition)

        # Calculate daily return if we have a previous portfolio
        daily_return = _calculate_daily_return(date_str, previous_portfolio)

        # Update cumulative return
        cumulative_return = (1 + cumulative_return) * (1 + daily_return) - 1

        # Store index performance
        performances.append({
            'date': date_str,
            'daily_return': daily_return,
            'cumulative_return': cumulative_return
        })

        # Update previous portfolio for next iteration
        previous_portfolio = [
            {'ticker': comp['ticker'], 'weight': comp['weight'], 'date': date_str}
            for comp in current_composition
        ]

    return compositions, performances

def _create_index_composition(date_str: str, top_stocks: List[Dict[str, Any]], weight: float) -> List[Dict[str, Any]]:
    """
    Create the index composition for a specific date.

    Args:
        date_str (str): Date string in ISO format
        top_stocks (List[Dict[str, Any]]): List of top stocks by market cap
        weight (float): Equal weight to assign to each stock

    Returns:
        List[Dict[str, Any]]: List of index composition records
    """
    composition = []
    for rank, stock in enumerate(top_stocks, 1):
        composition.append({
            'date': date_str,
            'ticker': stock['ticker'],
            'weight': weight,
            'rank': rank
        })
    return composition

def _calculate_daily_return(date_str: str, previous_portfolio: Optional[List[Dict[str, Any]]]) -> float:
    """
    Calculate the daily return of the index based on the previous portfolio.

    Args:
        date_str (str): Current date string in ISO format
        previous_portfolio (List[Dict[str, Any]], optional): Previous day's portfolio

    Returns:
        float: Daily return as a decimal (e.g., 0.01 for 1%)
    """
    if not previous_portfolio:
        return 0.0

    # Get current prices for previous portfolio stocks
    prev_tickers = [stock['ticker'] for stock in previous_portfolio]
    current_prices = get_stock_prices_for_date(date_str, prev_tickers)

    # Calculate return based on previous weights and current prices
    portfolio_return = 0.0
    valid_stocks = 0

    for prev_stock in previous_portfolio:
        ticker = prev_stock['ticker']
        prev_weight = prev_stock['weight']

        if ticker in current_prices:
            # Get previous close price
            prev_prices = get_stock_prices_for_date(prev_stock['date'], [ticker])
            if ticker in prev_prices:
                prev_close = prev_prices[ticker]['close']
                curr_close = current_prices[ticker]['close']

                # Calculate stock return
                if prev_close > 0:
                    stock_return = (curr_close - prev_close) / prev_close
                    portfolio_return += stock_return * prev_weight
                    valid_stocks += 1

    # Only return a non-zero value if we have valid stocks
    if valid_stocks > 0:
        return portfolio_return

    return 0.0
