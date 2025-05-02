import os
import duckdb
from pathlib import Path
from app.core.config import settings

# Ensure data directory exists
data_dir = Path(os.path.dirname(settings.DB_PATH))
data_dir.mkdir(parents=True, exist_ok=True)

def get_db_connection():
    """Get a connection to the DuckDB database."""
    conn = duckdb.connect(settings.DB_PATH)
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    
    # Create stocks table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        ticker TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT,
        exchange TEXT
    )
    """)
    
    # Create stock_prices table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        date DATE,
        ticker TEXT,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume INTEGER,
        market_cap FLOAT,
        PRIMARY KEY (date, ticker)
    )
    """)
    
    # Create index_compositions table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS index_compositions (
        date DATE,
        ticker TEXT,
        weight FLOAT,
        rank INTEGER,
        PRIMARY KEY (date, ticker)
    )
    """)
    
    # Create index_performance table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS index_performance (
        date DATE PRIMARY KEY,
        daily_return FLOAT,
        cumulative_return FLOAT
    )
    """)
    
    conn.close()

def reset_db():
    """Reset the database by dropping all tables."""
    conn = get_db_connection()
    
    conn.execute("DROP TABLE IF EXISTS stocks")
    conn.execute("DROP TABLE IF EXISTS stock_prices")
    conn.execute("DROP TABLE IF EXISTS index_compositions")
    conn.execute("DROP TABLE IF EXISTS index_performance")
    
    conn.close()
    
    # Reinitialize the database
    init_db()

# Initialize the database when the module is imported
init_db()
