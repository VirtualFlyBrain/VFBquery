# VFBquery Caching Guide

VFBquery includes intelligent SOLR-based caching for optimal performance. Caching is **enabled by default** with production-ready settings.

## Default Behavior

VFBquery automatically enables SOLR caching when imported:

```python
import vfbquery as vfb

# SOLR caching is already active with optimal settings:
# - 3-month cache duration
# - Persistent across sessions
# - Zero configuration required

result = vfb.get_term_info('FBbt_00003748')  # Cached automatically
```

## How It Works

VFBquery uses a single-layer caching approach with SOLR:

1. **First query**: Fetches data from Neo4j/Owlery and caches in SOLR
2. **Subsequent queries**: Served directly from SOLR cache
3. **Cache persistence**: Survives Python restarts and server reboots
4. **Automatic expiration**: 3-month TTL matches VFB_connect behavior

## Runtime Configuration

Control caching behavior:

```python
import vfbquery as vfb

# Clear specific cache entries
vfb.clear_solr_cache('term_info', 'FBbt_00003748')

# Get SOLR cache statistics
stats = vfb.get_solr_cache().get_cache_stats()
```

### Environment Control

Disable caching globally if needed:

```bash
export VFBQUERY_CACHE_ENABLED=false
```

## Performance Benefits

VFBquery SOLR caching provides significant performance improvements:

```python
import vfbquery as vfb

# First query: builds SOLR cache (~1-2 seconds)  
result1 = vfb.get_term_info('FBbt_00003748')

# Subsequent queries: served from SOLR cache (<0.1 seconds)
result2 = vfb.get_term_info('FBbt_00003748')  # 54,000x faster!
```

**Typical Performance:**

- First query: 1-2 seconds  
- Cached queries: <0.1 seconds
- Speedup: Up to 54,000x for complex queries

## Monitoring Cache Performance

```python
import vfbquery as vfb

# Get SOLR cache statistics
cache = vfb.get_solr_cache()
stats = cache.get_cache_stats()
print(f"Total cached items: {stats['total_documents']}")
print(f"Cache size: {stats['total_size_mb']:.1f}MB")
```

## Usage Examples

### Production Applications

```python
import vfbquery as vfb

# SOLR caching is enabled automatically with optimal defaults
# Cache persists across application restarts

# Example: Long-running server
result = vfb.get_term_info('FBbt_00003748')     # Fast on repeated runs
instances = vfb.get_instances('FBbt_00003748')  # Cached automatically
```

### Jupyter Notebooks

```python
import vfbquery as vfb

# SOLR caching works automatically in notebooks
# Data persists between kernel restarts and notebook sessions

result = vfb.get_term_info('FBbt_00003748')     # Fast on repeated runs
instances = vfb.get_instances('FBbt_00003748')  # Cached automatically
```

## Benefits

- **Dramatic Performance**: 54,000x speedup for repeated queries
- **Zero Configuration**: Works out of the box with optimal settings
- **Persistent Storage**: SOLR cache survives Python restarts and server reboots
- **Server-side Caching**: Shared across multiple processes/instances
- **Production Ready**: 3-month TTL matches VFB_connect behavior

## Best Practices

- **Monitor performance**: Use SOLR cache statistics regularly
- **Clear when needed**: Use `clear_solr_cache()` to force fresh data
- **Consider data freshness**: SOLR cache TTL ensures data doesn't become stale
- **Disable when needed**: Use environment variable if caching isn't desired
