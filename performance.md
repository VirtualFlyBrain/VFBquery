# VFBquery Performance Test Results

**Test Date:** 2026-02-03 04:09:44 UTC
**Git Commit:** 8906834a5787f2d593938416041fcc3397ef18b2
**Branch:** main
**Workflow Run:** [21616566648](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/21616566648)

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
Test image and developmental lineage queries ... INFO: Owlery query returned 400 Bad Request (invalid for this term type): <http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/FBtp0000001>
ok
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
Ran 15 tests in 76.376s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 2.5632s ✅
get_term_info (individual): 2.8165s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 2.4637s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.4481s ✅
NeuronsPresynapticHere: 2.2445s ✅
NeuronsPostsynapticHere: 2.3797s ✅
NeuronNeuronConnectivity: 2.0033s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.9015s ✅
PartsOf: 1.8868s ✅
SubclassesOf: 2.0236s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 1.8911s ✅
TractsNervesInnervatingHere: 1.8983s ✅
LineageClonesIn: 1.8984s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.2078s ✅
ImagesThatDevelopFrom: 9.1684s ✅
ERROR: Owlery instances request failed: 400 Client Error: Bad Request for url: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBtp0000001%3E&direct=false&includeDeprecated=false
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBtp0000001%3E&direct=false&includeDeprecated=false
epFrag: 5.5367s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.9267s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.9060s ✅
NeuronRegionConnectivityQuery: 1.8756s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 1.1075s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 4.5545s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 2.1688s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 1.0012s ✅
  └─ Found 0 total clusters
clusterExpression: 1.0503s ✅
  └─ Found 0 genes expressed
expressionCluster: 0.7539s ✅
  └─ Found 0 clusters expressing gene
scRNAdatasetData: 0.9218s ✅
  └─ Found 0 clusters in dataset

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 2.6130s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.8968s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.7322s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.8312s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.7315s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.7476s ✅
  └─ Found 0 painted domains
DatasetImages: 0.9057s ✅
  └─ Found 0 images in dataset
AllAlignedImages: 0.7199s ✅
  └─ Found 0 aligned images
AlignedDatasets: 1.0457s ✅
  └─ Found 0 aligned datasets
AllDatasets: 0.9588s ✅
  └─ Found 116 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 1.6021s ✅
  └─ Found 0 terms for publication
TransgeneExpressionHere: 0.9890s ✅
  └─ Found 2346 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 4.165s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 2.2582 seconds
VFB_00101567 query took: 1.9065 seconds
Total time for both queries: 4.1646 seconds
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
*Last updated: 2026-02-03 04:09:44 UTC*
