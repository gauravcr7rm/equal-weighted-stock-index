# Equal-Weighted Stock Index Tracker

A backend service that tracks and manages a custom equal-weighted stock index comprising the top 100 US stocks by daily market capitalization.

## Features

- Daily tracking of top 100 US stocks by market cap
- Equal-weighted index construction and rebalancing
- Historical performance and composition retrieval
- Composition change detection
- Data export to Excel

## Tech Stack

- Python
- FastAPI
- DuckDB
- Redis
- Polars/Pandas
- Docker

## Setup Instructions

### Local Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file to add your API keys and configure settings.

6. Run the data acquisition job:
   ```
   python -m app.jobs.data_acquisition
   ```

7. Start the API server:
   ```
   python run_api.py
   ```

### Docker Setup

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Run the data acquisition job:
   ```
   docker-compose exec app python -m app.jobs.data_acquisition
   ```

## API Usage

### Build Index
```
curl -X POST "http://localhost:8000/build-index" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2023-01-31"}'
```

### Get Index Performance
```
curl "http://localhost:8000/index-performance?start_date=2023-01-01&end_date=2023-01-31"
```

### Get Index Composition
```
curl "http://localhost:8000/index-composition?date=2023-01-15"
```

### Get Composition Changes
```
curl "http://localhost:8000/composition-changes?start_date=2023-01-01&end_date=2023-01-31"
```

### Export Data
```
curl -X POST "http://localhost:8000/export-data" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2023-01-01", "end_date": "2023-01-31"}'
```

## Project Structure

```
.
├── app/                    # Main application package
│   ├── api/                # API endpoints and routes
│   │   ├── api.py          # FastAPI application setup
│   │   └── routes/         # API route modules
│   ├── core/               # Core application modules
│   │   └── config.py       # Configuration settings
│   ├── db/                 # Database modules
│   │   ├── database.py     # DuckDB connection and initialization
│   │   └── redis_cache.py  # Redis caching functionality
│   ├── jobs/               # Background jobs
│   │   └── data_acquisition.py  # Data acquisition job
│   ├── models/             # Pydantic models
│   │   ├── index.py        # Index-related models
│   │   └── stock.py        # Stock-related models
│   ├── services/           # Business logic services
│   │   ├── data_sources/   # Data source implementations
│   │   ├── data_storage.py # Data storage operations
│   │   ├── export_service.py  # Data export functionality
│   │   └── index_construction.py  # Index construction logic
│   └── main.py             # Application entry point
├── data/                   # Database files
├── exports/                # Exported files
├── tests/                  # Test modules
├── .env                    # Environment variables
├── .env.example            # Example environment variables
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── run.sh                  # Shell script to run the application
└── run_api.py              # Script to run the API server
```

## Database Schema

### Tables

1. **stocks** - Stock metadata
   - ticker (TEXT): Stock symbol
   - name (TEXT): Company name
   - sector (TEXT): Industry sector
   - exchange (TEXT): Stock exchange

2. **stock_prices** - Daily stock price and market cap data
   - date (DATE): Trading date
   - ticker (TEXT): Stock symbol
   - open (FLOAT): Opening price
   - high (FLOAT): High price
   - low (FLOAT): Low price
   - close (FLOAT): Closing price
   - volume (INTEGER): Trading volume
   - market_cap (FLOAT): Market capitalization

3. **index_compositions** - Daily index compositions
   - date (DATE): Trading date
   - ticker (TEXT): Stock symbol
   - weight (FLOAT): Stock weight in the index
   - rank (INTEGER): Market cap rank

4. **index_performance** - Daily index performance
   - date (DATE): Trading date
   - daily_return (FLOAT): Daily return percentage
   - cumulative_return (FLOAT): Cumulative return percentage

