"""
Caching system for LogicPwn Business Logic Exploitation Framework.

This module provides a comprehensive caching system for improving performance
by caching responses, sessions, configurations, and validation results.
Designed for high-performance security testing and exploit chaining workflows.

Key Features:
- Response caching with TTL
- Session caching and persistence
- Configuration caching
- Validation result caching
- Memory-efficient cache management
- Cache invalidation strategies
- Performance monitoring

Usage::

    # Cache responses
    cached_response = cache_manager.get_response(url, method)
    if not cached_response:
                                            response = send_request(url, method)
                                            cache_manager.set_response(url, method, response)
    
    # Cache sessions
    session = cache_manager.get_session(session_id)
    if not session:
                                            session = authenticate_session(config)
                                            cache_manager.set_session(session_id, session)
"""

import time
import functools
from typing import Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
import json
from loguru import logger


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
                                            """Check if cache entry has expired."""
                                            return time.time() - self.timestamp > self.ttl

    def access(self):
                                            """Mark entry as accessed."""
                                            self.access_count += 1


class CacheManager:
    """High-performance cache manager for LogicPwn."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
                                            """
                                            Initialize cache manager.
                                            
                                            Args:
                                                max_size: Maximum number of cache entries
                                                default_ttl: Default time-to-live in seconds
                                            """
                                            self.max_size = max_size
                                            self.default_ttl = default_ttl
                                            self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
                                            self.stats = {
                                                'hits': 0,
                                                'misses': 0,
                                                'evictions': 0,
                                                'expirations': 0
                                            }
    
    def _generate_key(self, *args, **kwargs) -> str:
                                            """Generate cache key from arguments."""
                                            key_data = str(args) + str(sorted(kwargs.items()))
                                            return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
                                            """
                                            Get value from cache.
                                            
                                            Args:
                                                key: Cache key
                                                
                                            Returns:
                                                Cached value or None if not found/expired
                                            """
                                            if key in self.cache:
                                                entry = self.cache[key]
                                                
                                                if entry.is_expired():
                                                    del self.cache[key]
                                                    self.stats['expirations'] += 1
                                                    self.stats['misses'] += 1
                                                    return None
                                                
                                                # Move to end (LRU)
                                                self.cache.move_to_end(key)
                                                entry.access()
                                                self.stats['hits'] += 1
                                                return entry.value
                                            
                                            self.stats['misses'] += 1
                                            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
                                                metadata: Optional[Dict[str, Any]] = None) -> None:
                                            """
                                            Set value in cache.
                                            
                                            Args:
                                                key: Cache key
                                                value: Value to cache
                                                ttl: Time-to-live in seconds (uses default if None)
                                                metadata: Additional metadata for the entry
                                            """
                                                # Evict if cache is full
                                            if len(self.cache) >= self.max_size:
                                                self._evict_oldest()
                                            
                                            entry = CacheEntry(
                                                value=value,
                                                timestamp=time.time(),
                                                ttl=ttl or self.default_ttl,
                                                metadata=metadata or {}
                                            )
                                            
                                            self.cache[key] = entry
                                            logger.debug(f"Cached entry: {key} (TTL: {entry.ttl}s)")
    
    def _evict_oldest(self) -> None:
                                            """Evict oldest cache entry."""
                                            if self.cache:
                                                oldest_key = next(iter(self.cache))
                                                del self.cache[oldest_key]
                                                self.stats['evictions'] += 1
                                                logger.debug(f"Evicted cache entry: {oldest_key}")
    
    def invalidate(self, key: str) -> bool:
                                            """
                                            Invalidate cache entry.
                                            
                                            Args:
                                                key: Cache key to invalidate
                                                
                                            Returns:
                                                True if entry was found and removed
                                            """
                                            if key in self.cache:
                                                del self.cache[key]
                                                logger.debug(f"Invalidated cache entry: {key}")
                                                return True
                                            return False
    
    def clear(self) -> None:
                                            """Clear all cache entries."""
                                            self.cache.clear()
                                            logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
                                            """
                                            Remove expired entries.
                                            
                                            Returns:
                                                Number of expired entries removed
                                            """
                                            expired_keys = [
                                                key for key, entry in self.cache.items()
                                                if entry.is_expired()
                                            ]
                                            
                                            for key in expired_keys:
                                                del self.cache[key]
                                                self.stats['expirations'] += 1
                                            
                                            if expired_keys:
                                                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
                                            
                                            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
                                            """Get cache statistics."""
                                            total_requests = self.stats['hits'] + self.stats['misses']
                                            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
                                            
                                            return {
                                                **self.stats,
                                                'size': len(self.cache),
                                                'max_size': self.max_size,
                                                'hit_rate': hit_rate,
                                                'total_requests': total_requests
                                            }


class ResponseCache:
    """Specialized cache for HTTP responses."""
    
    def __init__(self, max_size: int = 500, default_ttl: int = 300):
                                            """
                                            Initialize response cache.
                                            
                                            Args:
                                                max_size: Maximum number of cached responses
                                                default_ttl: Default TTL for responses
                                            """
                                            self.cache_manager = CacheManager(max_size, default_ttl)
    
    def get_response(self, url: str, method: str, params: Optional[Dict] = None,
                                                        headers: Optional[Dict] = None) -> Optional[Any]:
                                            """
                                            Get cached response.
                                            
                                            Args:
                                                url: Request URL
                                                method: HTTP method
                                                params: Query parameters
                                                headers: Request headers
                                                
                                            Returns:
                                                Cached response or None
                                            """
                                            key = self._generate_response_key(url, method, params, headers)
                                            return self.cache_manager.get(key)
    
    def set_response(self, url: str, method: str, response: Any,
                                                        params: Optional[Dict] = None, headers: Optional[Dict] = None,
                                                        ttl: Optional[int] = None) -> None:
                                            """
                                            Cache response.
                                            
                                            Args:
                                                url: Request URL
                                                method: HTTP method
                                                response: Response to cache
                                                params: Query parameters
                                                headers: Request headers
                                                ttl: Custom TTL
                                            """
                                            key = self._generate_response_key(url, method, params, headers)
                                            metadata = {
                                                'url': url,
                                                'method': method,
                                                'params': params,
                                                'headers': headers
                                            }
                                            self.cache_manager.set(key, response, ttl, metadata)
    
    def _generate_response_key(self, url: str, method: str, 
                                                                 params: Optional[Dict], headers: Optional[Dict]) -> str:
                                            """Generate cache key for response."""
                                            key_data = {
                                                'url': url,
                                                'method': method.upper(),
                                                'params': params or {},
                                                'headers': {k.lower(): v for k, v in (headers or {}).items()}
                                            }
                                            return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


class SessionCache:
    """Specialized cache for authentication sessions."""
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
                                            """
                                            Initialize session cache.
                                            
                                            Args:
                                                max_size: Maximum number of cached sessions
                                                default_ttl: Default TTL for sessions (1 hour)
                                            """
                                            self.cache_manager = CacheManager(max_size, default_ttl)
    
    def get_session(self, session_id: str) -> Optional[Any]:
                                            """
                                            Get cached session.
                                            
                                            Args:
                                                session_id: Session identifier
                                                
                                            Returns:
                                                Cached session or None
                                            """
                                            return self.cache_manager.get(session_id)
    
    def set_session(self, session_id: str, session: Any, ttl: Optional[int] = None) -> None:
                                            """
                                            Cache session.
                                            
                                            Args:
                                                session_id: Session identifier
                                                session: Session to cache
                                                ttl: Custom TTL
                                            """
                                            metadata = {
                                                'session_id': session_id,
                                                'created_at': time.time()
                                            }
                                            self.cache_manager.set(session_id, session, ttl, metadata)
    
    def invalidate_session(self, session_id: str) -> bool:
                                            """
                                            Invalidate cached session.
                                            
                                            Args:
                                                session_id: Session identifier
                                                
                                            Returns:
                                                True if session was found and removed
                                            """
                                            return self.cache_manager.invalidate(session_id)


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
                                            ttl: Time-to-live in seconds
                                            key_func: Custom key generation function
                                            
    Returns:
                                            Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
                                            cache_manager = CacheManager(default_ttl=ttl)
                                            
                                            @functools.wraps(func)
                                            def wrapper(*args, **kwargs):
                                                # Generate cache key
                                                if key_func:
                                                    cache_key = key_func(*args, **kwargs)
                                                else:
                                                    cache_key = cache_manager._generate_key(*args, **kwargs)
                                                
                                                # Try to get from cache
                                                cached_result = cache_manager.get(cache_key)
                                                if cached_result is not None:
                                                    logger.debug(f"Cache hit for {func.__name__}")
                                                    return cached_result
                                                
                                                # Execute function and cache result
                                                result = func(*args, **kwargs)
                                                cache_manager.set(cache_key, result, ttl)
                                                logger.debug(f"Cache miss for {func.__name__}, cached result")
                                                
                                                return result
                                            
                                            return wrapper
    return decorator


# Global cache instances
response_cache = ResponseCache()
session_cache = SessionCache()
config_cache = CacheManager(max_size=100, default_ttl=600)  # 10 minutes for config


def get_cache_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all cache managers."""
    return {
                                            'response_cache': response_cache.cache_manager.get_stats(),
                                            'session_cache': session_cache.cache_manager.get_stats(),
                                            'config_cache': config_cache.get_stats()
    }


def clear_all_caches() -> None:
    """Clear all cache managers."""
    response_cache.cache_manager.clear()
    session_cache.cache_manager.clear()
    config_cache.clear()
    logger.info("All caches cleared") 