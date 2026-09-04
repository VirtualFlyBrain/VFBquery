# VFBquery Performance Test Results

**Test Date:** 2026-09-04 06:59:12 UTC
**Git Commit:** 0dd0a357c0d23248c6457399adc903515e9a07de
**Branch:** main
**Workflow Run:** [33844410550](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/33844410550)

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

src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 

=============================== warnings summary ===============================
src/vfbquery/vfb_queries.py:4967
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:4967: DeprecationWarning: invalid escape sequence '\]'
    """Build a ``[label](url)`` cell, or plain text when there is no url.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 18 passed, 1 warning in 30.76s ========================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 0.751s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.3860 seconds
VFB_00101567 query took: 0.3647 seconds
Total time for both queries: 0.7507 seconds
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
created: 4/4 workers
4 workers [68 items]

scheduling tests via LoadScheduling

src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw2] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw2] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw2] SKIPPED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw2] SKIPPED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw3] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw3] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw3] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw0] SKIPPED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 

=================================== FAILURES ===================================
___________ TestDownstreamClassConnectivityDict.test_limit_respected ___________
[gw1] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f71aa5f13c0>

    @pytest.mark.integration
    def test_limit_respected(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=3, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:58: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1159: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1152: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:4839: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'downstream'
neuron_root = 'FBbt_00005106'

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM):
        """Aggregate class-level partner connectivity for the queried class AND
        each of its subclasses individually, correctly under FBbt
        multi-inheritance using set-union over instance memberships.
    
        ``direction`` is ``'downstream'`` (partner = downstream of queried class)
        or ``'upstream'``. Returns a flat list of row dicts; every row is tagged
        with the queried (sub)class it belongs to via ``query_id`` /
        ``_query_label``. The input term's own rows (aggregated over its full
        instance population, exactly as before) come first, followed by a block of
        rows for each subclass that has connectivity instances, ordered by class id.
    
        The expensive pieces (per-instance edges, partner-side hierarchy and
        membership) are computed once for the whole subtree and instances are then
        partitioned by queried (sub)class, so cost is roughly independent of the
        number of subclasses.
        """
        from collections import defaultdict
    
        # 1a. Queried (sub)classes in scope: the input term plus every subclass.
        #     Reuse Owlery's reasoner subclass closure (the canonical subclass set
        #     used throughout VFBquery — get_instances, _fetch_connectivity_entries
        #     — and effectively cached) rather than a fresh Neo4j SUBCLASSOF
        #     traversal. The same set seeds the partner-fetch in step 3 below, so
        #     it is computed once here. Owlery excludes the queried class itself, so
        #     add it back.
        try:
            owl_query = f"<{short_form}>"
            subclass_ids = vc.vfb.oc.get_subclasses(
                query=owl_query, query_by_label=False, verbose=False,
                timeout=OWLERY_SUBCLASS_TIMEOUT,
            )
        except Exception as e:
            print(f"Owlery subclass query failed for {short_form}: {e}; "
                  "falling back to Neo4j SUBCLASSOF closure")
            subclass_ids = _neo4j_subclass_ids(short_form)
        query_class_ids = {short_form, *(subclass_ids or [])}
    
        # 1b. queried (sub)class -> its instances (SUBCLASSOF closure), with labels.
        #     The proven anchored membership query (single variable-length walk
        #     bounded by ``WHERE ... IN [ids]``) returns the instances AND the label
        #     for every queried (sub)class that actually has connectivity instances
        #     — which is exactly the set of blocks we emit — so no separate label
        #     lookup or subtree query is needed. Classes with no instances simply
        #     don't come back.
        membership_q = (
            "MATCH (c:Class)<-[:SUBCLASSOF*0..]-(:Class)<-[:INSTANCEOF]-"
            "(n:Individual:has_neuron_connectivity) "
            "WHERE c.short_form IN %s "
            "RETURN c.short_form AS cid, c.label AS label, "
            "collect(DISTINCT n.short_form) AS iids" % sorted(query_class_ids)
        )
        try:
            rows = get_dict_cursor()(vc.nc.commit_list([membership_q]))
        except Exception as e:
            print(f"Queried-side membership query failed for {short_form}: {e}")
            return []
        query_class_to_instances = defaultdict(set)
        query_labels = {}
        all_instances = set()
        for r in rows:
            cid = r.get('cid')
            iids = set(r.get('iids') or [])
            if not cid or not iids:
                continue
            query_class_to_instances[cid] = iids
            query_labels[cid] = r.get('label') or cid
            all_instances.update(iids)
        if not query_class_to_instances:
            return []
        query_labels.setdefault(short_form, short_form)
    
        # 2. Per-instance edges from cache (once for the whole subtree). Cache
        #    misses are skipped with a warning; the resulting connected_n /
        #    pairwise / total_weight will be a slight underestimate when this
        #    happens.
        found_edges, missing = _bulk_fetch_per_instance_connectivity(all_instances)
        if missing:
            print(
                f"Warning: per-instance connectivity cache missing for "
                f"{len(missing)}/{len(all_instances)} instances under {short_form}; "
                f"those will be skipped (results may be a slight underestimate)."
            )
        if not found_edges:
            return []
    
        weight_key = 'outputs' if direction == 'downstream' else 'inputs'
    
        # 3. Direct partner classes from the existing class-level connectivity
        #    field (already cached, unioned across the input term's subclass docs)
        #    — used as the seed set for the partner-side ancestor walk. Reuse the
        #    subclass set already resolved in step 1a rather than re-querying Owlery.
        solr_field = (
            'downstream_connectivity_query' if direction == 'downstream'
            else 'upstream_connectivity_query'
        )
        class_entries = _fetch_connectivity_entries(
            short_form, solr_field, subclass_ids=query_class_ids)
        direct_partner_ids = set()
        for entry in class_entries:
            obj = entry.get('object', {})
            pid = obj.get('short_form')
            if pid:
                direct_partner_ids.add(pid)
    
        # 4. Walk SUBCLASSOF up from each direct partner to ``neuron_root``.
        partner_class_ids, class_labels = _get_partner_class_ancestors(
            direct_partner_ids, neuron_root,
        )
        if not partner_class_ids:
            return []
    
        # 5. Build partner_instance_id -> {class_ids it belongs to}, restricted
        #    to in-scope partner classes. The helper already returns this
        #    instance -> {classes} mapping, so it is used directly. From it we also
        #    derive the total instance count per partner class (with SUBCLASSOF
        #    closure), which is the denominator when the partner is the presynaptic
        #    side (the upstream direction — see VFB_connect parity below).
        instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
        partner_class_total = defaultdict(int)
        _partner_class_members = defaultdict(set)
        for iid, classes in instance_to_partner_classes.items():
            for c in classes:
>               _partner_class_members[c].add(iid)
E               Failed: Timeout (>300.0s) from pytest-timeout.

src/vfbquery/vfb_queries.py:4688: Failed
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
  /opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected - Failed: Timeout (>300.0s) from pytest-timeout.
======= 1 failed, 29 passed, 38 skipped, 2 warnings in 843.89s (0:14:03) =======
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 49
- **Passed**: 48 ✅
- **Failed**: 1 ❌
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
*Last updated: 2026-09-04 06:59:12 UTC*
