import json
import logging
import redis
from typing import Any, Optional
from redis.exceptions import RedisError

from app.core.config import settings

# Configure logging
logger = logging.getLogger("redis_cache")

class RedisCache:
    """Redis cache client for storing and retrieving data."""

    def __init__(self, host: str = None, port: int = None, decode_responses: bool = True):
        """
        Initialize Redis cache client.

        Args:
            host (str, optional): Redis host. Defaults to settings.REDIS_HOST.
            port (int, optional): Redis port. Defaults to settings.REDIS_PORT.
            decode_responses (bool, optional): Whether to decode responses. Defaults to True.
        """
        self.host = host or settings.REDIS_HOST
        self.port = port or settings.REDIS_PORT
        self.decode_responses = decode_responses
        self._client = None

        # Initialize connection
        self._initialize_connection()

    def _initialize_connection(self) -> None:
        """Initialize Redis connection."""
        try:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                decode_responses=self.decode_responses
            )
            # Test connection
            self._client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except RedisError as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self._client = None

    def is_connected(self) -> bool:
        """
        Check if connected to Redis.

        Returns:
            bool: True if connected, False otherwise
        """
        if not self._client:
            return False

        try:
            self._client.ping()
            return True
        except RedisError:
            return False

    def set(self, key: str, data: Any, expiration: int = 3600) -> bool:
        """
        Set data in Redis cache.

        Args:
            key (str): Cache key
            data (Any): Data to cache (will be JSON serialized)
            expiration (int, optional): Expiration time in seconds. Defaults to 3600 (1 hour).

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Not connected to Redis, cannot set cache")
            return False

        try:
            serialized_data = json.dumps(data)
            self._client.setex(key, expiration, serialized_data)
            logger.debug(f"Cache set for key: {key}, expires in {expiration}s")
            return True
        except (RedisError, TypeError, ValueError) as e:
            logger.error(f"Failed to set cache for key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Get data from Redis cache.

        Args:
            key (str): Cache key

        Returns:
            Any or None: Cached data (JSON deserialized) or None if not found
        """
        if not self.is_connected():
            logger.warning("Not connected to Redis, cannot get cache")
            return None

        try:
            data = self._client.get(key)
            if data:
                logger.debug(f"Cache hit for key: {key}")
                return json.loads(data)
            logger.debug(f"Cache miss for key: {key}")
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete data from Redis cache.

        Args:
            key (str): Cache key

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Not connected to Redis, cannot delete cache")
            return False

        try:
            self._client.delete(key)
            logger.debug(f"Cache deleted for key: {key}")
            return True
        except RedisError as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False

    def clear(self) -> bool:
        """
        Clear all cache data.

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.warning("Not connected to Redis, cannot clear cache")
            return False

        try:
            self._client.flushall()
            logger.info("Cache cleared")
            return True
        except RedisError as e:
            logger.error(f"Failed to clear cache: {e}")
            return False

# Create a singleton instance
redis_cache = RedisCache()

# Backward compatibility functions
def set_cache(key: str, data: Any, expiration: int = 3600) -> bool:
    """
    Set data in Redis cache.

    Args:
        key (str): Cache key
        data (Any): Data to cache
        expiration (int, optional): Expiration time in seconds. Defaults to 3600 (1 hour).

    Returns:
        bool: True if successful, False otherwise
    """
    return redis_cache.set(key, data, expiration)

def get_cache(key: str) -> Optional[Any]:
    """
    Get data from Redis cache.

    Args:
        key (str): Cache key

    Returns:
        Any or None: Cached data or None if not found
    """
    return redis_cache.get(key)

def delete_cache(key: str) -> bool:
    """
    Delete data from Redis cache.

    Args:
        key (str): Cache key

    Returns:
        bool: True if successful, False otherwise
    """
    return redis_cache.delete(key)

def clear_cache() -> bool:
    """
    Clear all cache data.

    Returns:
        bool: True if successful, False otherwise
    """
    return redis_cache.clear()
