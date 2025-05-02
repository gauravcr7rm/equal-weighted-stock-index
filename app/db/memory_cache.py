import time
from typing import Dict, Any, Optional

# Simple in-memory cache
_cache: Dict[str, Dict[str, Any]] = {}

def set_cache(key: str, data: Any, expiration: int = 3600) -> bool:
    """
    Set data in memory cache.
    
    Args:
        key (str): Cache key
        data (Any): Data to cache
        expiration (int): Expiration time in seconds (default: 1 hour)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        _cache[key] = {
            'data': data,
            'expires_at': time.time() + expiration
        }
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False

def get_cache(key: str) -> Optional[Any]:
    """
    Get data from memory cache.
    
    Args:
        key (str): Cache key
        
    Returns:
        Any or None: Cached data or None if not found or expired
    """
    try:
        cache_entry = _cache.get(key)
        if not cache_entry:
            return None
        
        # Check if expired
        if time.time() > cache_entry['expires_at']:
            del _cache[key]
            return None
        
        return cache_entry['data']
    except Exception as e:
        print(f"Cache error: {e}")
        return None

def delete_cache(key: str) -> bool:
    """
    Delete data from memory cache.
    
    Args:
        key (str): Cache key
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if key in _cache:
            del _cache[key]
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False

def clear_cache() -> bool:
    """
    Clear all cache data.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        _cache.clear()
        return True
    except Exception as e:
        print(f"Cache error: {e}")
        return False
