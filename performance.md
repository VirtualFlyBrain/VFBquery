# VFBquery Performance Test Results

**Test Date:** 2026-05-29 20:23:43 UTC
**Git Commit:** ab0bc15cbb8c3e58d9c86434dd4b135d6ddc4c02
**Branch:** main
**Workflow Run:** [26659171834](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26659171834)

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
Test dataset and template queries ... FAIL
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

======================================================================
FAIL: test_13_dataset_template_queries (src.test.test_query_performance.QueryPerformanceTest)
Test dataset and template queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 755, in test_13_dataset_template_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "AllDatasets exceeded threshold")
AssertionError: 5.441993474960327 not less than 3.0 : AllDatasets exceeded threshold

----------------------------------------------------------------------
Ran 18 tests in 88.632s

FAILED (failures=1)
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 3.2223s ✅
get_term_info (individual): 2.0572s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 2.5059s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.1622s ✅
NeuronsPresynapticHere: 2.0825s ✅
NeuronsPostsynapticHere: 2.1334s ✅
NeuronNeuronConnectivity: 1.9596s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.9527s ✅
PartsOf: 1.7740s ✅
SubclassesOf: 1.7964s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 2.1613s ✅
TractsNervesInnervatingHere: 1.7885s ✅
LineageClonesIn: 1.9727s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.2617s ✅
ImagesThatDevelopFrom: 2.2497s ✅
epFrag: 1.7802s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 1.7841s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.8248s ✅
NeuronRegionConnectivityQuery: 1.7945s ✅

================================================================================
DOWNSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
DownstreamClassConnectivity: 1.8483s ✅

================================================================================
UPSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
UpstreamClassConnectivity: 1.8154s ✅

================================================================================
CROSS-DATASET CONNECTIVITY (live, slow)
================================================================================
QueryConnectivity: 2.0299s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 0.9374s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.0870s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.2417s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.9102s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 1.6148s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 0.8725s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.8810s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.0077s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.7945s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 1.1114s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.8209s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.8196s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.8848s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.7800s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 3.2766s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 0.9746s ✅
  └─ Found 86 aligned datasets, returned 10
AllDatasets: 5.4420s ✅
  └─ Found 130 total datasets, returned 20

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.8802s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 1.5338s ✅
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
Ran 1 test in 3.732s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1.8060 seconds
VFB_00101567 query took: 1.9252 seconds
Total time for both queries: 3.7313 seconds
Performance Level: 🟠 Acceptable (3-6 seconds)
==================================================
Performance test completed successfully!
============================= test session starts ==============================
platform linux -- Python 3.10.20, pytest-9.0.3, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.20/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
collecting ... collected 55 items

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results PASSED [  1%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys PASSED [  3%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present PASSED [  5%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected PASSED [  7%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream PASSED [  9%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream PASSED [ 10%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe PASSED [ 12%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 14%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected PASSED [ 16%]
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation PASSED [ 18%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results PASSED [ 20%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys PASSED [ 21%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present PASSED [ 23%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected PASSED [ 25%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe PASSED [ 27%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 29%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected PASSED [ 30%]
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation PASSED [ 32%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results PASSED [ 34%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys PASSED [ 36%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present PASSED [ 38%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected PASSED [ 40%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero PASSED [ 41%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe PASSED [ 43%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 45%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected PASSED [ 47%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe PASSED [ 49%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts PASSED [ 50%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows PASSED [ 52%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root PASSED [ 54%]
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation PASSED [ 56%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results PASSED [ 58%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys PASSED [ 60%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present PASSED [ 61%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected PASSED [ 63%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero PASSED [ 65%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe PASSED [ 67%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns PASSED [ 69%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected PASSED [ 70%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe PASSED [ 72%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts PASSED [ 74%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_is_constant_across_rows PASSED [ 76%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root PASSED [ 78%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation PASSED [ 80%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets PASSED [ 81%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol PASSED [ 83%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present PASSED [ 85%]
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol PASSED [ 87%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types PASSED [ 89%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone PASSED [ 90%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class PASSED [ 92%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results PASSED [ 94%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results PASSED [ 96%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning PASSED [ 98%]
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error PASSED [100%]

=============================== warnings summary ===============================
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:582: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(default=default, dump_default=dump_default, **kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:986: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:776: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:137
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:137: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    output_format = fields.String(required=False, missing='table')

../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
../../../../../opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218
  /opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/marshmallow/fields.py:1218: RemovedInMarshmallow4Warning: The 'missing' argument to fields is deprecated. Use 'load_default' instead.
    super().__init__(**kwargs)

src/vfbquery/vfb_queries.py:307
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:307: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False)

src/vfbquery/vfb_queries.py:308
  /home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py:308: ChangedInMarshmallow4Warning: `Field` should not be instantiated. Use `fields.Raw` or  another field subclass instead.
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Field()), required=False, allow_none=True)

src/test/test_neuron_neuron_connectivity.py:22
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:22: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:31
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:31: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:41
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:41: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:51
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:51: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:59
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:59: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:70
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:70: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:93
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:93: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_neuron_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_neuron_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:23
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:23: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:32
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:32: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:42
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:42: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:52
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:52: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:72
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:72: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_neuron_region_connectivity.py:80
  /home/runner/work/VFBquery/VFBquery/src/test/test_neuron_region_connectivity.py:80: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:124
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:124: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:168
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:168: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_upstream_class_connectivity.py:181
  /home/runner/work/VFBquery/VFBquery/src/test/test_upstream_class_connectivity.py:181: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:25
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:25: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:55
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:55: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:64
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:64: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:76
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:76: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:84
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:84: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:95
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:95: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:102
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:102: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:123
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:123: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:171
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:171: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_downstream_class_connectivity.py:185
  /home/runner/work/VFBquery/VFBquery/src/test/test_downstream_class_connectivity.py:185: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:16
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:16: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:21
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:21: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:28
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:28: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:34
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:34: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:47
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:47: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:56
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:56: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:71
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:71: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:85
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:85: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:101
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:101: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

src/test/test_vfb_connectivity.py:114
  /home/runner/work/VFBquery/VFBquery/src/test/test_vfb_connectivity.py:114: PytestUnknownMarkWarning: Unknown pytest.mark.integration - is this a typo?  You can register custom marks to avoid this warning - for details, see https://docs.pytest.org/en/stable/how-to/mark.html
    @pytest.mark.integration

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================= 55 passed, 64 warnings in 1375.22s (0:22:55) =================
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-29 20:23:43 UTC*
