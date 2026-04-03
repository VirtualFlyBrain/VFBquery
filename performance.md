# VFBquery Performance Test Results

**Test Date:** 2026-04-03 04:25:44 UTC
**Git Commit:** 9efd0255d47f3be41eeaea807d06a1c3737154ef
**Branch:** main
**Workflow Run:** [23933675248](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/23933675248)

## Test Overview

This performance test measures the execution time of all implemented VFB queries organized by functionality:

### 1. Term Information Queries

- **Term Info**: Comprehensive term information retrieval with preview data

### 2. Neuron Part & Synaptic Queries

- **NeuronsPartHere**: Neurons with parts overlapping anatomical regions
- **NeuronsSynaptic**: Neurons with synapses in a region
- **NeuronsPresynapticHere**: Neurons with presynaptic terminals in a region
- **NeuronsPostsynapticHere**: Neurons with postsynaptic terminals in a region

### 3. Anatomical Hierarchy Queries

- **ComponentsOf**: Anatomical components of a structure
- **PartsOf**: Parts of an anatomical structure
- **SubclassesOf**: Subclasses of anatomical terms (can be very slow for complex terms)

### 4. Tract/Nerve & Lineage Queries

- **NeuronClassesFasciculatingHere**: Neurons fasciculating with tracts
- **TractsNervesInnervatingHere**: Tracts/nerves innervating neuropils
- **LineageClonesIn**: Lineage clones in neuropils (complex OWL reasoning)

### 5. Image & Developmental Queries

- **ImagesNeurons**: Neuron images in anatomical regions
- **ImagesThatDevelopFrom**: Developmental lineage images
- **epFrag**: Expression pattern fragments
- **ListAllAvailableImages**: All available images for a term

### 6. Connectivity Queries

- **NeuronNeuronConnectivity**: Neuron-to-neuron connectivity
- **NeuronRegionConnectivity**: Neuron-to-region connectivity
- **NeuronInputsTo**: Individual neuron inputs

### 7. Similarity Queries (NBLAST & NeuronBridge)

- **SimilarMorphologyTo**: NBLAST morphological similarity
- **SimilarMorphologyToPartOf**: NBLAST to expression patterns (NBLASTexp)
- **SimilarMorphologyToPartOfexp**: Reverse NBLASTexp
- **SimilarMorphologyToNB**: NeuronBridge matches
- **SimilarMorphologyToNBexp**: NeuronBridge for expression patterns

### 8. Expression & Transcriptomics Queries

- **ExpressionOverlapsHere**: Expression patterns overlapping regions
- **anatScRNAseqQuery**: scRNAseq clusters in anatomy
- **clusterExpression**: Genes expressed in clusters
- **expressionCluster**: Clusters expressing genes
- **scRNAdatasetData**: Cluster data from scRNAseq datasets

### 9. Dataset & Template Queries

- **PaintedDomains**: Template painted anatomy domains
- **DatasetImages**: Images in datasets
- **AllAlignedImages**: Images aligned to templates
- **AlignedDatasets**: Datasets aligned to templates
- **AllDatasets**: All available datasets

### 10. Publication & Transgene Queries

- **TermsForPub**: Terms referencing publications
- **TransgeneExpressionHere**: Transgene expression patterns in regions

## Performance Thresholds

- **Fast queries**: < 1 second (SOLR lookups)
- **Medium queries**: < 3 seconds (Owlery + SOLR)
- **Slow queries**: < 10 seconds (Neo4j + complex processing)
- **Very Slow queries**: < 31 seconds (Complex OWL reasoning - over 30 seconds)

## Test Results

```
test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance ... ok
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ok
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ok
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... ok
test_05_tract_lineage_queries (src.test.test_query_performance.QueryPerformanceTest)
Test tract/nerve and lineage clone queries ... ok
test_05b_image_queries (src.test.test_query_performance.QueryPerformanceTest)
Test image and developmental lineage queries ... ok
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok
test_07_connectivity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron connectivity queries ... ok
test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_09_neuron_input_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron input/synapse queries ... ok
test_10_expression_queries (src.test.test_query_performance.QueryPerformanceTest)
Test expression pattern queries ... ok
test_11_transcriptomics_queries (src.test.test_query_performance.QueryPerformanceTest)
Test scRNAseq transcriptomics queries ... ok
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... FAIL
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

======================================================================
FAIL: test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 660, in test_13_dataset_template_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "AllAlignedImages exceeded threshold")
AssertionError: 7.344918489456177 not less than 3.0 : AllAlignedImages exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 102.413s

FAILED (failures=1)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 2.7069s ✅
get_term_info (individual): 1.5735s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.9524s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.0559s ✅
NeuronsPresynapticHere: 1.5464s ✅
NeuronsPostsynapticHere: 2.1134s ✅
NeuronNeuronConnectivity: 1.6915s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.4132s ✅
PartsOf: 1.3266s ✅
SubclassesOf: 1.7995s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.8721s ✅
TractsNervesInnervatingHere: 1.3115s ✅
LineageClonesIn: 1.2788s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 2.2705s ✅
ImagesThatDevelopFrom: 1.3577s ✅
epFrag: 1.2966s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.2923s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.3184s ✅
NeuronRegionConnectivityQuery: 1.6823s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 1.2470s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 2.6948s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 0.9843s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.6444s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 26.5485s ✅
  └─ Found 4588 genes expressed, returned 10
clusterExpression: Skipped (test data may not exist): 26.548524856567383 not less than 15.0 : clusterExpression exceeded threshold
expressionCluster: 0.7016s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.5767s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 0.9788s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 1.1983s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.7849s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.7177s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.7245s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.6367s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.8108s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 7.3449s ✅
  └─ Found 527179 aligned images, returned 10

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.6251s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 2.3200s ✅
  └─ Found 2340 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.580s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.2850 seconds
VFB_00101567 query took: 1.2947 seconds
Total time for both queries: 2.5797 seconds
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
*Last updated: 2026-04-03 04:25:44 UTC*
