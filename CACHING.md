# VFBquery Caching Guide

VFBquery includes intelligent caching for optimal performance. Caching is **enabled by default** with production-ready settings.

## Default Behavior

VFBquery automatically enables caching when imported:

```python
import vfbquery as vfb

# Caching is already active with optimal settings:
# - 3-month cache duration
# - 2GB memory cache with LRU eviction  
# - Persistent disk storage
# - Zero configuration required

result = vfb.get_term_info('FBbt_00003748')  # Cached automatically
```

## Runtime Configuration

Adjust cache settings while your application is running:

```python
import vfbquery as vfb

# Modify cache duration
vfb.set_cache_ttl(720)                    # 1 month  
vfb.set_cache_ttl(24)                     # 1 day

# Adjust memory limits
vfb.set_cache_memory_limit(512)           # 512MB
vfb.set_cache_max_items(5000)             # 5K items

# Toggle disk persistence  
vfb.disable_disk_cache()                  # Memory-only
vfb.enable_disk_cache()                   # Restore persistence
```

### Environment Control

Disable caching globally if needed:

```bash
export VFBQUERY_CACHE_ENABLED=false
```

## Performance Benefits

VFBquery caching provides significant performance improvements:

```python
import vfbquery as vfb

# First query: builds cache (~1-2 seconds)  
result1 = vfb.get_term_info('FBbt_00003748')

# Subsequent queries: served from cache (<0.1 seconds)
result2 = vfb.get_term_info('FBbt_00003748')  # 54,000x faster!
```

**Typical Performance:**

- First query: 1-2 seconds  
- Cached queries: <0.1 seconds
- Speedup: Up to 54,000x for complex queries

## Monitoring Cache Performance

```python
import vfbquery as vfb

# Get cache statistics
stats = vfb.get_vfbquery_cache_stats()
print(f"Hit rate: {stats['hit_rate_percent']}%")
print(f"Memory used: {stats['memory_cache_size_mb']}MB")
print(f"Cache items: {stats['memory_cache_items']}")

# Get current configuration
config = vfb.get_cache_config()
print(f"TTL: {config['cache_ttl_hours']} hours")
print(f"Memory limit: {config['memory_cache_size_mb']}MB")
```

## Usage Examples

### Production Applications

```python
import vfbquery as vfb

# Caching is enabled automatically with optimal defaults
# Adjust only if your application has specific needs

# Example: Long-running server with limited memory
vfb.set_cache_memory_limit(512)    # 512MB limit
vfb.set_cache_ttl(168)             # 1 week TTL
```

### Jupyter Notebooks

```python
import vfbquery as vfb

# Caching works automatically in notebooks
# Data persists between kernel restarts

result = vfb.get_term_info('FBbt_00003748')     # Fast on repeated runs
instances = vfb.get_instances('FBbt_00003748')  # Cached automatically
```

## Benefits

- **Dramatic Performance**: 54,000x speedup for repeated queries
- **Zero Configuration**: Works out of the box with optimal settings
- **Persistent Storage**: Cache survives Python restarts  
- **Memory Efficient**: LRU eviction prevents memory bloat
- **Multi-layer Caching**: Optimizes SOLR queries, parsing, and results
- **Production Ready**: 3-month TTL matches VFB_connect behavior

## Best Practices

- **Monitor performance**: Use `get_vfbquery_cache_stats()` regularly
- **Adjust for your use case**: Tune memory limits for long-running applications  
- **Consider data freshness**: Shorter TTL for frequently changing data
- **Disable when needed**: Use environment variable if caching isn't desired
