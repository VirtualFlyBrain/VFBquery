"""
VFBquery Caching Enhancements

This module implements caching optimizations inspired by VFB_connect 
to improve VFBquery performance for repeated queries.

Features:
1. Term info result caching (similar to VFB_connect's VFBTerm cache)
2. SOLR query result caching
3. Query result caching for get_instances and other functions
4. Configurable cache expiry and size limits
5. Memory-based and disk-based caching options
"""

import os
import json
import time
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import lru_cache, wraps
from dataclasses import dataclass, asdict
import threading

# Custom JSON encoder for caching
from .vfb_queries import NumpyEncoder

@dataclass
class CacheConfig:
    """Configuration for VFBquery caching system."""
    enabled: bool = True
    memory_cache_size_mb: int = 2048  # Max memory cache size in MB (2GB default)
    max_items: int = 10000  # Max items in memory cache (fallback limit)
    disk_cache_enabled: bool = True
    disk_cache_dir: Optional[str] = None
    cache_ttl_hours: int = 2160  # Cache time-to-live in hours (3 months = 90 days * 24 hours)
    solr_cache_enabled: bool = True
    term_info_cache_enabled: bool = True
    query_result_cache_enabled: bool = True

class VFBQueryCache:
    """
    Enhanced caching system for VFBquery inspired by VFB_connect optimizations.
    
    Provides multiple layers of caching:
    - Memory cache for frequently accessed items (size-limited)
    - Disk cache for persistence across sessions  
    - Query result caching for expensive operations
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = {'hits': 0, 'misses': 0, 'memory_size_bytes': 0}
        self._lock = threading.RLock()
        
        # Set up disk cache directory
        if self.config.disk_cache_enabled:
            if self.config.disk_cache_dir:
                self.cache_dir = Path(self.config.disk_cache_dir)
            else:
                # Use similar location to VFB_connect
                self.cache_dir = Path.home() / '.vfbquery_cache'
            self.cache_dir.mkdir(exist_ok=True)
        
        # Enable caching based on environment variable (like VFB_connect)
        env_enabled = os.getenv('VFBQUERY_CACHE_ENABLED', '').lower()
        if env_enabled in ('false', '0', 'no'):
            self.config.enabled = False
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create deterministic hash from arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid based on TTL."""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        
        age_hours = (time.time() - cache_entry['timestamp']) / 3600
        return age_hours < self.config.cache_ttl_hours
    
    def _get_from_memory(self, cache_key: str) -> Optional[Any]:
        """Get item from memory cache."""
        with self._lock:
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                if self._is_cache_valid(entry):
                    self._cache_stats['hits'] += 1
                    return entry['data']
                else:
                    # Remove expired entry and update memory size tracking
                    expired_entry = self._memory_cache.pop(cache_key)
                    self._cache_stats['memory_size_bytes'] -= expired_entry.get('size_bytes', 0)
            
            self._cache_stats['misses'] += 1
            return None
    
    def _get_object_size(self, obj: Any) -> int:
        """Estimate memory size of an object in bytes."""
        try:
            import sys
            if isinstance(obj, (str, bytes)):
                return len(obj)
            elif isinstance(obj, dict):
                return sum(self._get_object_size(k) + self._get_object_size(v) for k, v in obj.items())
            elif isinstance(obj, (list, tuple)):
                return sum(self._get_object_size(item) for item in obj)
            else:
                # Fallback: use sys.getsizeof for other objects
                return sys.getsizeof(obj)
        except:
            # If size estimation fails, assume 1KB
            return 1024

    def _store_in_memory(self, cache_key: str, data: Any):
        """Store item in memory cache with size-based LRU eviction."""
        with self._lock:
            entry = {
                'data': data,
                'timestamp': time.time(),
                'size_bytes': self._get_object_size(data)
            }
            
            # Check if we need to evict items to stay under memory limit
            max_size_bytes = self.config.memory_cache_size_mb * 1024 * 1024
            
            # If this single item is larger than the cache limit, don't cache it
            if entry['size_bytes'] > max_size_bytes:
                return
            
            # Evict items if adding this one would exceed memory limit or max items
            while (len(self._memory_cache) >= self.config.max_items or
                   self._cache_stats['memory_size_bytes'] + entry['size_bytes'] > max_size_bytes):
                if not self._memory_cache:
                    break
                # Remove oldest item (first in dict)
                oldest_key = next(iter(self._memory_cache))
                old_entry = self._memory_cache.pop(oldest_key)
                self._cache_stats['memory_size_bytes'] -= old_entry.get('size_bytes', 0)
            
            # Add new entry
            self._memory_cache[cache_key] = entry
            self._cache_stats['memory_size_bytes'] += entry['size_bytes']
    
    def _get_from_disk(self, cache_key: str) -> Optional[Any]:
        """Get item from disk cache."""
        if not self.config.disk_cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    entry = pickle.load(f)
                    if self._is_cache_valid(entry):
                        return entry['data']
                    else:
                        # Remove expired file
                        cache_file.unlink()
            except Exception:
                # If file is corrupted, remove it
                cache_file.unlink(missing_ok=True)
        
        return None
    
    def _store_on_disk(self, cache_key: str, data: Any):
        """Store item on disk cache."""
        if not self.config.disk_cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        try:
            entry = {
                'data': data,
                'timestamp': time.time()
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(entry, f)
        except Exception as e:
            print(f"Warning: Could not save to disk cache: {e}")
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get item from cache (memory first, then disk)."""
        if not self.config.enabled:
            return None
        
        # Try memory cache first
        result = self._get_from_memory(cache_key)
        if result is not None:
            return result
        
        # Try disk cache
        result = self._get_from_disk(cache_key)
        if result is not None:
            # Store in memory for future access
            self._store_in_memory(cache_key, result)
            return result
        
        return None
    
    def set(self, cache_key: str, data: Any):
        """Store item in cache (both memory and disk)."""
        if not self.config.enabled:
            return
        
        self._store_in_memory(cache_key, data)
        self._store_on_disk(cache_key, data)
    
    def clear(self):
        """Clear all caches."""
        with self._lock:
            self._memory_cache.clear()
            self._cache_stats['memory_size_bytes'] = 0
            
        if self.config.disk_cache_enabled and hasattr(self, 'cache_dir') and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._cache_stats['hits'] + self._cache_stats['misses']
        hit_rate = (self._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        memory_size_mb = self._cache_stats.get('memory_size_bytes', 0) / (1024 * 1024)
        
        return {
            'enabled': self.config.enabled,
            'memory_cache_items': len(self._memory_cache),
            'memory_cache_size_mb': round(memory_size_mb, 2),
            'memory_cache_limit_mb': self.config.memory_cache_size_mb,
            'max_items': self.config.max_items,
            'hits': self._cache_stats['hits'],
            'misses': self._cache_stats['misses'],
            'hit_rate_percent': round(hit_rate, 2),
            'disk_cache_enabled': self.config.disk_cache_enabled,
            'cache_ttl_hours': self.config.cache_ttl_hours,
            'cache_ttl_days': round(self.config.cache_ttl_hours / 24, 1)
        }


# Global cache instance
_global_cache = VFBQueryCache()

def configure_cache(config: CacheConfig):
    """Configure the global cache instance."""
    global _global_cache
    _global_cache = VFBQueryCache(config)

def get_cache() -> VFBQueryCache:
    """Get the global cache instance."""
    return _global_cache

def cache_result(cache_prefix: str, enabled_check: Optional[str] = None):
    """
    Decorator to cache function results.
    
    Args:
        cache_prefix: Prefix for cache keys
        enabled_check: Config attribute to check if this cache type is enabled
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Check if this specific cache type is enabled
            if enabled_check and not getattr(cache.config, enabled_check, True):
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache._generate_cache_key(cache_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:  # Only cache non-None results
                cache.set(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def enable_vfbquery_caching(
    cache_ttl_hours: int = 2160,  # 3 months default
    memory_cache_size_mb: int = 2048,  # 2GB default
    max_items: int = 10000,
    disk_cache_enabled: bool = True,
    disk_cache_dir: Optional[str] = None
):
    """
    Enable VFBquery caching with specified configuration.
    
    Args:
        cache_ttl_hours: Cache time-to-live in hours (default: 2160 = 3 months)
        memory_cache_size_mb: Maximum memory cache size in MB (default: 2048 = 2GB)  
        max_items: Maximum number of items in memory cache (default: 10000)
        disk_cache_enabled: Enable persistent disk caching (default: True)
        disk_cache_dir: Custom cache directory path (optional)
    
    Usage:
        from vfbquery.cache_enhancements import enable_vfbquery_caching
        enable_vfbquery_caching()  # Use defaults: 3 months TTL, 2GB memory
        enable_vfbquery_caching(cache_ttl_hours=720, memory_cache_size_mb=1024)  # 1 month, 1GB
    """
    config = CacheConfig(
        enabled=True,
        cache_ttl_hours=cache_ttl_hours,
        memory_cache_size_mb=memory_cache_size_mb,
        max_items=max_items,
        disk_cache_enabled=disk_cache_enabled,
        disk_cache_dir=disk_cache_dir
    )
    configure_cache(config)
    print(f"VFBquery caching enabled: TTL={cache_ttl_hours}h ({cache_ttl_hours//24} days), Memory={memory_cache_size_mb}MB")

def disable_vfbquery_caching():
    """Disable VFBquery caching."""
    config = CacheConfig(enabled=False)
    configure_cache(config)
    print("VFBquery caching disabled")

def clear_vfbquery_cache():
    """Clear all VFBquery caches."""
    get_cache().clear()
    print("VFBquery cache cleared")

def get_vfbquery_cache_stats() -> Dict[str, Any]:
    """Get VFBquery cache statistics."""
    return get_cache().get_stats()

def set_cache_ttl(hours: int):
    """
    Update the cache TTL (time-to-live) for new cache entries.
    
    Args:
        hours: New TTL in hours (e.g., 24 for 1 day, 720 for 1 month, 2160 for 3 months)
        
    Examples:
        set_cache_ttl(24)    # 1 day
        set_cache_ttl(168)   # 1 week  
        set_cache_ttl(720)   # 1 month
        set_cache_ttl(2160)  # 3 months (default)
    """
    cache = get_cache()
    cache.config.cache_ttl_hours = hours
    days = hours / 24
    print(f"Cache TTL updated to {hours} hours ({days:.1f} days)")

def set_cache_memory_limit(size_mb: int):
    """
    Update the memory cache size limit.
    
    Args:
        size_mb: Maximum memory cache size in MB (e.g., 512, 1024, 2048)
        
    Examples:
        set_cache_memory_limit(512)   # 512MB
        set_cache_memory_limit(1024)  # 1GB
        set_cache_memory_limit(2048)  # 2GB (default)
    """
    cache = get_cache()
    old_limit = cache.config.memory_cache_size_mb
    cache.config.memory_cache_size_mb = size_mb
    
    # If reducing size, trigger eviction if needed
    if size_mb < old_limit:
        with cache._lock:
            max_size_bytes = size_mb * 1024 * 1024
            while cache._cache_stats.get('memory_size_bytes', 0) > max_size_bytes:
                if not cache._memory_cache:
                    break
                # Remove oldest item
                oldest_key = next(iter(cache._memory_cache))
                old_entry = cache._memory_cache.pop(oldest_key)
                cache._cache_stats['memory_size_bytes'] -= old_entry.get('size_bytes', 0)
    
    print(f"Memory cache limit updated from {old_limit}MB to {size_mb}MB")

def set_cache_max_items(max_items: int):
    """
    Update the maximum number of items in memory cache.
    
    Args:
        max_items: Maximum number of cached items (e.g., 1000, 5000, 10000)
        
    Examples:
        set_cache_max_items(1000)   # 1K items
        set_cache_max_items(5000)   # 5K items  
        set_cache_max_items(10000)  # 10K items (default)
    """
    cache = get_cache()
    old_limit = cache.config.max_items
    cache.config.max_items = max_items
    
    # If reducing count, trigger eviction if needed
    if max_items < old_limit:
        with cache._lock:
            while len(cache._memory_cache) > max_items:
                if not cache._memory_cache:
                    break
                # Remove oldest item
                oldest_key = next(iter(cache._memory_cache))
                old_entry = cache._memory_cache.pop(oldest_key)
                cache._cache_stats['memory_size_bytes'] -= old_entry.get('size_bytes', 0)
    
    print(f"Max cache items updated from {old_limit} to {max_items}")

def enable_disk_cache(cache_dir: Optional[str] = None):
    """
    Enable persistent disk caching.
    
    Args:
        cache_dir: Optional custom cache directory path
        
    Examples:
        enable_disk_cache()                          # Use default location
        enable_disk_cache('/tmp/my_vfbquery_cache')  # Custom location
    """
    cache = get_cache()
    cache.config.disk_cache_enabled = True
    
    if cache_dir:
        cache.config.disk_cache_dir = cache_dir
        cache.cache_dir = Path(cache_dir)
        cache.cache_dir.mkdir(exist_ok=True)
    
    print(f"Disk caching enabled: {getattr(cache, 'cache_dir', 'default location')}")

def disable_disk_cache():
    """Disable persistent disk caching (memory cache only)."""
    cache = get_cache()
    cache.config.disk_cache_enabled = False
    print("Disk caching disabled (memory cache only)")

def get_cache_config() -> Dict[str, Any]:
    """
    Get current cache configuration settings.
    
    Returns:
        Dictionary with current cache configuration
    """
    cache = get_cache()
    config = cache.config
    
    return {
        'enabled': config.enabled,
        'cache_ttl_hours': config.cache_ttl_hours,
        'cache_ttl_days': config.cache_ttl_hours / 24,
        'memory_cache_size_mb': config.memory_cache_size_mb,
        'max_items': config.max_items,
        'disk_cache_enabled': config.disk_cache_enabled,
        'disk_cache_dir': config.disk_cache_dir,
        'solr_cache_enabled': config.solr_cache_enabled,
        'term_info_cache_enabled': config.term_info_cache_enabled,
        'query_result_cache_enabled': config.query_result_cache_enabled
    }
