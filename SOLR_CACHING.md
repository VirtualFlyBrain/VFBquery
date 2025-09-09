# SOLR-Based Result Caching for VFBquery

This document describes an **experimental approach** to eliminate cold start delays by storing pre-computed VFBquery results directly in a SOLR collection, enabling instant retrieval without expensive Neo4j queries and data processing.

## The Cold Start Problem

Current VFBquery performance shows:
- **Cold start**: 155+ seconds for complex queries like `FBbt_00003748` 
- **Warm cache**: <0.1 seconds (54,000x faster with local caching)

The bottleneck occurs during:
1. Neo4j graph traversal for relationships and instances
2. Complex data processing in `fill_query_results()`  
3. VFB_connect lookup cache initialization (125+ seconds)

## SOLR Cache Solution

### Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   VFBquery      │    │  SOLR Cache      │    │  Original       │
│   Function      │───▶│  Collection      │───▶│  Neo4j Query    │
│                 │    │  (vfbquery_cache)│    │  (if cache miss)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │              ┌─────────▼─────────┐              │
         └──────────────│  Cached Result    │◀─────────────┘
                        │  (Instant Return) │
                        └───────────────────┘
```

### Key Benefits

1. **Instant Cold Starts**: Pre-computed results available immediately
2. **Server-Side Caching**: Results shared across all users/instances
3. **Persistent Storage**: Survives deployments and system restarts  
4. **Scalable**: SOLR's distributed architecture handles large datasets
5. **Analytics**: Track cache hit rates and popular queries

## Implementation

### Basic Usage

```python
import vfbquery as vfb

# Enable SOLR result caching (experimental)
vfb.enable_solr_result_caching()

# First call: Computes result and stores in SOLR cache
result1 = vfb.get_term_info('FBbt_00003748')  # ~155s + cache storage

# Subsequent calls: Retrieved instantly from SOLR
result2 = vfb.get_term_info('FBbt_00003748')  # <0.1s (cache hit)

# Works for any user/instance/deployment
result3 = vfb.get_term_info('FBbt_00003748')  # Still <0.1s
```

### Cache Warming

Pre-populate cache during deployment or maintenance windows:

```python
import vfbquery as vfb

# Common anatomical terms that benefit from caching
popular_terms = [
    'FBbt_00003748',  # medulla  
    'FBbt_00007401',  # mushroom body
    'FBbt_00003679',  # optic lobe
    'FBbt_00100313',  # brain
    # ... more frequently queried terms
]

# Warm up cache for these terms
vfb.warmup_solr_cache(
    term_ids=popular_terms,
    query_types=['term_info', 'instances']
)
```

### Cache Management

```python
# Get cache statistics
stats = vfb.get_solr_cache_stats()
print(f"Total cached results: {stats['total_entries']}")
print(f"Cache hit rate: {stats['total_hits']}")
print(f"Cache size: {stats['cache_size_mb']:.2f} MB")

# Clean up expired entries
deleted = vfb.cleanup_solr_cache()
print(f"Cleaned up {deleted} expired entries")

# Disable when not needed
vfb.disable_solr_result_caching()
```

## SOLR Collection Schema

The cache uses a dedicated SOLR collection with this schema:

```xml
<field name="id" type="string" indexed="true" stored="true" required="true"/>
<field name="query_type" type="string" indexed="true" stored="true"/>
<field name="term_id" type="string" indexed="true" stored="true"/>
<field name="query_params" type="string" indexed="true" stored="true"/>
<field name="result_json" type="text_general" indexed="false" stored="true"/>
<field name="created_at" type="pdate" indexed="true" stored="true"/>
<field name="expires_at" type="pdate" indexed="true" stored="true"/>
<field name="result_size" type="plong" indexed="true" stored="true"/>
<field name="version" type="string" indexed="true" stored="true"/>
<field name="hit_count" type="plong" indexed="true" stored="true"/>
```

### Cache Key Generation

Cache keys are generated deterministically:
```
{query_type}_{term_id}_{params_hash}
```

Examples:
- `term_info_FBbt_00003748_a1b2c3d4` (term info with specific parameters)
- `instances_FBbt_00003748_e5f6g7h8` (instances with limit/dataframe options)

## Configuration

### Default Settings

```python
# Cache configuration
CACHE_URL = "https://solr.virtualflybrain.org/solr/vfbquery_cache"
TTL_HOURS = 2160  # 3 months (same as VFB_connect)
MAX_RESULT_SIZE_MB = 10  # Don't cache results > 10MB
```

### Environment Variables

```bash
# Enable/disable SOLR caching
export VFBQUERY_SOLR_CACHE_ENABLED=true

# Custom SOLR cache collection URL
export VFBQUERY_SOLR_CACHE_URL="https://custom.solr.server/cache"

# Cache TTL in hours
export VFBQUERY_SOLR_CACHE_TTL=720  # 1 month
```

## Deployment Strategy

### Phase 1: Proof of Concept
1. **Create SOLR collection** with cache schema
2. **Test with sample terms** to verify performance gains
3. **Measure cache hit rates** and storage requirements

### Phase 2: Selective Caching
1. **Identify high-value terms** (slow queries, frequent requests)
2. **Implement cache warming** for these terms
3. **Monitor performance impact** and adjust as needed

### Phase 3: Full Deployment
1. **Enable by default** for production systems
2. **Automated cache warming** during deployments
3. **Cache analytics dashboard** for monitoring

## Performance Projections

Based on current performance data:

| Scenario | Current Time | With SOLR Cache | Improvement |
|----------|--------------|-----------------|-------------|
| Cold start (FBbt_00003748) | 155.0s | <0.1s | **1,550x** |
| Complex anatomy queries | 60-180s | <0.1s | **600-1,800x** |
| Popular terms (warm) | <0.1s | <0.1s | Same |

### Storage Requirements

Estimated storage per cached result:
- **Simple terms**: 5-50 KB
- **Complex anatomical classes**: 100-500 KB  
- **Large instance queries**: 1-10 MB

For 1,000 popular terms: ~500 MB total cache size

## Fallback Strategy

The implementation includes robust fallback:

1. **SOLR cache lookup** (timeout: 5s)
2. **If cache miss/timeout**: Execute original Neo4j query
3. **Store result** in SOLR cache for future use
4. **Graceful degradation**: System works normally if SOLR unavailable

## Integration with Existing Caching

SOLR caching complements existing memory/disk caching:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Request   │───▶│   Memory    │───▶│    SOLR     │───▶│   Neo4j     │
│             │    │   Cache     │    │   Cache     │    │   Query     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                   │                 │                   │
       └───────────────────┼─────────────────┼───────────────────┘
                           │                 │
                     ┌─────▼─────┐    ┌─────▼─────┐
                     │  Instant  │    │  Instant  │
                     │  Return   │    │  Return   │
                     │  (<1ms)   │    │ (~50ms)   │
                     └───────────┘    └───────────┘
```

**Cache Hierarchy:**
1. **Memory cache**: Fastest (<1ms), per-instance
2. **SOLR cache**: Fast (~50ms), shared across instances
3. **Neo4j computation**: Slow (60-180s), only when necessary

## Security Considerations

- **Public cache**: Results stored in shared SOLR collection
- **No sensitive data**: Only public VFB anatomical data
- **Query parameter hashing**: Prevents cache key manipulation
- **TTL enforcement**: Automatic expiration prevents stale data

## Monitoring and Analytics

### Cache Metrics
- **Hit rate percentage**: Measure cache effectiveness
- **Average response time**: Track performance improvements  
- **Storage usage**: Monitor cache size growth
- **Popular terms**: Identify candidates for pre-warming

### Example Dashboard Queries
```sql
-- Most cached query types
SELECT query_type, COUNT(*) FROM vfbquery_cache GROUP BY query_type

-- Cache hit leaders  
SELECT term_id, hit_count FROM vfbquery_cache ORDER BY hit_count DESC LIMIT 10

-- Cache size by term
SELECT term_id, result_size/1024 as size_kb FROM vfbquery_cache ORDER BY result_size DESC
```

## Future Enhancements

1. **Smart pre-warming**: ML-based prediction of terms to cache
2. **Compression**: Reduce storage requirements with result compression
3. **Versioning**: Handle VFB data updates with cache invalidation
4. **Regional caching**: Geo-distributed SOLR for global performance
5. **Cache warming API**: Allow external systems to request pre-computation

## Implementation Notes

- **Atomic operations**: Use SOLR's optimistic locking for concurrent updates
- **Batch operations**: Efficient bulk cache warming and cleanup
- **Error handling**: Comprehensive fallback to ensure reliability  
- **Logging**: Detailed metrics for performance analysis
- **Testing**: Mock SOLR server for unit tests

This SOLR-based approach represents a paradigm shift from client-side to server-side caching, potentially eliminating the cold start problem entirely for VFBquery users.
