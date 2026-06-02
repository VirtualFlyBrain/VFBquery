# VFBquery Performance Test Results

**Test Date:** 2026-06-02 06:33:38 UTC
**Git Commit:** d3f38d13017459580c9a75f8269f971844584f63
**Branch:** main
**Workflow Run:** [26802603506](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26802603506)

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
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0
created: 4/4 workers
4 workers [18 items]

scheduling tests via LoadScheduling

src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

============================= 18 passed in 28.83s ==============================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.466s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.2355 seconds
VFB_00101567 query took: 1.2297 seconds
Total time for both queries: 2.4652 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0
created: 8/8 workers
8 workers [55 items]

scheduling tests via LoadScheduling

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw7] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw5] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw5] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw7] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw5] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw6] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw4] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw7] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw6] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw5] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw7] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw7] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw4] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw5] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw6] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw4] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 

======================== 55 passed in 261.33s (0:04:21) ========================
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 74
- **Passed**: 74 ✅
- **Failed**: 0 ❌
- **Errors**: 0 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|

🎉 **Result**: All performance thresholds met!

---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-06-02 06:33:38 UTC*
