#!/usr/bin/env python
import logging
import sys
import uvicorn
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("run_api")

# Ensure data directory exists
data_dir = Path("./data")
data_dir.mkdir(parents=True, exist_ok=True)

# Ensure exports directory exists
exports_dir = Path("./exports")
exports_dir.mkdir(parents=True, exist_ok=True)

# Import settings
from app.core.config import settings

def main():
    """Run the API server."""
    try:
        logger.info(f"Starting Equal-Weighted Stock Index Tracker API")
        logger.info(f"API will be available at http://{settings.API_HOST}:{settings.API_PORT}")
        
        uvicorn.run(
            "app.api.api:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
        )
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
