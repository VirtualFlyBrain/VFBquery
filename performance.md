# VFBquery Performance Test Results

**Test Date:** 2025-11-18 22:32:22 UTC
**Git Commit:** 2f8c0234a43dc27765f37d0ba92f817cea449011
**Branch:** dev
**Workflow Run:** [19482607070](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19482607070)

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
Test scRNAseq transcriptomics queries ... VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
DEBUG: Checking cache for term_info, term_id=FBbt_00003748, cache_term_id=FBbt_00003748_preview_True, should_cache=True
DEBUG: Attempting cache lookup for term_info(FBbt_00003748_preview_True) with full results
DEBUG: Cache lookup result: True
get_term_info (mushroom body): 1.9760s ✅
DEBUG: Checking cache for term_info, term_id=VFB_00101567, cache_term_id=VFB_00101567_preview_True, should_cache=True
DEBUG: Attempting cache lookup for term_info(VFB_00101567_preview_True) with full results
DEBUG: Cache lookup result: True
get_term_info (individual): 1.7684s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
DEBUG: Checking cache for neurons_part_here, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for neurons_part_here(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
NeuronsPartHere: 1.4663s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
DEBUG: Checking cache for neurons_synaptic, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for neurons_synaptic(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
NeuronsSynaptic: 2.0687s ✅
DEBUG: Checking cache for neurons_presynaptic, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for neurons_presynaptic(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
NeuronsPresynapticHere: 1.5751s ✅
DEBUG: Checking cache for neurons_postsynaptic, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for neurons_postsynaptic(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
NeuronsPostsynapticHere: 1.3623s ✅
DEBUG: Checking cache for neuron_neuron_connectivity_query, term_id=VFB_jrchk00s, cache_term_id=VFB_jrchk00s, should_cache=True
DEBUG: Attempting cache lookup for neuron_neuron_connectivity_query(VFB_jrchk00s) with full results
DEBUG: Cache lookup result: True
NeuronNeuronConnectivity: 1.3721s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
DEBUG: Checking cache for components_of, term_id=FBbt_00003748, cache_term_id=FBbt_00003748, should_cache=True
DEBUG: Attempting cache lookup for components_of(FBbt_00003748) with full results
DEBUG: Cache lookup result: True
ComponentsOf: 1.3843s ✅
DEBUG: Checking cache for parts_of, term_id=FBbt_00003748, cache_term_id=FBbt_00003748, should_cache=True
DEBUG: Attempting cache lookup for parts_of(FBbt_00003748) with full results
DEBUG: Cache lookup result: True
PartsOf: 1.3647s ✅
DEBUG: Checking cache for subclasses_of, term_id=FBbt_00003748, cache_term_id=FBbt_00003748, should_cache=True
DEBUG: Attempting cache lookup for subclasses_of(FBbt_00003748) with full results
DEBUG: Cache lookup result: True
SubclassesOf: 1.3774s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
DEBUG: Checking cache for neuron_classes_fasciculating_here, term_id=FBbt_00003987, cache_term_id=FBbt_00003987, should_cache=True
DEBUG: Attempting cache lookup for neuron_classes_fasciculating_here(FBbt_00003987) with full results
DEBUG: Cache lookup result: True
NeuronClassesFasciculatingHere: 1.5887s ✅
DEBUG: Checking cache for tracts_nerves_innervating_here, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for tracts_nerves_innervating_here(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
TractsNervesInnervatingHere: 1.4295s ✅
DEBUG: Checking cache for lineage_clones_in, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for lineage_clones_in(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
LineageClonesIn: 1.3775s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
DEBUG: Checking cache for images_neurons, term_id=FBbt_00007401, cache_term_id=FBbt_00007401, should_cache=True
DEBUG: Attempting cache lookup for images_neurons(FBbt_00007401) with full results
DEBUG: Cache lookup result: True
ImagesNeurons: 1.3565s ✅
DEBUG: Checking cache for images_that_develop_from, term_id=FBbt_00001419, cache_term_id=FBbt_00001419, should_cache=True
DEBUG: Attempting cache lookup for images_that_develop_from(FBbt_00001419) with full results
DEBUG: Cache lookup result: True
ImagesThatDevelopFrom: 1.3787s ✅
DEBUG: Checking cache for expression_pattern_fragments, term_id=FBtp0000001, cache_term_id=FBtp0000001, should_cache=True
DEBUG: Attempting cache lookup for expression_pattern_fragments(FBtp0000001) with full results
DEBUG: Cache lookup result: True
epFrag: 1.3849s ✅

================================================================================
INSTANCE QUERIES
================================================================================
DEBUG: Checking cache for instances, term_id=FBbt_00003982, cache_term_id=FBbt_00003982, should_cache=True
DEBUG: Attempting cache lookup for instances(FBbt_00003982) with full results
DEBUG: Cache lookup result: True
ListAllAvailableImages: 1.3749s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
DEBUG: Checking cache for neuron_neuron_connectivity_query, term_id=VFB_jrchk00s, cache_term_id=VFB_jrchk00s, should_cache=True
DEBUG: Attempting cache lookup for neuron_neuron_connectivity_query(VFB_jrchk00s) with full results
DEBUG: Cache lookup result: True
NeuronNeuronConnectivityQuery: 1.3809s ✅
DEBUG: Checking cache for neuron_region_connectivity_query, term_id=VFB_jrchk00s, cache_term_id=VFB_jrchk00s, should_cache=True
DEBUG: Attempting cache lookup for neuron_region_connectivity_query(VFB_jrchk00s) with full results
DEBUG: Cache lookup result: True
NeuronRegionConnectivityQuery: 1.3842s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
DEBUG: Checking cache for similar_neurons, term_id=VFB_jrchk00s, cache_term_id=VFB_jrchk00s_score_NBLAST_score, should_cache=False
DEBUG: Attempting cache lookup for similar_neurons(VFB_jrchk00s_score_NBLAST_score) with full results
DEBUG: Cache lookup result: False
✅ Neo4j connection established
SimilarMorphologyTo: 10.6681s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.0977s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 0.9734s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
ok
test_12_nblast_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... ok
test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries ... ok
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

----------------------------------------------------------------------
Ran 15 tests in 54.052s

OK
================================================================================
anatScRNAseqQuery: 0.8399s ✅
  └─ Found 0 total clusters
clusterExpression: 0.8650s ✅
  └─ Found 0 genes expressed
expressionCluster: 0.8008s ✅
  └─ Found 0 clusters expressing gene
scRNAdatasetData: 0.7572s ✅
  └─ Found 0 clusters in dataset

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 0.8484s ✅
  └─ Found 227 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.5487s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.5578s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.5599s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.5828s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.5880s ✅
  └─ Found 0 painted domains
DatasetImages: 0.5793s ✅
  └─ Found 0 images in dataset
AllAlignedImages: 0.5528s ✅
  └─ Found 0 aligned images
AlignedDatasets: 0.7891s ✅
  └─ Found 0 aligned datasets
AllDatasets: 0.8566s ✅
  └─ Found 115 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.5244s ✅
  └─ Found 0 terms for publication
TransgeneExpressionHere: 0.6868s ✅
  └─ Found 2339 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.860s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
DEBUG: Checking cache for term_info, term_id=FBbt_00003748, cache_term_id=FBbt_00003748_preview_True, should_cache=True
DEBUG: Attempting cache lookup for term_info(FBbt_00003748_preview_True) with full results
DEBUG: Cache lookup result: True
DEBUG: Checking cache for term_info, term_id=VFB_00101567, cache_term_id=VFB_00101567_preview_True, should_cache=True
DEBUG: Attempting cache lookup for term_info(VFB_00101567_preview_True) with full results
DEBUG: Cache lookup result: True

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.3740 seconds
VFB_00101567 query took: 1.4854 seconds
Total time for both queries: 2.8594 seconds
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
*Last updated: 2025-11-18 22:32:22 UTC*
