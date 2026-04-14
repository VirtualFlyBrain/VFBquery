# VFBquery Performance Test Results

**Test Date:** 2026-04-14 06:39:58 UTC
**Git Commit:** 6ae5c88938306dce73cc56b5c7632303139e33be
**Branch:** main
**Workflow Run:** [24383947348](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/24383947348)

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
Test term info query performance ... FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... WARNING: Owlery unavailable for query '<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00007401>': ConnectionError
FAIL
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
Test dataset and template queries ... ok
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 113, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "term_info query exceeded threshold")
AssertionError: 311.5026309490204 not less than 31.0 : term_info query exceeded threshold

======================================================================
FAIL: test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 139, in test_02_neuron_part_queries
    self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "NeuronsPartHere exceeded threshold")
AssertionError: 1169.273244380951 not less than 31.0 : NeuronsPartHere exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 1552.404s

FAILED (failures=2)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
Unexpected error when retrieving term info: SolrError: Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/?q=id%3AFBbt_00003748&wt=json' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Max retries exceeded with url: /solr/vfb_json/select/?q=id%3AFBbt_00003748&wt=json (Caused by ConnectTimeoutError(<HTTPConnection(host='solr.virtualflybrain.org', port=80) at 0x7fd29c309060>, 'Connection to solr.virtualflybrain.org timed out. (connect timeout=990)'))
get_term_info (mushroom body): 311.5026s ❌

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1169.2732s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 3.0193s ✅
NeuronsPresynapticHere: 2.0546s ✅
NeuronsPostsynapticHere: 2.4114s ✅
NeuronNeuronConnectivity: 1.9588s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 2.1771s ✅
PartsOf: 1.8573s ✅
SubclassesOf: 2.0468s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.8180s ✅
TractsNervesInnervatingHere: 1.8437s ✅
LineageClonesIn: 1.8150s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.0737s ✅
ImagesThatDevelopFrom: 1.8631s ✅
epFrag: 1.8210s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.8193s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.8044s ✅
NeuronRegionConnectivityQuery: 1.8200s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 0.9384s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.4163s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.2905s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.9720s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 1.0475s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 0.9985s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 1.1145s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.1233s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.7119s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.7100s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.7262s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.6873s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.9587s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.7855s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 2.8056s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 0.9123s ✅
  └─ Found 72 aligned datasets, returned 10
AllDatasets: 0.9729s ✅
  └─ Found 130 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.9413s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 1.9278s ✅
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
Ran 1 test in 3.660s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.8590 seconds
VFB_00101567 query took: 1.8012 seconds
Total time for both queries: 3.6602 seconds
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
*Last updated: 2026-04-14 06:39:58 UTC*
