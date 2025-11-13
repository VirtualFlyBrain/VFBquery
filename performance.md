# VFBquery Performance Test Results

**Test Date:** 2025-11-13 03:10:28 UTC
**Git Commit:** 1040f305f9e0cc94d644ce26e82df68e00c7f079
**Branch:** main
**Workflow Run:** [19319202253](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19319202253)

## Test Overview

This performance test measures the execution time of all implemented VFB queries including:

### Core Queries
- **Term Info Queries**: Basic term information retrieval
- **Neuron Part Queries**: Neurons with parts overlapping regions
- **Synaptic Terminal Queries**: Pre/post synaptic terminals
- **Anatomical Hierarchy**: Components, parts, subclasses
- **Instance Queries**: Available images and instances

### New Queries (2025)
- **NeuronClassesFasciculatingHere**: Neurons fasciculating with tracts
- **TractsNervesInnervatingHere**: Tracts/nerves innervating neuropils
- **LineageClonesIn**: Lineage clones in neuropils

## Performance Thresholds

- **Fast queries**: < 1 second (SOLR lookups)
- **Medium queries**: < 3 seconds (Owlery + SOLR)
- **Slow queries**: < 10 seconds (Neo4j + complex processing)

## Test Results

```
test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance ... FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ok
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ok
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... ok
test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries ... ok
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 94, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
AssertionError: 12.69656229019165 not less than 3.0 : term_info query exceeded threshold

----------------------------------------------------------------------
Ran 6 tests in 25.246s

FAILED (failures=1)
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

================================================================================
TERM INFO QUERIES
================================================================================
DEBUG: Cache lookup for FBbt_00003748: MISS
get_term_info (mushroom body): 12.6966s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.1397s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.4513s ✅
NeuronsPresynapticHere: 0.9791s ✅
NeuronsPostsynapticHere: 1.1147s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 0.9237s ✅
PartsOf: 0.9482s ✅
SubclassesOf: 0.9327s ✅

================================================================================
NEW QUERIES (2025)
================================================================================
NeuronClassesFasciculatingHere: 1.2333s ✅
TractsNervesInnervatingHere: 0.9584s ✅
LineageClonesIn: 0.9776s ✅
ImagesNeurons: 0.9519s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.9373s ✅

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.096s

OK
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.1483 seconds
VFB_00101567 query took: 0.9475 seconds
Total time for both queries: 2.0958 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2025-11-13 03:10:28 UTC*
