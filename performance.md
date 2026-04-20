# VFBquery Performance Test Results

**Test Date:** 2026-04-20 04:54:23 UTC
**Git Commit:** c24d81f527f3a010c7c0ddbf195fffd4ea462adb
**Branch:** main
**Workflow Run:** [24649050608](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/24649050608)

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
Test dataset and template queries ... ok
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

----------------------------------------------------------------------
Ran 15 tests in 81.437s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 2.8540s ✅
get_term_info (individual): 2.2556s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 2.7242s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.7335s ✅
NeuronsPresynapticHere: 1.8843s ✅
NeuronsPostsynapticHere: 2.5005s ✅
NeuronNeuronConnectivity: 1.9508s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.8332s ✅
PartsOf: 1.8378s ✅
SubclassesOf: 1.8280s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.8239s ✅
TractsNervesInnervatingHere: 1.8240s ✅
LineageClonesIn: 1.8333s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.1485s ✅
ImagesThatDevelopFrom: 1.9642s ✅
epFrag: 1.8993s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.8257s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.8244s ✅
NeuronRegionConnectivityQuery: 1.8050s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 1.0739s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 2.9839s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.2990s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.9263s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 3.1286s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 0.8000s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.9230s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.9286s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.8780s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.7274s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.7151s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.8977s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.9206s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.7795s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 2.3525s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 0.9120s ✅
  └─ Found 72 aligned datasets, returned 10
AllDatasets: 0.9257s ✅
  └─ Found 130 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.9114s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 2.3878s ✅
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
Ran 1 test in 3.714s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.8479 seconds
VFB_00101567 query took: 1.8661 seconds
Total time for both queries: 3.7141 seconds
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
*Last updated: 2026-04-20 04:54:23 UTC*
