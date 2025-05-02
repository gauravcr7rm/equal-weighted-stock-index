import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main")

# Ensure data directory exists
data_dir = Path("./data")
data_dir.mkdir(parents=True, exist_ok=True)

# Ensure exports directory exists
exports_dir = Path("./exports")
exports_dir.mkdir(parents=True, exist_ok=True)

# Import app and settings
from app.api.api import app  # noqa: F401
from app.core.config import settings

# Log startup information
logger.info(f"Starting Equal-Weighted Stock Index Tracker API")
logger.info(f"API will be available at http://{settings.API_HOST}:{settings.API_PORT}")

if __name__ == "__main__":
    try:
        import uvicorn
        logger.info("Starting uvicorn server...")
        uvicorn.run(
            "app.main:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=True,
        )
    except ImportError:
        logger.error("Uvicorn not installed. Please install it with 'pip install uvicorn'.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)
