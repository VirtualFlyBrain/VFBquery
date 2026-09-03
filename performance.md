# VFBquery Performance Test Results

**Test Date:** 2026-09-03 07:04:46 UTC
**Git Commit:** c5fd9343e1ef22f2a3f4a982812269587a7d6ad2
**Branch:** main
**Workflow Run:** [33724402720](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/33724402720)

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
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

============================= 18 passed in 12.76s ==============================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 0.904s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.5383 seconds
VFB_00101567 query took: 0.3654 seconds
Total time for both queries: 0.9036 seconds
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

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
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
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 

=================================== FAILURES ===================================
_ TestQueryConnectivityExcludeDbsDefault.test_default_excludes_are_a_strict_subset_of_everything _
[gw0] linux -- Python 3.10.21 /opt/hostedtoolcache/Python/3.10.21/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityExcludeDbsDefault object at 0x7faf27b12110>
expansion_result = {'connections': [{'upstream_class': 'adult antennal lobe projection neuron DA1 lPN', 'upstream_class_id': 'FBbt_000673...}, 'downstream': {'query': 'Kenyon cell', 'id': 'FBbt_00003686', 'label': 'Kenyon cell', 'classes_searched': 38, ...}}}

    @pytest.mark.integration
    def test_default_excludes_are_a_strict_subset_of_everything(self, expansion_result):
        # Grouped, and reusing the module fixture for the default half, so this
        # costs one extra query rather than two full ungrouped ones over every
        # dataset — which is what made it the most expensive test here.
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS
    
        everything = query_connectivity(
            upstream_type=EXPANSION_UPSTREAM,
            downstream_type=EXPANSION_DOWNSTREAM,
            exclude_dbs=[],
            group_by_class=True,
        )
        assert DEFAULT_EXCLUDE_DBS == ["hb", "fafb"]
>       assert 0 < expansion_result["count"] < everything["count"]
E       assert 17 < 17

src/test/test_vfb_connectivity.py:304: AssertionError
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present
  /opt/hostedtoolcache/Python/3.10.21/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything - assert 17 < 17
============= 1 failed, 67 passed, 6 warnings in 661.31s (0:11:01) =============
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 87
- **Passed**: 86 ✅
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
*Last updated: 2026-09-03 07:04:46 UTC*
