# VFBquery Performance Test Results

**Test Date:** 2026-05-31 13:31:15 UTC
**Git Commit:** de86553a3e54c836a19821eb25ee174e74c7b993
**Branch:** main
**Workflow Run:** [26713771770](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26713771770)

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
=== RETRY ATTEMPT (auto-retry on first failure) ===
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
test_07b_downstream_class_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test DownstreamClassConnectivity query (multi-step aggregation) ... ok
test_07b_upstream_class_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test UpstreamClassConnectivity query (multi-step aggregation) ... ok
test_07c_cross_dataset_connectivity (src.test.test_query_performance.QueryPerformanceTest)
Test cross-dataset query_connectivity (live, both-end filtered) ... ok
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
Ran 18 tests in 66.303s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 1.4535s ✅
get_term_info (individual): 1.4388s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.8002s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.7595s ✅
NeuronsPresynapticHere: 1.4150s ✅
NeuronsPostsynapticHere: 1.6469s ✅
NeuronNeuronConnectivity: 1.4026s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.3981s ✅
PartsOf: 1.3777s ✅
SubclassesOf: 1.4041s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 3.2920s ✅
TractsNervesInnervatingHere: 1.9219s ✅
LineageClonesIn: 1.4473s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 2.7182s ✅
ImagesThatDevelopFrom: 1.6223s ✅
epFrag: 1.3700s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.4016s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.3696s ✅
NeuronRegionConnectivityQuery: 1.3995s ✅

================================================================================
DOWNSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
DownstreamClassConnectivity: 1.4234s ✅

================================================================================
UPSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
UpstreamClassConnectivity: 1.4422s ✅

================================================================================
CROSS-DATASET CONNECTIVITY (live, slow)
================================================================================
QueryConnectivity: 1.1352s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 0.8421s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 2.8888s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.0157s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.7483s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 0.7818s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 0.5994s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.6789s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 0.7848s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.6410s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.6384s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.6386s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.6481s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.6943s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.6303s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 2.6236s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 0.7538s ✅
  └─ Found 86 aligned datasets, returned 10
AllDatasets: 1.3917s ✅
  └─ Found 130 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.7074s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 0.8675s ✅
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
Ran 1 test in 3.016s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.4745 seconds
VFB_00101567 query took: 1.5409 seconds
Total time for both queries: 3.0154 seconds
Performance Level: 🟠 Acceptable (3-6 seconds)
==================================================
Performance test completed successfully!
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0
created: 4/4 workers
4 workers [55 items]

scheduling tests via LoadScheduling

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw3] [  1%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw1] [  3%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
[gw2] [  5%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] [  7%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw0] [  9%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw3] [ 10%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
[gw0] [ 12%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw2] [ 14%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
[gw3] [ 16%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw0] [ 18%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw3] [ 20%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw1] [ 21%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw2] [ 23%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw0] [ 25%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw3] [ 27%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] [ 29%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw1] [ 30%] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] [ 32%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw0] [ 34%] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw3] [ 36%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw3] [ 38%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw1] [ 40%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] [ 41%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw0] [ 43%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw1] [ 45%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw2] [ 47%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw3] [ 49%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw3] [ 50%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw0] [ 52%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
[gw0] [ 54%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw3] [ 56%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] [ 58%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw3] [ 60%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] [ 61%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] [ 63%] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw3] [ 65%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw1] [ 67%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw1] [ 69%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw1] [ 70%] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw1] [ 72%] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw1] [ 74%] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw1] [ 76%] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw2] [ 78%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw0] [ 80%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
[gw1] [ 81%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw1] [ 83%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw1] [ 85%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw1] [ 87%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw1] [ 89%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw3] [ 90%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw3] [ 92%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw0] [ 94%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw2] [ 96%] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw0] [ 98%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw2] [100%] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 

=============================== warnings summary ===============================
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(default=default, dump_default=dump_default, **kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: 16 warnings
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:138
src/vfbquery/vfb_queries.py:138
src/vfbquery/vfb_queries.py:138
src/vfbquery/vfb_queries.py:138
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:138: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    output_format = fields.String(required=False, missing='table')

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: 16 warnings
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
src/vfbquery/vfb_queries.py:308
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:308: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False)

src/vfbquery/vfb_queries.py:309
src/vfbquery/vfb_queries.py:309
src/vfbquery/vfb_queries.py:309
src/vfbquery/vfb_queries.py:309
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:309: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False, allow_none=True)

src/test/test_neuron_neuron_connectivity.py:22
src/test/test_neuron_neuron_connectivity.py:22
src/test/test_neuron_neuron_connectivity.py:22
src/test/test_neuron_neuron_connectivity.py:22
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:22: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:31
src/test/test_neuron_neuron_connectivity.py:31
src/test/test_neuron_neuron_connectivity.py:31
src/test/test_neuron_neuron_connectivity.py:31
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:31: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:41
src/test/test_neuron_neuron_connectivity.py:41
src/test/test_neuron_neuron_connectivity.py:41
src/test/test_neuron_neuron_connectivity.py:41
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:41: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:51
src/test/test_neuron_neuron_connectivity.py:51
src/test/test_neuron_neuron_connectivity.py:51
src/test/test_neuron_neuron_connectivity.py:51
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:51: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:59
src/test/test_neuron_neuron_connectivity.py:59
src/test/test_neuron_neuron_connectivity.py:59
src/test/test_neuron_neuron_connectivity.py:59
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:59: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:70
src/test/test_neuron_neuron_connectivity.py:70
src/test/test_neuron_neuron_connectivity.py:70
src/test/test_neuron_neuron_connectivity.py:70
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:70: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:85
src/test/test_neuron_neuron_connectivity.py:85
src/test/test_neuron_neuron_connectivity.py:85
src/test/test_neuron_neuron_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:93
src/test/test_neuron_neuron_connectivity.py:93
src/test/test_neuron_neuron_connectivity.py:93
src/test/test_neuron_neuron_connectivity.py:93
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:93: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:101
src/test/test_neuron_neuron_connectivity.py:101
src/test/test_neuron_neuron_connectivity.py:101
src/test/test_neuron_neuron_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:23
src/test/test_neuron_region_connectivity.py:23
src/test/test_neuron_region_connectivity.py:23
src/test/test_neuron_region_connectivity.py:23
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:23: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:32
src/test/test_neuron_region_connectivity.py:32
src/test/test_neuron_region_connectivity.py:32
src/test/test_neuron_region_connectivity.py:32
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:32: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:42
src/test/test_neuron_region_connectivity.py:42
src/test/test_neuron_region_connectivity.py:42
src/test/test_neuron_region_connectivity.py:42
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:42: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:52
src/test/test_neuron_region_connectivity.py:52
src/test/test_neuron_region_connectivity.py:52
src/test/test_neuron_region_connectivity.py:52
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:52: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:64
src/test/test_neuron_region_connectivity.py:64
src/test/test_neuron_region_connectivity.py:64
src/test/test_neuron_region_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:72
src/test/test_neuron_region_connectivity.py:72
src/test/test_neuron_region_connectivity.py:72
src/test/test_neuron_region_connectivity.py:72
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:72: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:80
src/test/test_neuron_region_connectivity.py:80
src/test/test_neuron_region_connectivity.py:80
src/test/test_neuron_region_connectivity.py:80
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:80: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:25
src/test/test_upstream_class_connectivity.py:25
src/test/test_upstream_class_connectivity.py:25
src/test/test_upstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:34
src/test/test_upstream_class_connectivity.py:34
src/test/test_upstream_class_connectivity.py:34
src/test/test_upstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:47
src/test/test_upstream_class_connectivity.py:47
src/test/test_upstream_class_connectivity.py:47
src/test/test_upstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:55
src/test/test_upstream_class_connectivity.py:55
src/test/test_upstream_class_connectivity.py:55
src/test/test_upstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:64
src/test/test_upstream_class_connectivity.py:64
src/test/test_upstream_class_connectivity.py:64
src/test/test_upstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:76
src/test/test_upstream_class_connectivity.py:76
src/test/test_upstream_class_connectivity.py:76
src/test/test_upstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:84
src/test/test_upstream_class_connectivity.py:84
src/test/test_upstream_class_connectivity.py:84
src/test/test_upstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:95
src/test/test_upstream_class_connectivity.py:95
src/test/test_upstream_class_connectivity.py:95
src/test/test_upstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:102
src/test/test_upstream_class_connectivity.py:102
src/test/test_upstream_class_connectivity.py:102
src/test/test_upstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:124
src/test/test_upstream_class_connectivity.py:124
src/test/test_upstream_class_connectivity.py:124
src/test/test_upstream_class_connectivity.py:124
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:124: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:168
src/test/test_upstream_class_connectivity.py:168
src/test/test_upstream_class_connectivity.py:168
src/test/test_upstream_class_connectivity.py:168
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:168: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:181
src/test/test_upstream_class_connectivity.py:181
src/test/test_upstream_class_connectivity.py:181
src/test/test_upstream_class_connectivity.py:181
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:181: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:25
src/test/test_downstream_class_connectivity.py:25
src/test/test_downstream_class_connectivity.py:25
src/test/test_downstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:34
src/test/test_downstream_class_connectivity.py:34
src/test/test_downstream_class_connectivity.py:34
src/test/test_downstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:47
src/test/test_downstream_class_connectivity.py:47
src/test/test_downstream_class_connectivity.py:47
src/test/test_downstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:55
src/test/test_downstream_class_connectivity.py:55
src/test/test_downstream_class_connectivity.py:55
src/test/test_downstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:64
src/test/test_downstream_class_connectivity.py:64
src/test/test_downstream_class_connectivity.py:64
src/test/test_downstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:76
src/test/test_downstream_class_connectivity.py:76
src/test/test_downstream_class_connectivity.py:76
src/test/test_downstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:84
src/test/test_downstream_class_connectivity.py:84
src/test/test_downstream_class_connectivity.py:84
src/test/test_downstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:95
src/test/test_downstream_class_connectivity.py:95
src/test/test_downstream_class_connectivity.py:95
src/test/test_downstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:102
src/test/test_downstream_class_connectivity.py:102
src/test/test_downstream_class_connectivity.py:102
src/test/test_downstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:123
src/test/test_downstream_class_connectivity.py:123
src/test/test_downstream_class_connectivity.py:123
src/test/test_downstream_class_connectivity.py:123
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:123: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:171
src/test/test_downstream_class_connectivity.py:171
src/test/test_downstream_class_connectivity.py:171
src/test/test_downstream_class_connectivity.py:171
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:171: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:185
src/test/test_downstream_class_connectivity.py:185
src/test/test_downstream_class_connectivity.py:185
src/test/test_downstream_class_connectivity.py:185
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:185: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:16
src/test/test_vfb_connectivity.py:16
src/test/test_vfb_connectivity.py:16
src/test/test_vfb_connectivity.py:16
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:16: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:21
src/test/test_vfb_connectivity.py:21
src/test/test_vfb_connectivity.py:21
src/test/test_vfb_connectivity.py:21
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:21: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:28
src/test/test_vfb_connectivity.py:28
src/test/test_vfb_connectivity.py:28
src/test/test_vfb_connectivity.py:28
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:28: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:34
src/test/test_vfb_connectivity.py:34
src/test/test_vfb_connectivity.py:34
src/test/test_vfb_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:47
src/test/test_vfb_connectivity.py:47
src/test/test_vfb_connectivity.py:47
src/test/test_vfb_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:56
src/test/test_vfb_connectivity.py:56
src/test/test_vfb_connectivity.py:56
src/test/test_vfb_connectivity.py:56
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:56: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:71
src/test/test_vfb_connectivity.py:71
src/test/test_vfb_connectivity.py:71
src/test/test_vfb_connectivity.py:71
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:71: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:85
src/test/test_vfb_connectivity.py:85
src/test/test_vfb_connectivity.py:85
src/test/test_vfb_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:101
src/test/test_vfb_connectivity.py:101
src/test/test_vfb_connectivity.py:101
src/test/test_vfb_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:114
src/test/test_vfb_connectivity.py:114
src/test/test_vfb_connectivity.py:114
src/test/test_vfb_connectivity.py:114
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:114: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 55 passed, 256 warnings in 402.44s (0:06:42) =================
```

## Summary

✅ **Test Status**: Performance tests completed


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-31 13:31:15 UTC*
