import os
from pathlib import Path
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Database settings
    DB_PATH: str = os.getenv("DB_PATH", "./data/stockindex.db")

    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # Data source settings
    ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    USE_YAHOO_FINANCE: bool = os.getenv("USE_YAHOO_FINANCE", "true").lower() == "true"
    IEX_CLOUD_API_KEY: str = os.getenv("IEX_CLOUD_API_KEY", "")
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")

    # Data acquisition settings
    DATA_HISTORY_DAYS: int = int(os.getenv("DATA_HISTORY_DAYS", "30"))

    class Config:
        env_file = ".env"

settings = Settings()
