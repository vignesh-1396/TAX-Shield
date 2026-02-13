"""
Redis Cache Service for ITC Shield
Provides caching for vendor data and GSP responses
"""
import json
import logging
from typing import Optional, Any
from datetime import timedelta
from functools import wraps

logger = logging.getLogger(__name__)

# Global cache instance
_cache_client = None

def get_cache_client():
    """Get or create Redis cache client"""
    global _cache_client
    
    if _cache_client is not None:
        return _cache_client
    
    try:
        from app.core.config import settings
        import redis
        
        # Only initialize if Redis URL is configured
        if not hasattr(settings, 'REDIS_URL') or not settings.REDIS_URL:
            logger.warning("Redis not configured. Caching disabled.")
            return None
        
        _cache_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True
        )
        
        # Test connection
        _cache_client.ping()
        logger.info("Redis cache connected successfully")
        return _cache_client
        
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")
        return None


class CacheService:
    """Service for caching vendor data and API responses"""
    
    # Cache TTL configurations (in seconds)
    VENDOR_DATA_TTL = 24 * 60 * 60  # 24 hours
    GSP_TOKEN_TTL = 50 * 60  # 50 minutes (tokens valid for 1 hour)
    COMPLIANCE_CHECK_TTL = 7 * 24 * 60 * 60  # 7 days
    
    def __init__(self):
        self.client = get_cache_client()
        self.enabled = self.client is not None
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        return f"itc_shield:{prefix}:{identifier}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def get_vendor_data(self, gstin: str) -> Optional[dict]:
        """Get cached vendor data"""
        key = self._make_key("vendor", gstin)
        return self.get(key)
    
    def set_vendor_data(self, gstin: str, data: dict) -> bool:
        """Cache vendor data for 24 hours"""
        key = self._make_key("vendor", gstin)
        return self.set(key, data, self.VENDOR_DATA_TTL)
    
    def invalidate_vendor(self, gstin: str) -> bool:
        """Invalidate cached vendor data"""
        key = self._make_key("vendor", gstin)
        return self.delete(key)
    
    def get_gsp_token(self, provider: str) -> Optional[str]:
        """Get cached GSP access token"""
        key = self._make_key("gsp_token", provider)
        data = self.get(key)
        return data.get("token") if data else None
    
    def set_gsp_token(self, provider: str, token: str, expires_in: int = None) -> bool:
        """Cache GSP access token"""
        key = self._make_key("gsp_token", provider)
        ttl = expires_in if expires_in else self.GSP_TOKEN_TTL
        return self.set(key, {"token": token}, ttl)


# Singleton instance
cache = CacheService()


def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=3600, key_prefix="vendor")
        def get_vendor(gstin: str):
            return fetch_from_api(gstin)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache.enabled:
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
