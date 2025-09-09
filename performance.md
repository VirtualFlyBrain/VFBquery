# VFBquery Performance Analysis

**Analysis Date:** 2025-09-09
**Git Commit:** 72c602f15edbf366806cf74524ae1c931f15a1ed
**Branch:** dev

## Executive Summary

**Root Cause Identified:** The 125-second delay for FBbt_00003748 queries is caused by VFB_connect's **lookup cache initialization** on cold start, not by the actual query processing.

## Test Overview

This performance test measures the execution time of VFB term info queries for specific terms:

- **FBbt_00003748**: medulla (anatomical class) - experiences cold start cache initialization
- **VFB_00101567**: individual anatomy data - benefits from warm cache

## Performance Analysis

### Cold Start vs Warm Cache Performance

| Scenario | FBbt_00003748 | VFB_00101567 | Notes |
|----------|---------------|---------------|--------|
| **Cold Start** (no cache) | 126.84s | ~125s | Initial lookup cache build |
| **Warm Cache** (cached) | 0.54s | 0.16s | Subsequent runs with cache |
| **Performance Test** | 125.07s | 0.16s | Matches cold start pattern |

### Root Cause Analysis

The 125-second delay is **NOT** a performance regression but rather VFB_connect's lookup cache initialization:

1. **Cache Purpose**: VFB_connect builds a complete lookup table of all terms (classes, individuals, properties) for faster subsequent queries
2. **Cache Location**: `~/.venv/lib/python3.10/site-packages/vfb_connect/lookup_cache.pkl`  
3. **Cache Validity**: 3 months (automatically rebuilds when stale)
4. **Trigger**: First query after cache expiry or in clean environment

### Performance Breakdown

The actual query components are fast:

- **SOLR term lookup**: ~0.08s
- **Term info parsing**: ~0.05s  
- **get_instances query**: ~1.4s
- **Results processing**: ~0.4s

**Total actual processing time**: ~2s (vs 126s cache build)

### Optimizations Available in VFB_connect

VFB_connect (since 2024-08-16) includes several caching optimizations:

1. **VFBTerm Object Cache**: Enable with `vfb._use_cache = True`
2. **Environment Control**: Set `VFB_CACHE_ENABLED=true` in CI
3. **Manual Cache Management**: Use `vfb.reload_lookup_cache()` for fresh data
4. **Timestamp-based Invalidation**: Automatic 3-month cache expiry

## Recommendations

### For Development

- **Accept the cold start cost** - it's a one-time initialization per environment
- **Use warm cache** for repeated development/testing
- **Enable VFBTerm caching** with `vfb._use_cache = True` for repeated queries

### For Production/CI

- **Pre-warm cache** in deployment scripts
- **Set `VFB_CACHE_ENABLED=true`** in environment
- **Monitor cache age** and refresh periodically
- **Consider cache persistence** across deployments

### Performance Thresholds

- Maximum single query time: 5 minutes (300 seconds) ✅
- Maximum total time for both queries: 7.5 minutes (450 seconds) ✅

**Status**: Current performance is within acceptable thresholds for cold start scenarios.

---
*Analysis completed: 2025-09-09*
*VFB_connect cache optimization introduced: 2024-08-16*
