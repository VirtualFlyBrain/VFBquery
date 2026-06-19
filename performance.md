# VFBquery Performance Test Results

**Test Date:** 2026-06-19 07:53:41 UTC
**Git Commit:** 254fde5c12ee5bb8af595aa410b858b2525b9a0f
**Branch:** main
**Workflow Run:** [27810648068](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/27810648068)

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
platform linux -- Python 3.10.20, pytest-9.1.0, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0
created: 4/4 workers
4 workers [18 items]

scheduling tests via LoadScheduling

src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
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
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

============================= 18 passed in 26.92s ==============================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.942s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.1629 seconds
VFB_00101567 query took: 0.7792 seconds
Total time for both queries: 1.9421 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
=== CONNECTIVITY RETRY ATTEMPT ===
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.1.0, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: xdist-3.8.0
created: 8/8 workers
8 workers [57 items]

scheduling tests via LoadScheduling

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw4] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw5] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw2] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw7] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw6] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw6] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw7] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw6] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw7] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw6] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw7] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw7] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw6] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw6] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw7] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw6] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw6] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw6] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw7] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw6] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw7] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw6] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw7] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw6] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw6] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw6] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw7] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw7] FAILED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw4] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw3] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw5] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw3] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw7] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw1] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw1] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw6] FAILED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw4] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw7] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw2] FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw5] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw6] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw7] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw5] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw0] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw0] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw4] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 

=================================== FAILURES ===================================
____________ TestNeuronRegionConnectivityDict.test_returns_results _____________
[gw5] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDict object at 0x7ff7fcba41f0>

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False
        )
        assert isinstance(result, dict)
>       assert result["count"] > 0
E       assert 0 > 0

src/test/test_neuron_region_connectivity.py:29: AssertionError
_________ TestNeuronNeuronConnectivityDataFrame.test_returns_dataframe _________
[gw2] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDataFrame object at 0x7f1eac386bf0>

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=True
        )
        assert isinstance(df, pd.DataFrame)
>       assert not df.empty
E       assert not True
E        +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty

src/test/test_neuron_neuron_connectivity.py:91: AssertionError
____________ TestNeuronRegionConnectivityDict.test_headers_present _____________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDict object at 0x7f2c8718c550>

    @pytest.mark.integration
    def test_headers_present(self):
>       result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )

src/test/test_neuron_region_connectivity.py:44: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3328: in get_neuron_region_connectivity
    results = vc.nc.commit_list([cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f2c8718fa60>
statements = ['\n        MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n        MATCH (target:Individual)<-[r:has_presy...label END, template_anat.short_form + "," + target.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
_________ TestNeuronRegionConnectivityDataFrame.test_returns_dataframe _________
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDataFrame object at 0x7f5e397778e0>

    @pytest.mark.integration
    def test_returns_dataframe(self):
>       df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True
        )

src/test/test_neuron_region_connectivity.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3328: in get_neuron_region_connectivity
    results = vc.nc.commit_list([cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f5e397a3190>
statements = ['\n        MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n        MATCH (target:Individual)<-[r:has_presy...label END, template_anat.short_form + "," + target.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
__ TestNeuronRegionConnectivityDataFrame.test_dataframe_has_expected_columns ___
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDataFrame object at 0x7f5e39776bc0>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
>       df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True, limit=1
        )

src/test/test_neuron_region_connectivity.py:74: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3328: in get_neuron_region_connectivity
    results = vc.nc.commit_list([cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f5e397a3190>
statements = ['\n        MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n        MATCH (target:Individual)<-[r:has_presy...label END, template_anat.short_form + "," + target.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
____________ TestNeuronRegionConnectivityDict.test_limit_respected _____________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDict object at 0x7f2c8715f490>

    @pytest.mark.integration
    def test_limit_respected(self):
>       result = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=False, limit=3
        )

src/test/test_neuron_region_connectivity.py:54: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3328: in get_neuron_region_connectivity
    results = vc.nc.commit_list([cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f2c8718fa60>
statements = ['\n        MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n        MATCH (target:Individual)<-[r:has_presy...label END, template_anat.short_form + "," + target.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
__ TestUpstreamClassConnectivityDataFrame.test_dataframe_has_expected_columns __
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDataFrame object at 0x7f5e397a1db0>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=1, force_refresh=True
        )
        expected_cols = {
            "id", "query_id", "upstream_class", "downstream_class",
            "total_n", "connected_n", "percent_connected",
            "pairwise_connections", "total_weight", "avg_weight",
        }
>       assert expected_cols.issubset(set(df.columns))
E       AssertionError: assert False
E        +  where False = <built-in method issubset of set object at 0x7f5e38b3dd20>(set())
E        +    where <built-in method issubset of set object at 0x7f5e38b3dd20> = {'avg_weight', 'connected_n', 'downstream_class', 'id', 'pairwise_connections', 'percent_connected', ...}.issubset
E        +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
E        +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns

src/test/test_upstream_class_connectivity.py:95: AssertionError
________ TestUpstreamClassConnectivityDataFrame.test_returns_dataframe _________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDataFrame object at 0x7f2c8718e020>

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )
        assert isinstance(df, pd.DataFrame)
>       assert not df.empty
E       assert not True
E        +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty

src/test/test_upstream_class_connectivity.py:83: AssertionError
___ TestUpstreamClassConnectivityHierarchyRollup.test_total_n_is_per_partner ___
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f2c8718dfc0>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_total_n_is_per_partner(self, result):
        """In the upstream direction the presynaptic side is the partner, so
        (matching VFB_connect's normalization) `total_n` describes the partner
        (`upstream_class`): it must be constant across every row referencing the
        same partner id, regardless of which queried (sub)class block it is in,
        and `connected_n` must never exceed it.
        """
        from collections import defaultdict
    
        rows = result["rows"]
>       assert rows, "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_upstream_class_connectivity.py:184: AssertionError
_ TestUpstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f5e397a1cf0>
result = {'headers': {}, 'rows': [], 'count': 0}

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
>       assert ids, "Expected at least one row to test against"
E       AssertionError: Expected at least one row to test against
E       assert []

src/test/test_upstream_class_connectivity.py:139: AssertionError
_ TestUpstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f5e397a1300>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_includes_subclass_breakdown(self, result):
        """The result should contain the input term's own rows plus a block of
        rows for each subclass that has connectivity instances. Any non-input
        query_id must be a genuine subclass of the input term.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor
    
        rows = result["rows"]
        query_ids = {r["query_id"] for r in rows}
>       assert TEST_CLASS in query_ids, "Expected the input term's own rows"
E       AssertionError: Expected the input term's own rows
E       assert 'FBbt_00001482' in set()

src/test/test_upstream_class_connectivity.py:208: AssertionError
_ TestUpstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root __
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f2c8718d6f0>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_no_rows_above_neuron_root(self, result):
        """The partner-side ancestor walk should stop at the Neuron class
        (FBbt_00005106). No row id should be a class outside the Neuron
        subtree.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor, NEURON_ROOT_SHORT_FORM
    
        ids = [r["id"] for r in result["rows"]]
>       assert ids, "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_upstream_class_connectivity.py:246: AssertionError
___________ TestDownstreamClassConnectivityDict.test_returns_results ___________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f2c8718f610>

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )
        assert isinstance(result, dict)
>       assert result["count"] > 0
E       assert 0 > 0

src/test/test_downstream_class_connectivity.py:31: AssertionError
________ TestDownstreamClassConnectivityDict.test_row_has_expected_keys ________
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f5e397a33a0>

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
>       assert result["rows"], "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_downstream_class_connectivity.py:39: AssertionError
___________ TestDownstreamClassConnectivityDict.test_headers_present ___________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f2c8718fbb0>

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
        assert "headers" in result
>       assert "downstream_class" in result["headers"]
E       AssertionError: assert 'downstream_class' in {}

src/test/test_downstream_class_connectivity.py:54: AssertionError
_______ TestDownstreamClassConnectivityDataFrame.test_returns_dataframe ________
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f5e397a38b0>

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )
        assert isinstance(df, pd.DataFrame)
>       assert not df.empty
E       assert not True
E        +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty

src/test/test_downstream_class_connectivity.py:83: AssertionError
_ TestDownstreamClassConnectivityDataFrame.test_dataframe_has_expected_columns _
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f5e397a32b0>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=1, force_refresh=True
        )
        expected_cols = {
            "id", "query_id", "upstream_class", "downstream_class",
            "total_n", "connected_n", "percent_connected",
            "pairwise_connections", "total_weight", "avg_weight",
        }
>       assert expected_cols.issubset(set(df.columns))
E       AssertionError: assert False
E        +  where False = <built-in method issubset of set object at 0x7f5e38b3e0a0>(set())
E        +    where <built-in method issubset of set object at 0x7f5e38b3e0a0> = {'avg_weight', 'connected_n', 'downstream_class', 'id', 'pairwise_connections', 'percent_connected', ...}.issubset
E        +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
E        +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns

src/test/test_downstream_class_connectivity.py:95: AssertionError
_ TestDownstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f5e397a19f0>
result = {'headers': {}, 'rows': [], 'count': 0}

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
>       assert ids, "Expected at least one row to test against"
E       AssertionError: Expected at least one row to test against
E       assert []

src/test/test_downstream_class_connectivity.py:136: AssertionError
_ TestDownstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f5e397a3c70>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_includes_subclass_breakdown(self, result):
        """The result should contain the input term's own rows plus a block of
        rows for each subclass that has connectivity instances. Any non-input
        query_id must be a genuine subclass of the input term.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor
    
        rows = result["rows"]
        query_ids = {r["query_id"] for r in rows}
>       assert TEST_CLASS in query_ids, "Expected the input term's own rows"
E       AssertionError: Expected the input term's own rows
E       assert 'FBbt_00001482' in set()

src/test/test_downstream_class_connectivity.py:207: AssertionError
_ TestDownstreamClassConnectivityHierarchyRollup.test_total_n_constant_within_each_query_class _
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f2c8718e2c0>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_total_n_constant_within_each_query_class(self, result):
        """In the downstream direction the presynaptic side is the queried
        class, so (matching VFB_connect's normalization) `total_n` is the
        queried (sub)class instance count: constant within each query block (it
        varies between blocks), and `connected_n` never exceeds it.
        """
        from collections import defaultdict
    
        rows = result["rows"]
>       assert rows, "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_downstream_class_connectivity.py:183: AssertionError
_ TestDownstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f2c871b04c0>
result = {'headers': {}, 'rows': [], 'count': 0}

    @pytest.mark.integration
    def test_no_rows_above_neuron_root(self, result):
        """The partner-side ancestor walk should stop at the Neuron class
        (FBbt_00005106). No row id should be a class outside the Neuron
        subtree.
        """
        from vfbquery.vfb_queries import vc, get_dict_cursor, NEURON_ROOT_SHORT_FORM
    
        ids = [r["id"] for r in result["rows"]]
>       assert ids, "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_downstream_class_connectivity.py:245: AssertionError
______________ TestListConnectomeDatasets.test_hemibrain_present _______________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_vfb_connectivity.TestListConnectomeDatasets object at 0x7f2c8718dde0>

    @pytest.mark.integration
    def test_hemibrain_present(self):
        datasets = list_connectome_datasets()
        symbols = [d["symbol"] for d in datasets]
>       assert "hb" in symbols
E       AssertionError: assert 'hb' in []

src/test/test_vfb_connectivity.py:32: AssertionError
_________ TestUpstreamClassConnectivityDict.test_row_has_expected_keys _________
[gw4] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7f4d5abc4e80>

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
        result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
>       assert result["rows"], "Expected at least one row"
E       AssertionError: Expected at least one row
E       assert []

src/test/test_upstream_class_connectivity.py:39: AssertionError
___________ TestNeuronNeuronConnectivityDict.test_direction_upstream ___________
[gw3] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDict object at 0x7f442f36a830>

    @pytest.mark.integration
    def test_direction_upstream(self):
>       all_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False
        )

src/test/test_neuron_neuron_connectivity.py:61: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3237: in get_neuron_neuron_connectivity
    results = vc.nc.commit_list([main_cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f442f36beb0>
statements = ['\n    MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n    MATCH (oi:Individual)-[r:synapsed_to]-(primary)...nat.label END, template_anat.short_form + "," + oi.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
__________ TestNeuronNeuronConnectivityDict.test_direction_downstream __________
[gw3] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDict object at 0x7f442f36ab00>

    @pytest.mark.integration
    def test_direction_downstream(self):
>       all_result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False
        )

src/test/test_neuron_neuron_connectivity.py:72: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3237: in get_neuron_neuron_connectivity
    results = vc.nc.commit_list([main_cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f442f36beb0>
statements = ['\n    MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n    MATCH (oi:Individual)-[r:synapsed_to]-(primary)...nat.label END, template_anat.short_form + "," + oi.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
____________ TestNeuronNeuronConnectivityDict.test_headers_present _____________
[gw1] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDict object at 0x7f310c391ea0>

    @pytest.mark.integration
    def test_headers_present(self):
>       result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, limit=1
        )

src/test/test_neuron_neuron_connectivity.py:43: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3237: in get_neuron_neuron_connectivity
    results = vc.nc.commit_list([main_cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f3120e80be0>
statements = ['\n    MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n    MATCH (oi:Individual)-[r:synapsed_to]-(primary)...nat.label END, template_anat.short_form + "," + oi.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
____________ TestNeuronNeuronConnectivityDict.test_limit_respected _____________
[gw1] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDict object at 0x7f310c392170>

    @pytest.mark.integration
    def test_limit_respected(self):
>       result = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=False, limit=3
        )

src/test/test_neuron_neuron_connectivity.py:53: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:922: in wrapper
    return func(*args, **kwargs)
src/vfbquery/vfb_queries.py:3237: in get_neuron_neuron_connectivity
    results = vc.nc.commit_list([main_cypher])
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.owlery_client.MockNeo4jClient object at 0x7f3120e80be0>
statements = ['\n    MATCH (primary:Individual {short_form: \'VFB_jrchk00s\'})\n    MATCH (oi:Individual)-[r:synapsed_to]-(primary)...nat.label END, template_anat.short_form + "," + oi.short_form]), "[![null]( \'null\')](null)", "") AS thumbnail\n    ']

    def commit_list(self, statements):
>       raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )
E       NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.

src/vfbquery/owlery_client.py:306: NotImplementedError
_______________ TestListConnectomeDatasets.test_returns_datasets _______________
[gw6] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_vfb_connectivity.TestListConnectomeDatasets object at 0x7f5e397c51b0>

    @pytest.mark.integration
    def test_returns_datasets(self):
>       datasets = list_connectome_datasets()

src/test/test_vfb_connectivity.py:18: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:79: in list_connectome_datasets
    nc = _get_nc()
src/vfbquery/vfb_connectivity.py:11: in _get_nc
    return Neo4jConnect()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.neo4j_client.Neo4jConnect object at 0x7f5e383f4af0>
endpoint = 'http://pdb.virtualflybrain.org', usr = 'neo4j', pwd = 'vfb'

    def __init__(self,
                 endpoint: str = "http://pdb.virtualflybrain.org",
                 usr: str = "neo4j",
                 pwd: str = "vfb"):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        self.commit = "/db/neo4j/tx/commit"
        self.headers = {'Content-type': 'application/json'}
    
        # Test connection and fall back to v3 API if needed
        if not self.test_connection():
            print("Falling back to Neo4j v3 connection")
            self.commit = "/db/data/transaction/commit"
            self.headers = {}
            if not self.test_connection():
>               raise Exception("Failed to connect to Neo4j.")
E               Exception: Failed to connect to Neo4j.

src/vfbquery/neo4j_client.py:59: Exception
____________ TestUpstreamClassConnectivityDict.test_headers_present ____________
[gw4] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7f4d5abc5150>

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
        assert "headers" in result
>       assert "upstream_class" in result["headers"]
E       AssertionError: assert 'upstream_class' in {}

src/test/test_upstream_class_connectivity.py:54: AssertionError
_________ TestQueryConnectivityKnown.test_known_connection_both_types __________
[gw7] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityKnown object at 0x7f2c8718fd30>

    @pytest.mark.integration
    def test_known_connection_both_types(self):
>       result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
        )

src/test/test_vfb_connectivity.py:49: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:139: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:179: in _query_connectivity_uncached
    nc = _get_nc()
src/vfbquery/vfb_connectivity.py:11: in _get_nc
    return Neo4jConnect()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.neo4j_client.Neo4jConnect object at 0x7f2c86d39ea0>
endpoint = 'http://pdb.virtualflybrain.org', usr = 'neo4j', pwd = 'vfb'

    def __init__(self,
                 endpoint: str = "http://pdb.virtualflybrain.org",
                 usr: str = "neo4j",
                 pwd: str = "vfb"):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        self.commit = "/db/neo4j/tx/commit"
        self.headers = {'Content-type': 'application/json'}
    
        # Test connection and fall back to v3 API if needed
        if not self.test_connection():
            print("Falling back to Neo4j v3 connection")
            self.commit = "/db/data/transaction/commit"
            self.headers = {}
            if not self.test_connection():
>               raise Exception("Failed to connect to Neo4j.")
E               Exception: Failed to connect to Neo4j.

src/vfbquery/neo4j_client.py:59: Exception
__ TestNeuronNeuronConnectivityDataFrame.test_dataframe_has_expected_columns ___
[gw2] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_neuron_neuron_connectivity.TestNeuronNeuronConnectivityDataFrame object at 0x7f1eac386ec0>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_neuron_neuron_connectivity(
            TEST_NEURON, return_dataframe=True, limit=1
        )
        expected_cols = {"id", "label", "outputs", "inputs", "tags"}
>       assert expected_cols.issubset(set(df.columns))
E       AssertionError: assert False
E        +  where False = <built-in method issubset of set object at 0x7f1eac3c3d80>(set())
E        +    where <built-in method issubset of set object at 0x7f1eac3c3d80> = {'id', 'inputs', 'label', 'outputs', 'tags'}.issubset
E        +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
E        +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns

src/test/test_neuron_neuron_connectivity.py:99: AssertionError
____ TestQueryConnectivityWeightFiltering.test_higher_weight_fewer_results _____
[gw5] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityWeightFiltering object at 0x7ff7fcbc57e0>

    @pytest.mark.integration
    def test_higher_weight_fewer_results(self):
>       result_low = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            weight=1,
        )

src/test/test_vfb_connectivity.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:139: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:179: in _query_connectivity_uncached
    nc = _get_nc()
src/vfbquery/vfb_connectivity.py:11: in _get_nc
    return Neo4jConnect()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.neo4j_client.Neo4jConnect object at 0x7ff811682170>
endpoint = 'http://pdb.virtualflybrain.org', usr = 'neo4j', pwd = 'vfb'

    def __init__(self,
                 endpoint: str = "http://pdb.virtualflybrain.org",
                 usr: str = "neo4j",
                 pwd: str = "vfb"):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        self.commit = "/db/neo4j/tx/commit"
        self.headers = {'Content-type': 'application/json'}
    
        # Test connection and fall back to v3 API if needed
        if not self.test_connection():
            print("Falling back to Neo4j v3 connection")
            self.commit = "/db/data/transaction/commit"
            self.headers = {}
            if not self.test_connection():
>               raise Exception("Failed to connect to Neo4j.")
E               Exception: Failed to connect to Neo4j.

src/vfbquery/neo4j_client.py:59: Exception
____________ TestUpstreamClassConnectivityDict.test_returns_results ____________
[gw0] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7f3911dbd330>

    @pytest.mark.integration
    def test_returns_results(self):
        result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )
        assert isinstance(result, dict)
>       assert result["count"] > 0
E       assert 0 > 0

src/test/test_upstream_class_connectivity.py:31: AssertionError
______ TestQueryConnectivityKnown.test_both_types_subset_of_either_alone _______
[gw4] linux -- Python 3.10.20 /opt/hostedtoolcache/Python/3.10.20/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityKnown object at 0x7f4d5abc7550>

    @pytest.mark.integration
    def test_both_types_subset_of_either_alone(self):
        result_both = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
        )
        result_up = query_connectivity(upstream_type=KNOWN_UPSTREAM)
>       result_down = query_connectivity(downstream_type=KNOWN_DOWNSTREAM)

src/test/test_vfb_connectivity.py:63: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/vfb_connectivity.py:139: in query_connectivity
    return _query_connectivity_uncached(
src/vfbquery/vfb_connectivity.py:179: in _query_connectivity_uncached
    nc = _get_nc()
src/vfbquery/vfb_connectivity.py:11: in _get_nc
    return Neo4jConnect()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <vfbquery.neo4j_client.Neo4jConnect object at 0x7f4d5659f5e0>
endpoint = 'http://pdb.virtualflybrain.org', usr = 'neo4j', pwd = 'vfb'

    def __init__(self,
                 endpoint: str = "http://pdb.virtualflybrain.org",
                 usr: str = "neo4j",
                 pwd: str = "vfb"):
        self.base_uri = endpoint
        self.usr = usr
        self.pwd = pwd
        self.commit = "/db/neo4j/tx/commit"
        self.headers = {'Content-type': 'application/json'}
    
        # Test connection and fall back to v3 API if needed
        if not self.test_connection():
            print("Falling back to Neo4j v3 connection")
            self.commit = "/db/data/transaction/commit"
            self.headers = {}
            if not self.test_connection():
>               raise Exception("Failed to connect to Neo4j.")
E               Exception: Failed to connect to Neo4j.

src/vfbquery/neo4j_client.py:59: Exception
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1312: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results - assert 0 > 0
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe - assert not True
 +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns - AssertionError: assert False
 +  where False = <built-in method issubset of set object at 0x7f5e38b3dd20>(set())
 +    where <built-in method issubset of set object at 0x7f5e38b3dd20> = {'avg_weight', 'connected_n', 'downstream_class', 'id', 'pairwise_connections', 'percent_connected', ...}.issubset
 +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
 +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe - assert not True
 +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner - AssertionError: Expected at least one row
assert []
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - AssertionError: Expected at least one row to test against
assert []
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - AssertionError: Expected the input term's own rows
assert 'FBbt_00001482' in set()
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - AssertionError: Expected at least one row
assert []
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results - assert 0 > 0
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys - AssertionError: Expected at least one row
assert []
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present - AssertionError: assert 'downstream_class' in {}
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe - assert not True
 +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns - AssertionError: assert False
 +  where False = <built-in method issubset of set object at 0x7f5e38b3e0a0>(set())
 +    where <built-in method issubset of set object at 0x7f5e38b3e0a0> = {'avg_weight', 'connected_n', 'downstream_class', 'id', 'pairwise_connections', 'percent_connected', ...}.issubset
 +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
 +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - AssertionError: Expected at least one row to test against
assert []
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - AssertionError: Expected the input term's own rows
assert 'FBbt_00001482' in set()
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class - AssertionError: Expected at least one row
assert []
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - AssertionError: Expected at least one row
assert []
FAILED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present - AssertionError: assert 'hb' in []
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys - AssertionError: Expected at least one row
assert []
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected - NotImplementedError: Neo4j queries are not available. Either Neo4j server is unavailable or connection failed.
FAILED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets - Exception: Failed to connect to Neo4j.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present - AssertionError: assert 'upstream_class' in {}
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types - Exception: Failed to connect to Neo4j.
FAILED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns - AssertionError: assert False
 +  where False = <built-in method issubset of set object at 0x7f1eac3c3d80>(set())
 +    where <built-in method issubset of set object at 0x7f1eac3c3d80> = {'id', 'inputs', 'label', 'outputs', 'tags'}.issubset
 +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
 +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results - Exception: Failed to connect to Neo4j.
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results - assert 0 > 0
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone - Exception: Failed to connect to Neo4j.
============ 34 failed, 23 passed, 4 warnings in 2401.09s (0:40:01) ============
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 76
- **Passed**: 42 ✅
- **Failed**: 34 ❌
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
*Last updated: 2026-06-19 07:53:41 UTC*
