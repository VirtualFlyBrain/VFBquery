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

## Cache coverage (v1.19.0)

As of v1.19.0 every query-result function reachable from the HA API handlers
(`ha_api.py`) is served by the persistent SOLR cache, except a small set that
are deliberately excluded (see below). Coverage is verified by a static sweep
that traces each handler entry point through the `QUERY_TYPE_MAP` dispatch and
the FlyBase/connectivity/hierarchy handlers — see `coverage_sweep.py`.

Caching is applied in one of two layers, both of which the handler path goes
through (`handler -> vfbquery.<fn> (patched to *_cached) -> _original`):

- `@with_solr_cache('<bucket>')` on the original in `vfb_queries.py` (most
  hierarchy / neuron-in-region / connectivity / image queries), or
- `@with_solr_cache('<bucket>')` on the `*_cached` wrapper in
  `cached_functions.py` (term_info, similarity, transcriptomics, datasets).

A function counts as cached if either layer carries the decorator; do not add
the decorator at both layers for the same function (double round-trips).

New buckets added in v1.19.0: `cluster_expression`, `expression_cluster`,
`scrnaseq_dataset_data`, `individual_neuron_inputs`, `similar_morphology`,
`similar_morphology_part_of`, `similar_morphology_part_of_exp`,
`similar_morphology_nb`, `similar_morphology_nb_exp`, `dataset_images`,
`all_aligned_images`, `all_datasets`, `transgene_expression_here`,
`related_anatomy`. The five genuinely new buckets (`dataset_images`,
`all_aligned_images`, `all_datasets`, `transgene_expression_here`,
`related_anatomy`) are also listed in the wrapper's `expensive_query_types`
and `dataframe_query_types`, so a limited request computes the full result
once, caches it, and serves later limited requests by slicing the cached full
result.

### Cross-dataset connectivity (`query_connectivity`)

`query_connectivity` takes five parameters (`upstream_type`,
`downstream_type`, `weight`, `group_by_class`, `exclude_dbs`), so the default
single-id `@with_solr_cache` key does not fit. It is persisted directly in
`vfb_connectivity.py` under a composite key
(`query_connectivity:{upstream}:{downstream}:{weight}:{group_by_class}:{exclude_dbs}`,
hashed for a Solr-safe document id). The in-memory `ResultCache` and request
coalescer in `ha_api.py` sit in front; this SOLR layer sits behind so a cold
miss survives restarts and reaches the other containers. Graph
post-processing (`post_fn`) stays in the handler and is never part of the
cached payload. `force_refresh=true` on `/query_connectivity` drops both the
in-memory entry and the SOLR document and recomputes.

### Deliberately not cached

- `get_similar_morphology_userdata` — keyed on a per-session user upload id;
  the result is user/session-specific, so it is left to the in-memory L1
  cache only.
- `get_flybase_stocks`, `get_flybase_combo_pubs`, `find_stocks`,
  `find_combo_publications` — backed by the FlyBase RDBMS, not Neo4j/Owlery;
  out of scope for this offload.
- `resolve_entity`, `resolve_combination` — thin resolvers over the already
  cached `term_info`.
- `list_connectome_datasets` — tiny static list; L1 cache is sufficient.
- `get_hierarchy` — delegates its heavy work to the SOLR-cached
  `get_parts_of` / `get_subclasses_of` and relies on Owlery's own
  server-side cache, with the handler holding an in-memory composite-key
  entry; persistent composite caching is a sensible follow-up but was left
  out to keep this change focused.

### Cache server

The cache reads and writes `cache_url`, which defaults to the dedicated
query-cache Solr:

```
http://vfbquerycache.virtualflybrain.org:80/solr/vfb_json
```

(`SolrResultCache.DEFAULT_CACHE_URL`). This is a separate, lightly-loaded host
from the ontology Solr (`solr.virtualflybrain.org`); it is reached on port 80
because the Solr native port is firewalled externally. Override with the
`VFBQUERY_SOLR_URL` environment variable (e.g. to point at a staging core for
testing):

```bash
export VFBQUERY_SOLR_URL=http://localhost:8983/solr/vfb_json
```

Note: data reads in `vfb_queries.py` (term_info, painted domains, ontology
label lookups, etc.) still go to `solr.virtualflybrain.org` — only the result
*cache* moved. The two are independent.

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

# Similarity queries are also cached
similar = vfb.get_similar_neurons('VFB_jrchk00s')  # Cached after first run
```

**Typical Performance:**

- First query: 1-2 seconds  
- Cached queries: <0.1 seconds
- Speedup: Up to 54,000x for complex queries
- **NBLAST similarity queries**: 10+ seconds → <0.1 seconds (cached)

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
- **Similarity Queries**: NBLAST and morphological similarity searches are cached
- **Production Ready**: 3-month TTL matches VFB_connect behavior

## Best Practices

- **Monitor performance**: Use SOLR cache statistics regularly
- **Clear when needed**: Use `clear_solr_cache()` to force fresh data
- **Consider data freshness**: SOLR cache TTL ensures data doesn't become stale
- **Disable when needed**: Use environment variable if caching isn't desired
