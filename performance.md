# VFBquery Performance Test Results

**Test Date:** 2026-08-20 03:37:09 UTC
**Git Commit:** 75832d86ced98e31bd10ee42c02aaf99a439d65b
**Branch:** main
**Workflow Run:** [32325983426](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/32325983426)

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
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
============================= test session starts ==============================
platform linux -- Python 3.10.21, pytest-9.1.1, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.21/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: timeout-2.4.0, xdist-3.8.0
timeout: 300.0s
timeout method: signal
timeout func_only: False
created: 4/4 workers
4 workers [18 items]

scheduling tests via LoadScheduling

src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

============================= 18 passed in 17.14s ==============================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.494s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.8654 seconds
VFB_00101567 query took: 0.6287 seconds
Total time for both queries: 1.4942 seconds
Performance Level: 🟢 Excellent (< 1.5 seconds)
==================================================
Performance test completed successfully!
=== CONNECTIVITY RETRY ATTEMPT ===
============================= test session starts ==============================
platform linux -- Python 3.10.21, pytest-9.1.1, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.21/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: timeout-2.4.0, xdist-3.8.0
timeout: 300.0s
timeout method: signal
timeout func_only: False
created: 8/8 workers
8 workers [65 items]

scheduling tests via LoadScheduling

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw5] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw5] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw6] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw7] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw7] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw7] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw4] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw6] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw1] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw4] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw4] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw4] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw5] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw3] ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw6] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw4] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw4] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw6] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw2] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw2] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw5] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw5] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw7] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw7] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw1] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw3] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw4] ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw4] ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw6] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw5] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw5] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw2] ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw6] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 

==================================== ERRORS ====================================
_ ERROR at setup of TestUpstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw3] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f8ec9b3fd60>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_upstream_class_connectivity.py:122: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4734: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream')
src/vfbquery/vfb_queries.py:4505: in _aggregate_class_connectivity
    instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
src/vfbquery/vfb_queries.py:4318: in _build_partner_instance_class_membership
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:827: in send
    r.content
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/models.py:1042: in content
    self._content = b"".join(self.iter_content(CONTENT_CHUNK_SIZE)) or b""
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/models.py:937: in generate
    yield from self.raw.stream(chunk_size, decode_content=True)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1260: in stream
    yield from self.read_chunked(amt, decode_content=decode_content)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1430: in read_chunked
    self._update_chunk_length()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1343: in _update_chunk_length
    line = self._fp.fp.readline()  # type: ignore[union-attr]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f8ec9b3d300>
b = <memory at 0x7f8eb38916c0>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw2] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7fe15eb7e560>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:121: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4661: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
src/vfbquery/vfb_queries.py:4493: in _aggregate_class_connectivity
    partner_class_ids, class_labels = _get_partner_class_ancestors(
src/vfbquery/vfb_queries.py:4281: in _get_partner_class_ancestors
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fe15eb15ba0>
b = <memory at 0x7fe14a5dc580>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw2] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7fe15eb7e560>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:121: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4661: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
src/vfbquery/vfb_queries.py:4493: in _aggregate_class_connectivity
    partner_class_ids, class_labels = _get_partner_class_ancestors(
src/vfbquery/vfb_queries.py:4281: in _get_partner_class_ancestors
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fe15eb15ba0>
b = <memory at 0x7fe14a5dc580>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ ERROR at setup of TestQueryConnectivitySubclassExpansion.test_parent_class_with_no_direct_instances_returns_results _
[gw4] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

    @pytest.fixture(scope="module")
    def expansion_result():
        """DA1 lPN -> Kenyon cell, grouped, run once for the whole module."""
>       return query_connectivity(
            upstream_type=EXPANSION_UPSTREAM,
            downstream_type=EXPANSION_DOWNSTREAM,
            group_by_class=True,
        )

src/test/test_vfb_connectivity.py:50: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:157: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f84302ecd00>
b = <memory at 0x7f8432124d00>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ ERROR at setup of TestQueryConnectivitySubclassExpansion.test_resolved_reports_how_a_label_was_read _
[gw4] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

    @pytest.fixture(scope="module")
    def expansion_result():
        """DA1 lPN -> Kenyon cell, grouped, run once for the whole module."""
>       return query_connectivity(
            upstream_type=EXPANSION_UPSTREAM,
            downstream_type=EXPANSION_DOWNSTREAM,
            group_by_class=True,
        )

src/test/test_vfb_connectivity.py:50: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:157: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f84302ecd00>
b = <memory at 0x7f8432124d00>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ ERROR at setup of TestQueryConnectivityExcludeDbsDefault.test_default_excludes_are_a_strict_subset_of_everything _
[gw2] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

    @pytest.fixture(scope="module")
    def expansion_result():
        """DA1 lPN -> Kenyon cell, grouped, run once for the whole module."""
>       return query_connectivity(
            upstream_type=EXPANSION_UPSTREAM,
            downstream_type=EXPANSION_DOWNSTREAM,
            group_by_class=True,
        )

src/test/test_vfb_connectivity.py:50: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:129: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fe15db995a0>
b = <memory at 0x7fe14a5dd780>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
=================================== FAILURES ===================================
____________ TestUpstreamClassConnectivityDict.test_returns_results ____________
[gw4] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7f843251f970>

    @pytest.mark.integration
    def test_returns_results(self):
>       result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:27: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4734: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream')
src/vfbquery/vfb_queries.py:4440: in _aggregate_class_connectivity
    rows = get_dict_cursor()(vc.nc.commit_list([membership_q]))
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f84325897e0>
b = <memory at 0x7f8432d63b80>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
________ TestUpstreamClassConnectivityDataFrame.test_returns_dataframe _________
[gw1] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDataFrame object at 0x7f605c589480>

    @pytest.mark.integration
    def test_returns_dataframe(self):
>       df = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:79: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4734: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream')
src/vfbquery/vfb_queries.py:4493: in _aggregate_class_connectivity
    partner_class_ids, class_labels = _get_partner_class_ancestors(
src/vfbquery/vfb_queries.py:4281: in _get_partner_class_ancestors
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f605c545690>
b = <memory at 0x7f60273c84c0>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
__________ TestNeuronRegionConnectivitySchema.test_schema_generation ___________
[gw5] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivitySchema object at 0x7faed4370490>

    def test_schema_generation(self):
>       term_info = get_term_info(TEST_NEURON)

src/test/test_neuron_region_connectivity.py:108: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:2690: in get_term_info
    term_info = fill_query_results(parsed_object, force_refresh=force_refresh)
src/vfbquery/vfb_queries.py:7129: in fill_query_results
    process_query(query)
src/vfbquery/vfb_queries.py:6971: in process_query
    result = _run_with_timeout(function, args=(short_form_value,), kwargs=base_kwargs)
src/vfbquery/vfb_queries.py:58: in _run_with_timeout
    return fut.result(timeout=timeout)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/concurrent/futures/_base.py:453: in result
    self._condition.wait(timeout)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <Condition(<unlocked _thread.RLock object owner=0 count=0 at 0x7faed437e740>, 0)>
timeout = 600

    def wait(self, timeout=None):
        """Wait until notified or until a timeout occurs.
    
        If the calling thread has not acquired the lock when this method is
        called, a RuntimeError is raised.
    
        This method releases the underlying lock, and then blocks until it is
        awakened by a notify() or notify_all() call for the same condition
        variable in another thread, or until the optional timeout occurs. Once
        awakened or timed out, it re-acquires the lock and returns.
    
        When the timeout argument is present and not None, it should be a
        floating point number specifying a timeout for the operation in seconds
        (or fractions thereof).
    
        When the underlying lock is an RLock, it is not released using its
        release() method, since this may not actually unlock the lock when it
        was acquired multiple times recursively. Instead, an internal interface
        of the RLock class is used, which really unlocks it even when it has
        been recursively acquired several times. Another internal interface is
        then used to restore the recursion level when the lock is reacquired.
    
        """
        if not self._is_owned():
            raise RuntimeError("cannot wait on un-acquired lock")
        waiter = _allocate_lock()
        waiter.acquire()
        self._waiters.append(waiter)
        saved_state = self._release_save()
        gotit = False
        try:    # restore state no matter what (e.g., KeyboardInterrupt)
            if timeout is None:
                waiter.acquire()
                gotit = True
            else:
                if timeout > 0:
>                   gotit = waiter.acquire(True, timeout)
E                   Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/threading.py:324: Failed
________ TestDownstreamClassConnectivityDict.test_row_has_expected_keys ________
[gw7] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7fdb147819f0>

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:36: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4661: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
src/vfbquery/vfb_queries.py:4505: in _aggregate_class_connectivity
    instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
src/vfbquery/vfb_queries.py:4318: in _build_partner_instance_class_membership
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fdb14740fd0>
b = <memory at 0x7fdb137f44c0>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestUpstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw6] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7fd54a17e4d0>
result = {'headers': {'id': {'title': 'ID', 'type': 'selection_id', 'order': -1}, 'upstream_class': {'title': 'Upstream Class',...'id': 'FBbt_00052046', 'query_id': 'FBbt_00001482', 'total_n': 397739, 'connected_n': 7633, ...}, ...], 'count': 10794}

    @pytest.mark.integration
    def test_includes_subclass_breakdown(self, result):
        """The result should contain the input term's own rows plus a block of
        rows for each subclass that has connectivity instances. Any non-input
        query_id must be a genuine subclass of the input term.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor
    
        rows = result["rows"]
        query_ids = {r["query_id"] for r in rows}
        assert TEST_CLASS in query_ids, "Expected the input term's own rows"
    
        # Full subclass closure (incl. the input term itself).
        q = (
            "MATCH (sub:Class)-[:SUBCLASSOF*0..]->(:Class {short_form: '%s'}) "
            "RETURN collect(DISTINCT sub.short_form) AS ids" % TEST_CLASS
        )
        subtree_rows = get_dict_cursor()(vc.nc.commit_list([q]))
        subtree = set(subtree_rows[0]["ids"]) if subtree_rows else set()
        offenders = [q for q in query_ids if q not in subtree]
        assert not offenders, (
            f"query_id(s) not in the input term's subclass closure: {offenders}"
        )
    
        # Subclasses of the input term that have connectivity instances.
        sub_q = (
            "MATCH (sub:Class)-[:SUBCLASSOF*1..]->(:Class {short_form: '%s'}) "
            "WHERE (sub)<-[:SUBCLASSOF*0..]-(:Class)<-[:INSTANCEOF]-"
            "(:Individual:has_neuron_connectivity) "
            "RETURN collect(DISTINCT sub.short_form) AS ids" % TEST_CLASS
        )
>       sub_rows = get_dict_cursor()(vc.nc.commit_list([sub_q]))

src/test/test_upstream_class_connectivity.py:229: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fd54a13c310>
b = <memory at 0x7fd54a97fe80>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestDownstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw4] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f8432563f70>
result = {'headers': {'id': {'title': 'ID', 'type': 'selection_id', 'order': -1}, 'upstream_class': {'title': 'Upstream Class',....}, {'id': 'FBbt_00005125', 'query_id': 'FBbt_00001482', 'total_n': 152, 'connected_n': 107, ...}, ...], 'count': 9095}

    @pytest.mark.integration
    def test_parent_class_appears_with_sensible_counts(self, result):
        """A row keyed on a parent class should have connected_n at least as
        large as any of its descendant rows (set-union semantics) and at most
        the sum of descendant connected_n (no double-counting beyond what
        multi-inheritance forces).
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor
    
        rows = [r for r in result["rows"] if r["query_id"] == TEST_CLASS]
        ids = [r["id"] for r in rows]
        assert ids, "Expected at least one row to test against"
    
        # Find any (parent, child) pair among the row ids.
        q = (
            "MATCH (p:Class)<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE p.short_form IN %s AND c.short_form IN %s "
            "RETURN p.short_form AS parent, c.short_form AS child LIMIT 1"
            % (ids, ids)
        )
        pairs = get_dict_cursor()(vc.nc.commit_list([q]))
        if not pairs:
            pytest.skip("No parent/child pair among result rows for this class")
    
        parent_id = pairs[0]["parent"]
        child_id = pairs[0]["child"]
        parent_row = next(r for r in rows if r["id"] == parent_id)
        # Sum connected_n across all descendant rows.
        desc_q = (
            "MATCH (p:Class {short_form: '%s'})<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS descs"
            % (parent_id, ids)
        )
>       desc_rows = get_dict_cursor()(vc.nc.commit_list([desc_q]))

src/test/test_downstream_class_connectivity.py:159: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f8430b587c0>
b = <memory at 0x7f8432d63880>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestUpstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw5] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7faed43721a0>
result = {'headers': {'id': {'title': 'ID', 'type': 'selection_id', 'order': -1}, 'upstream_class': {'title': 'Upstream Class',...'id': 'FBbt_00052046', 'query_id': 'FBbt_00001482', 'total_n': 397739, 'connected_n': 7633, ...}, ...], 'count': 10794}

    @pytest.mark.integration
    def test_parent_class_appears_with_sensible_counts(self, result):
        """A row keyed on a parent class should have connected_n at least as
        large as any of its descendant rows (set-union semantics) and at most
        the sum of descendant connected_n.
    
        Restricted to the input term's own block so partner rows are not mixed
        across queried (sub)classes.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor
    
        rows = [r for r in result["rows"] if r["query_id"] == TEST_CLASS]
        ids = [r["id"] for r in rows]
        assert ids, "Expected at least one row to test against"
    
        q = (
            "MATCH (p:Class)<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE p.short_form IN %s AND c.short_form IN %s "
            "RETURN p.short_form AS parent, c.short_form AS child LIMIT 1"
            % (ids, ids)
        )
        pairs = get_dict_cursor()(vc.nc.commit_list([q]))
        if not pairs:
            pytest.skip("No parent/child pair among result rows for this class")
    
        parent_id = pairs[0]["parent"]
        parent_row = next(r for r in rows if r["id"] == parent_id)
        desc_q = (
            "MATCH (p:Class {short_form: '%s'})<-[:SUBCLASSOF*1..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS descs"
            % (parent_id, ids)
        )
>       desc_rows = get_dict_cursor()(vc.nc.commit_list([desc_q]))

src/test/test_upstream_class_connectivity.py:159: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7faed4330af0>
b = <memory at 0x7faed3bc1480>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
___________ TestDownstreamClassConnectivityDict.test_headers_present ___________
[gw7] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7fdb14781510>

    @pytest.mark.integration
    def test_headers_present(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:50: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4661: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
src/vfbquery/vfb_queries.py:4505: in _aggregate_class_connectivity
    instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
src/vfbquery/vfb_queries.py:4318: in _build_partner_instance_class_membership
    results = vc.nc.commit_list([query])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:827: in send
    r.content
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/models.py:1042: in content
    self._content = b"".join(self.iter_content(CONTENT_CHUNK_SIZE)) or b""
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/models.py:937: in generate
    yield from self.raw.stream(chunk_size, decode_content=True)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1260: in stream
    yield from self.read_chunked(amt, decode_content=decode_content)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1430: in read_chunked
    self._update_chunk_length()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/response.py:1343: in _update_chunk_length
    line = self._fp.fp.readline()  # type: ignore[union-attr]
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fdb0ffab190>
b = <memory at 0x7fdb137f4100>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestDownstreamClassConnectivityDataFrame.test_dataframe_has_expected_columns _
[gw0] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f978a98f190>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
>       df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4661: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
src/vfbquery/vfb_queries.py:4440: in _aggregate_class_connectivity
    rows = get_dict_cursor()(vc.nc.commit_list([membership_q]))
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f978a923250>
b = <memory at 0x7f978b18be80>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
______ TestQueryConnectivityKnown.test_both_types_subset_of_either_alone _______
[gw1] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityKnown object at 0x7f605c5b1b40>

    @pytest.mark.integration
    def test_both_types_subset_of_either_alone(self):
        # Grouped on all three sides: a one-sided query returns every partner of
        # the named type, which is the one shape in this file that can run to
        # thousands of rows. Grouping bounds it at class pairs, and the
        # containment being asserted holds either way.
>       both = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            group_by_class=True,
        )

src/test/test_vfb_connectivity.py:110: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:129: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f605b58fa00>
b = <memory at 0x7f60273c84c0>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
____ TestQueryConnectivityWeightFiltering.test_higher_weight_fewer_results _____
[gw3] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityWeightFiltering object at 0x7f8ec9b7fcd0>

    @pytest.mark.integration
    def test_higher_weight_fewer_results(self):
>       result_low = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            weight=1,
        )

src/test/test_vfb_connectivity.py:144: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:129: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7f8ec8693400>
b = <memory at 0x7f8eb3890340>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_________ TestQueryConnectivityKnown.test_known_connection_both_types __________
[gw6] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityKnown object at 0x7fd54a1a56f0>

    @pytest.mark.integration
    def test_known_connection_both_types(self):
>       result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
        )

src/test/test_vfb_connectivity.py:97: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:441: in _query_connectivity_uncached
    results = nc.commit_list([cypher])
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fd53587d930>
b = <memory at 0x7fd54a97fe80>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestQueryConnectivityExcludeDbsDefault.test_default_matches_passing_it_explicitly _
[gw5] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityExcludeDbsDefault object at 0x7faed439a800>

    @pytest.mark.integration
    def test_default_matches_passing_it_explicitly(self):
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS
    
>       implicit = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, downstream_type=KNOWN_DOWNSTREAM,
        )

src/test/test_vfb_connectivity.py:244: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:341: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:391: in _query_connectivity_uncached
    class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
src/vfbquery/vfb_connectivity.py:129: in _resolve_neuron_type_label
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7faea42bbf10>
b = <memory at 0x7faed3bc2980>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
_ TestQueryConnectivitySubclassExpansion.test_anchor_side_does_not_change_the_answer _
[gw6] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivitySubclassExpansion object at 0x7fd54a1a4b80>

    @pytest.mark.integration
    def test_anchor_side_does_not_change_the_answer(self):
        # The query is driven from whichever side has fewer individuals; that is
        # a performance choice and must not be an answer choice. Run on the
        # small pair: forcing the anchor onto Kenyon cell's ~16,000 individuals
        # tested nothing extra and cost the most of anything in this file.
        from vfbquery.vfb_connectivity import (
            _get_nc, _subclass_closure, _build_connectivity_cypher,
            _resolve_neuron_type_label, DEFAULT_EXCLUDE_DBS,
        )
        from vfbquery.neo4j_client import dict_cursor
    
        nc = _get_nc()
        up_id = _resolve_neuron_type_label(nc, KNOWN_UPSTREAM)
        down_id = _resolve_neuron_type_label(nc, KNOWN_DOWNSTREAM)
>       _, up_ids, _ = _subclass_closure(nc, up_id)

src/test/test_vfb_connectivity.py:204: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:215: in _subclass_closure
    results = nc.commit_list([
src/vfbquery/neo4j_client.py:252: in commit_list
    response = requests.post(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:134: in post
    return request("post", url, data=data, json=json, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/api.py:71: in request
    return session.request(method=method, url=url, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:651: in request
    resp = self.send(prep, **send_kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/sessions.py:784: in send
    r = adapter.send(request, **kwargs)
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/requests/adapters.py:696: in send
    resp = conn.urlopen(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:788: in urlopen
    response = self._make_request(
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connectionpool.py:534: in _make_request
    response = conn.getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/urllib3/connection.py:571: in getresponse
    httplib_response = super().getresponse()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:1423: in getresponse
    response.begin()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:330: in begin
    version, status, reason = self._read_status()
/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/http/client.py:291: in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <socket.SocketIO object at 0x7fd5478d1d20>
b = <memory at 0x7fd51f43d6c0>

    def readinto(self, b):
        """Read up to len(b) bytes into the writable buffer *b* and return
        the number of bytes read.  If the socket is non-blocking and no bytes
        are available, None is returned.
    
        If *b* is non-empty, a 0 return value indicates that the connection
        was shutdown at the other end.
        """
        self._checkClosed()
        self._checkReadable()
        if self._timeout_occurred:
            raise OSError("cannot read from timed out object")
        while True:
            try:
>               return self._sock.recv_into(b)
E               Failed: Timeout (>300.0s) from pytest-timeout.

/opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/socket.py:717: Failed
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
  /opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly - Failed: Timeout (>300.0s) from pytest-timeout.
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read - Failed: Timeout (>300.0s) from pytest-timeout.
ERROR src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything - Failed: Timeout (>300.0s) from pytest-timeout.
======= 14 failed, 45 passed, 5 warnings, 6 errors in 1364.00s (0:22:43) =======
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 90
- **Passed**: 64 ✅
- **Failed**: 26 ❌
- **Errors**: 0 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|

⚠️ **Result**: Some performance thresholds exceeded or tests failed

Please review the failed tests above. Common causes:
- Network latency to VFB services
- SOLR/Neo4j/Owlery server load
- First-time cache population (expected to be slower)

---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-08-20 03:37:09 UTC*
