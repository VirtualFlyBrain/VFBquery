# VFBquery Performance Test Results

**Test Date:** 2026-03-18 04:19:01 UTC
**Git Commit:** beba3eb5703dab6f33f00c45134a31a0bc982585
**Branch:** main
**Workflow Run:** [23228816254](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/23228816254)

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
AssertionError: 4.078628063201904 not less than 3.0 : AllAlignedImages exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 134.483s

FAILED (failures=1)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 2.5807s ✅
get_term_info (individual): 2.4825s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 2.5936s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.6601s ✅
NeuronsPresynapticHere: 2.1237s ✅
NeuronsPostsynapticHere: 2.5381s ✅
NeuronNeuronConnectivity: 1.9596s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 2.2380s ✅
PartsOf: 1.9231s ✅
SubclassesOf: 1.9032s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.9427s ✅
TractsNervesInnervatingHere: 1.9139s ✅
LineageClonesIn: 2.0148s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.4091s ✅
ImagesThatDevelopFrom: 1.9587s ✅
epFrag: 1.9462s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 2.0690s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.9652s ✅
NeuronRegionConnectivityQuery: 1.9178s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 1.0073s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 4.1550s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.3318s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 1.0053s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 41.9593s ✅
  └─ Found 4588 genes expressed, returned 10
clusterExpression: Skipped (test data may not exist): 41.959288120269775 not less than 15.0 : clusterExpression exceeded threshold
expressionCluster: 1.0983s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 1.7973s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 4.5870s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.7982s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 1.0646s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 1.1240s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 1.0199s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.9789s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.9180s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 4.0786s ✅
  └─ Found 465165 aligned images, returned 10

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.9604s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 6.6195s ✅
  └─ Found 2338 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 3.911s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.9489 seconds
VFB_00101567 query took: 1.9618 seconds
Total time for both queries: 3.9107 seconds
Performance Level: 🟠 Acceptable (3-6 seconds)
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
*Last updated: 2026-03-18 04:19:01 UTC*
