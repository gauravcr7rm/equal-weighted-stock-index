import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

from app.services.data_sources import fetch_stock_data
from app.services.data_storage import store_stock_metadata, store_stock_prices
from app.db.database import get_db_connection, init_db
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("data_acquisition")

def run_data_acquisition(days=None, limit=None):
    """
    Run the data acquisition job to fetch and store stock data.

    Args:
        days (int, optional): Number of days of history to fetch. Defaults to settings.DATA_HISTORY_DAYS.
        limit (int, optional): Number of stocks to fetch. Defaults to 150.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use default values from settings if not provided
        if days is None:
            days = settings.DATA_HISTORY_DAYS

        if limit is None:
            limit = 150  # Default to 150 to ensure we have enough data

        logger.info(f"Starting data acquisition job for the last {days} days with limit of {limit} stocks")

        # Ensure database is initialized
        init_db()

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        logger.info(f"Fetching data from {start_date.date()} to {end_date.date()}")

        # Fetch stock data
        stock_data = fetch_stock_data(start_date, end_date)

        if not stock_data or not stock_data.get('metadata') or not stock_data.get('prices'):
            logger.error("Failed to fetch stock data")
            return False

        # Store metadata
        logger.info(f"Storing metadata for {len(stock_data['metadata'])} stocks")
        store_stock_metadata(stock_data['metadata'])

        # Store prices
        logger.info(f"Storing {len(stock_data['prices'])} price records")
        store_stock_prices(stock_data['prices'])

        # Verify data was stored
        conn = get_db_connection()
        stock_count = conn.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
        price_count = conn.execute("SELECT COUNT(*) FROM stock_prices").fetchone()[0]
        conn.close()

        logger.info(f"Verification: {stock_count} stocks and {price_count} price records in database")

        logger.info("Data acquisition completed successfully")
        return True

    except Exception as e:
        logger.exception(f"Error in data acquisition: {e}")
        return False

if __name__ == "__main__":
    # Ensure data directory exists
    data_dir = Path(os.path.dirname(settings.DB_PATH))
    data_dir.mkdir(parents=True, exist_ok=True)

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Fetch stock data')
    parser.add_argument('--days', type=int, default=settings.DATA_HISTORY_DAYS,
                        help=f'Number of days of history to fetch (default: {settings.DATA_HISTORY_DAYS})')
    parser.add_argument('--limit', type=int, default=150,
                        help='Number of stocks to fetch (default: 150)')
    args = parser.parse_args()

    success = run_data_acquisition(days=args.days, limit=args.limit)

    if not success:
        logger.error("Data acquisition failed")
        sys.exit(1)
