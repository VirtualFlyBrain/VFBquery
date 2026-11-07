# VFBquery Performance Test Results

**Test Date:** 2026-11-07 00:26:48 UTC
**Git Commit:** 3fe13d7984f23fa36ba88141cf1789d921729feb
**Branch:** main
**Workflow Run:** [42313917760](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/42313917760)

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
platform linux -- Python 3.10.22, pytest-9.2.0, pluggy-1.7.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0, timeout-2.4.0, platformdirs-4.12.4
timeout: 300.0s
timeout method: signal
timeout func_only: False
created: 4/4 workers
4 workers [18 items]

scheduling tests via LoadScheduling

src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 

=============================== warnings summary ===============================
src/vfbquery/vfb_queries.py:5480
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:5480: DeprecationWarning: invalid escape sequence '\]'
    """Build a ``[label](url)`` cell, or plain text when there is no url.

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 18 passed, 1 warning in 18.30s ========================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 0.790s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.3929 seconds
VFB_00101567 query took: 0.3970 seconds
Total time for both queries: 0.7899 seconds
Performance Level: 🟢 Excellent (< 1.5 seconds)
==================================================
Performance test completed successfully!
=== CONNECTIVITY RETRY ATTEMPT ===
============================= test session starts ==============================
platform linux -- Python 3.10.22, pytest-9.2.0, pluggy-1.7.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0, timeout-2.4.0, platformdirs-4.12.4
timeout: 300.0s
timeout method: signal
timeout func_only: False
created: 4/4 workers
4 workers [78 items]

scheduling tests via LoadScheduling

src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw0] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw2] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw3] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw2] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
[gw3] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
[gw1] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw0] FAILED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
[gw3] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 

=================================== FAILURES ===================================
_ TestUpstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root __
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f35b75592d0>
result = {'headers': {'id': {'title': 'ID', 'type': 'selection_id', 'order': -1}, 'upstream_class': {'title': 'Upstream Class',...'id': 'FBbt_00052046', 'query_id': 'FBbt_00001482', 'total_n': 458776, 'connected_n': 8213, ...}, ...], 'count': 11001}

    @pytest.mark.integration
    def test_no_rows_above_neuron_root(self, result):
        """The partner-side ancestor walk should stop at the Neuron class
        (FBbt_00005106). No row id should be a class outside the Neuron
        subtree.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor, NEURON_ROOT_SHORT_FORM
    
        ids = [r["id"] for r in result["rows"]]
        assert ids, "Expected at least one row"
        q = (
            "MATCH (root:Class {short_form: '%s'})<-[:SUBCLASSOF*0..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS in_neuron"
            % (NEURON_ROOT_SHORT_FORM, ids)
        )
        result_rows = get_dict_cursor()(vc.nc.commit_list([q]))
        in_neuron = set(result_rows[0]["in_neuron"]) if result_rows else set()
        offenders = [i for i in ids if i not in in_neuron]
>       assert not offenders, (
            f"Found {len(offenders)} row(s) outside the Neuron subtree: "
            f"{offenders[:5]}"
        )
E       AssertionError: Found 11001 row(s) outside the Neuron subtree: ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00005125']
E       assert not ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00005125', 'FBbt_00052046', ...]

src/test/test_upstream_class_connectivity.py:295: AssertionError
_______ TestUpstreamClassConnectivityDict.test_empty_class_returns_zero ________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7fbf2551ab30>

    @pytest.mark.integration
    def test_empty_class_returns_zero(self):
>       result = get_upstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5388: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00000001', direction = 'upstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 0}

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM,
                                      status=None):
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
    
        An empty list means "no partners": the class has no connectivity
        instances, or they have no positive-weight edges to in-scope partner
        classes. It never means "a backend call failed" — that raises
        :class:`ConnectivityBackendError` so that no cache layer can store a zero
        that was really an outage.
    
        ``status`` may be a dict; on return it carries ``missing`` (the number of
        queried instances whose per-instance connectivity could not be obtained,
        so the counts are underestimates) and ``total`` (queried instances).
        """
        from collections import defaultdict
        if status is None:
            status = {}
        status.update(missing=0, total=0)
    
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
            raw = vc.nc.commit_list([membership_q])
        except Exception as e:
            raise ConnectivityBackendError(
                f"Queried-side membership query failed for {short_form}: {e}"
            ) from e
        if not isinstance(raw, list):
            # commit_list reports a transaction error by returning False, not by
            # raising, and dict_cursor then turns False into [] — which is how a
            # Neo4j outage used to read as "no instances". A class with no
            # instances comes back as a list with an empty ``data``.
>           raise ConnectivityBackendError(
                f"Queried-side membership query returned no result for {short_form}"
            )
E           vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001

src/vfbquery/vfb_queries.py:5045: ConnectivityBackendError
_ TestUpstreamClassConnectivityDataFrame.test_empty_class_returns_empty_dataframe _
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDataFrame object at 0x7fdaef33c9a0>

    @pytest.mark.integration
    def test_empty_class_returns_empty_dataframe(self):
>       df = get_upstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=True, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:145: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5388: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00000001', direction = 'upstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 0}

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM,
                                      status=None):
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
    
        An empty list means "no partners": the class has no connectivity
        instances, or they have no positive-weight edges to in-scope partner
        classes. It never means "a backend call failed" — that raises
        :class:`ConnectivityBackendError` so that no cache layer can store a zero
        that was really an outage.
    
        ``status`` may be a dict; on return it carries ``missing`` (the number of
        queried instances whose per-instance connectivity could not be obtained,
        so the counts are underestimates) and ``total`` (queried instances).
        """
        from collections import defaultdict
        if status is None:
            status = {}
        status.update(missing=0, total=0)
    
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
            raw = vc.nc.commit_list([membership_q])
        except Exception as e:
            raise ConnectivityBackendError(
                f"Queried-side membership query failed for {short_form}: {e}"
            ) from e
        if not isinstance(raw, list):
            # commit_list reports a transaction error by returning False, not by
            # raising, and dict_cursor then turns False into [] — which is how a
            # Neo4j outage used to read as "no instances". A class with no
            # instances comes back as a list with an empty ``data``.
>           raise ConnectivityBackendError(
                f"Queried-side membership query returned no result for {short_form}"
            )
E           vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001

src/vfbquery/vfb_queries.py:5045: ConnectivityBackendError
___________ TestDownstreamClassConnectivityDict.test_returns_results ___________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f35b7535a20>

    @pytest.mark.integration
    def test_returns_results(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5314: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream', status=status)
src/test/test_downstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'downstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 181}

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM,
                                      status=None):
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
    
        An empty list means "no partners": the class has no connectivity
        instances, or they have no positive-weight edges to in-scope partner
        classes. It never means "a backend call failed" — that raises
        :class:`ConnectivityBackendError` so that no cache layer can store a zero
        that was really an outage.
    
        ``status`` may be a dict; on return it carries ``missing`` (the number of
        queried instances whose per-instance connectivity could not be obtained,
        so the counts are underestimates) and ``total`` (queried instances).
        """
        from collections import defaultdict
        if status is None:
            status = {}
        status.update(missing=0, total=0)
    
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
            raw = vc.nc.commit_list([membership_q])
        except Exception as e:
            raise ConnectivityBackendError(
                f"Queried-side membership query failed for {short_form}: {e}"
            ) from e
        if not isinstance(raw, list):
            # commit_list reports a transaction error by returning False, not by
            # raising, and dict_cursor then turns False into [] — which is how a
            # Neo4j outage used to read as "no instances". A class with no
            # instances comes back as a list with an empty ``data``.
            raise ConnectivityBackendError(
                f"Queried-side membership query returned no result for {short_form}"
            )
        rows = get_dict_cursor()(raw)
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
        status.update(missing=len(missing), total=len(all_instances))
        if missing:
            print(
                f"Warning: per-instance connectivity unavailable for "
                f"{len(missing)}/{len(all_instances)} instances under {short_form}; "
                f"those will be skipped (results are an underestimate)."
            )
        if not found_edges:
            # Every queried instance is a has_neuron_connectivity individual, so
            # each has a per-instance result; getting none of them is a Solr/Neo4j
            # failure, not a class with no partners.
            raise ConnectivityBackendError(
                f"Per-instance connectivity unavailable for all "
                f"{len(all_instances)} instances under {short_form}"
            )
    
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
            if any(_has_positive_edge(edges, weight_key)
                   for edges in found_edges.values()):
                # Instances have partners but no partner *class* came back:
                # _fetch_connectivity_entries swallows Solr errors as [] and
                # _get_partner_class_ancestors swallows Neo4j errors, so this is
                # an outage, not a class whose partners are unclassified.
                raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
            return []
    
        # 5. Build partner_instance_id -> {class_ids it belongs to}, restricted
        #    to in-scope partner classes. The helper already returns this
        #    instance -> {classes} mapping, so it is used directly. From it we also
        #    derive the total instance count per partner class (with SUBCLASSOF
        #    closure), which is the denominator when the partner is the presynaptic
        #    side (the upstream direction — see VFB_connect parity below).
        instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
        if not instance_to_partner_classes:
            # partner_class_ids is non-empty here and every one of those classes
            # has at least one connectivity instance (that is how it became a
            # partner), so an empty membership map is the Neo4j query failing —
            # the helper swallows the exception and returns {} — and would
            # otherwise yield count 0 with no error.
>           raise ConnectivityBackendError(
                f"Partner class membership query failed for {short_form} "
                f"({len(partner_class_ids)} partner classes)"
            )
E           vfbquery.vfb_queries.ConnectivityBackendError: Partner class membership query failed for FBbt_00001482 (3288 partner classes)

src/vfbquery/vfb_queries.py:5134: ConnectivityBackendError
_ TestDownstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f159e564f10>
result = {'headers': {'id': {'title': 'ID', 'type': 'selection_id', 'order': -1}, 'upstream_class': {'title': 'Upstream Class',....}, {'id': 'FBbt_00005125', 'query_id': 'FBbt_00001482', 'total_n': 181, 'connected_n': 127, ...}, ...], 'count': 9343}

    @pytest.mark.integration
    def test_no_rows_above_neuron_root(self, result):
        """The partner-side ancestor walk should stop at the Neuron class
        (FBbt_00005106). No row id should be a class outside the Neuron
        subtree.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor, NEURON_ROOT_SHORT_FORM
    
        ids = [r["id"] for r in result["rows"]]
        assert ids, "Expected at least one row"
        q = (
            "MATCH (root:Class {short_form: '%s'})<-[:SUBCLASSOF*0..]-(c:Class) "
            "WHERE c.short_form IN %s "
            "RETURN collect(DISTINCT c.short_form) AS in_neuron"
            % (NEURON_ROOT_SHORT_FORM, ids)
        )
        result_rows = get_dict_cursor()(vc.nc.commit_list([q]))
        in_neuron = set(result_rows[0]["in_neuron"]) if result_rows else set()
        offenders = [i for i in ids if i not in in_neuron]
>       assert not offenders, (
            f"Found {len(offenders)} row(s) outside the Neuron subtree: "
            f"{offenders[:5]}"
        )
E       AssertionError: Found 9343 row(s) outside the Neuron subtree: ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00059289']
E       assert not ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00059289', 'FBbt_00005125', ...]

src/test/test_downstream_class_connectivity.py:294: AssertionError
______ TestDownstreamClassConnectivityDict.test_empty_class_returns_zero _______
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7fbf2551a620>

    @pytest.mark.integration
    def test_empty_class_returns_zero(self):
>       result = get_downstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5314: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream', status=status)
src/test/test_downstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00000001', direction = 'downstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 0}

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM,
                                      status=None):
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
    
        An empty list means "no partners": the class has no connectivity
        instances, or they have no positive-weight edges to in-scope partner
        classes. It never means "a backend call failed" — that raises
        :class:`ConnectivityBackendError` so that no cache layer can store a zero
        that was really an outage.
    
        ``status`` may be a dict; on return it carries ``missing`` (the number of
        queried instances whose per-instance connectivity could not be obtained,
        so the counts are underestimates) and ``total`` (queried instances).
        """
        from collections import defaultdict
        if status is None:
            status = {}
        status.update(missing=0, total=0)
    
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
            raw = vc.nc.commit_list([membership_q])
        except Exception as e:
            raise ConnectivityBackendError(
                f"Queried-side membership query failed for {short_form}: {e}"
            ) from e
        if not isinstance(raw, list):
            # commit_list reports a transaction error by returning False, not by
            # raising, and dict_cursor then turns False into [] — which is how a
            # Neo4j outage used to read as "no instances". A class with no
            # instances comes back as a list with an empty ``data``.
>           raise ConnectivityBackendError(
                f"Queried-side membership query returned no result for {short_form}"
            )
E           vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001

src/vfbquery/vfb_queries.py:5045: ConnectivityBackendError
_ TestDownstreamClassConnectivityDataFrame.test_empty_class_returns_empty_dataframe _
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7fdaef33c850>

    @pytest.mark.integration
    def test_empty_class_returns_empty_dataframe(self):
>       df = get_downstream_class_connectivity(
            EMPTY_CLASS, return_dataframe=True, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:145: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5314: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream', status=status)
src/test/test_downstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00000001', direction = 'downstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 0}

    def _aggregate_class_connectivity(short_form, direction,
                                      neuron_root=NEURON_ROOT_SHORT_FORM,
                                      status=None):
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
    
        An empty list means "no partners": the class has no connectivity
        instances, or they have no positive-weight edges to in-scope partner
        classes. It never means "a backend call failed" — that raises
        :class:`ConnectivityBackendError` so that no cache layer can store a zero
        that was really an outage.
    
        ``status`` may be a dict; on return it carries ``missing`` (the number of
        queried instances whose per-instance connectivity could not be obtained,
        so the counts are underestimates) and ``total`` (queried instances).
        """
        from collections import defaultdict
        if status is None:
            status = {}
        status.update(missing=0, total=0)
    
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
            raw = vc.nc.commit_list([membership_q])
        except Exception as e:
            raise ConnectivityBackendError(
                f"Queried-side membership query failed for {short_form}: {e}"
            ) from e
        if not isinstance(raw, list):
            # commit_list reports a transaction error by returning False, not by
            # raising, and dict_cursor then turns False into [] — which is how a
            # Neo4j outage used to read as "no instances". A class with no
            # instances comes back as a list with an empty ``data``.
>           raise ConnectivityBackendError(
                f"Queried-side membership query returned no result for {short_form}"
            )
E           vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001

src/vfbquery/vfb_queries.py:5045: ConnectivityBackendError
_ TestQueryConnectivityExcludeDbsDefault.test_default_excludes_are_a_strict_subset_of_everything _
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityExcludeDbsDefault object at 0x7fdaef33ded0>
expansion_result = {'connections': [], 'warnings': ["'DA1 lPN' is not a VFB term; matched the only term containing it: 'adult antennal lo... 'downstream': {'query': 'Kenyon cell', 'id': 'FBbt_00003686', 'label': 'FBbt_00003686', 'classes_searched': 38, ...}}}

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
        # Subset, not strict subset. Excluding a dataset can only ever remove
        # rows, and that is the contract worth asserting. Demanding a strict
        # decrease additionally requires hemibrain or FAFB to hold rows for
        # *this* term pair, which is backend content -- it was true when this
        # was written and is not true now (17 either way).
>       assert 0 < expansion_result["count"] <= everything["count"]
E       assert 0 < 0

src/test/test_vfb_connectivity.py:315: AssertionError
______ TestQueryConnectivityKnown.test_both_types_subset_of_either_alone _______
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityKnown object at 0x7f159e593460>

    @pytest.mark.integration
    # Three live queries, two of them one-sided (everything downstream of the
    # giant fiber neuron / upstream of GFC2), so a cold run can pass 300s.
    @pytest.mark.timeout(600)
    def test_both_types_subset_of_either_alone(self):
        # Grouped on all three sides: a one-sided query returns every partner of
        # the named type, which is the one shape in this file that can run to
        # thousands of rows. Grouping bounds it at class pairs, and the
        # containment being asserted holds either way.
        both = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            group_by_class=True,
        )
        up_only = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, group_by_class=True,
        )
        down_only = query_connectivity(
            downstream_type=KNOWN_DOWNSTREAM, group_by_class=True,
        )
    
>       assert both["count"] > 0
E       assert 0 > 0

src/test/test_vfb_connectivity.py:128: AssertionError
_____________ TestKnownNeurotransmitters.test_includes_subclasses ______________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestKnownNeurotransmitters object at 0x7f35b758f010>
known_tm9 = {'neurotransmitters': [], 'warnings': ["Neuron class not found for ID 'FBbt_00003797'. Check the ID is a valid neuron class (not an anatomy region)."], 'count': 0, 'resolved': {}}

    @pytest.mark.integration
    def test_includes_subclasses(self, known_tm9):
        # Tm9a / Tm9b are subtypes of Tm9 and should appear as their own rows.
        cell_types = {r["cell_type_id"] for r in known_tm9["neurotransmitters"]}
>       assert len(cell_types) > 1
E       assert 0 > 1
E        +  where 0 = len(set())

src/test/test_vfb_connectivity.py:436: AssertionError
_ TestQueryConnectivityExcludeDbsDefault.test_default_matches_passing_it_explicitly _
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityExcludeDbsDefault object at 0x7fdaef3e4130>

    @pytest.mark.integration
    def test_default_matches_passing_it_explicitly(self):
        from vfbquery.vfb_connectivity import DEFAULT_EXCLUDE_DBS
    
        implicit = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, downstream_type=KNOWN_DOWNSTREAM,
        )
        explicit = query_connectivity(
            upstream_type=KNOWN_UPSTREAM, downstream_type=KNOWN_DOWNSTREAM,
            exclude_dbs=list(DEFAULT_EXCLUDE_DBS),
        )
>       assert implicit["count"] == explicit["count"]
E       assert 20 == 0

src/test/test_vfb_connectivity.py:328: AssertionError
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
  /opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1392: PytestRemovedIn10Warning: Class-scoped fixtures defined as instance methods are deprecated.
  Instance attributes set in the 'result' fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use a @classmethod decorator below @pytest.fixture and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children
  /opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1392: PytestRemovedIn10Warning: Class-scoped fixtures defined as instance methods are deprecated.
  Instance attributes set in the 'rollup_result' fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use a @classmethod decorator below @pytest.fixture and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - AssertionError: Found 11001 row(s) outside the Neuron subtree: ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00005125']
assert not ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00005125', 'FBbt_00052046', ...]
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero - vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe - vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results - vfbquery.vfb_queries.ConnectivityBackendError: Partner class membership query failed for FBbt_00001482 (3288 partner classes)
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - AssertionError: Found 9343 row(s) outside the Neuron subtree: ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00059289']
assert not ['FBbt_00005106', 'FBbt_00047095', 'FBbt_00059271', 'FBbt_00059274', 'FBbt_00059289', 'FBbt_00005125', ...]
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero - vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe - vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00000001
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything - assert 0 < 0
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone - assert 0 > 0
FAILED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses - assert 0 > 1
 +  where 0 = len(set())
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly - assert 20 == 0
============ 11 failed, 67 passed, 5 warnings in 1346.97s (0:22:26) ============
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 97
- **Passed**: 86 ✅
- **Failed**: 11 ❌
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
*Last updated: 2026-11-07 00:26:48 UTC*
