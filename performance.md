# VFBquery Performance Test Results

**Test Date:** 2026-05-28 07:05:50 UTC
**Git Commit:** d0018aa405662802ed041d52c21a6cc21780fda5
**Branch:** main
**Workflow Run:** [26557757296](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/26557757296)

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
Test dataset and template queries ... ok
test_14_publication_transgene_queries (src.test.test_query_performance.QueryPerformanceTest)
Test publication and transgene queries ... ok

----------------------------------------------------------------------
Ran 18 tests in 134.325s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

🔥 SOLR caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
get_term_info (mushroom body): 6.1410s ✅
get_term_info (individual): 6.0859s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 6.9535s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.8994s ✅
NeuronsPresynapticHere: 2.3585s ✅
NeuronsPostsynapticHere: 2.4734s ✅
NeuronNeuronConnectivity: 2.7049s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 2.1980s ✅
PartsOf: 2.6747s ✅
SubclassesOf: 3.1493s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 3.7257s ✅
TractsNervesInnervatingHere: 3.8040s ✅
LineageClonesIn: 2.0089s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 3.6302s ✅
ImagesThatDevelopFrom: 2.3138s ✅
epFrag: 2.8265s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 5.6657s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 3.8148s ✅
NeuronRegionConnectivityQuery: 1.9827s ✅

================================================================================
DOWNSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
DownstreamClassConnectivity: 4.0141s ✅

================================================================================
UPSTREAM CLASS CONNECTIVITY (multi-step aggregation)
================================================================================
UpstreamClassConnectivity: 2.0182s ✅

================================================================================
CROSS-DATASET CONNECTIVITY (live, slow)
================================================================================
QueryConnectivity: 1.8851s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 1.0389s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 5.0821s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.8291s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 1.2635s ✅
  └─ Found 57 total clusters, returned 10
clusterExpression: 2.8978s ✅
  └─ Found 4588 genes expressed, returned 10
expressionCluster: 1.1102s ✅
  └─ Found 9 clusters expressing gene
scRNAdatasetData: 0.9274s ✅
  └─ Found 13 clusters in dataset, returned 10

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.1088s ✅
  └─ Found 215 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 1.0538s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.9900s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.8449s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.8571s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 1.0013s ✅
  └─ Found 46 painted domains, returned 10
DatasetImages: 0.9788s ✅
  └─ Found 46 images in dataset, returned 10
AllAlignedImages: 3.7387s ✅
  └─ Found 527179 aligned images, returned 10
AlignedDatasets: 1.4548s ✅
  └─ Found 86 aligned datasets, returned 10
AllDatasets: 1.2864s ✅
  └─ Found 130 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 1.2238s ✅
  └─ Found 2 terms for publication
TransgeneExpressionHere: 2.0046s ✅
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
Ran 1 test in 6.414s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 2.5889 seconds
VFB_00101567 query took: 3.8245 seconds
Total time for both queries: 6.4134 seconds
Performance Level: 🔴 Slow (> 6 seconds)
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
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present FAILED [ 61%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected PASSED [ 63%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero PASSED [ 65%]
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe FAILED [ 67%]
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

=================================== FAILURES ===================================
___________ TestDownstreamClassConnectivityDict.test_headers_present ___________

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f42647e6710>

    @pytest.mark.integration
    def test_headers_present(self):
        result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )
        assert "headers" in result
>       assert "downstream_class" in result["headers"]
E       AssertionError: assert 'downstream_class' in {}

src/test/test_downstream_class_connectivity.py:53: AssertionError
----------------------------- Captured stdout call -----------------------------
Bulk per-instance cache fetch failed (_dataframe_False): Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
Warning: per-instance connectivity cache missing for 107/107 instances of FBbt_00001482; those will be skipped (results may be a slight underestimate).
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:344 Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 534, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connection.py", line 571, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 1395, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 323, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 284, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/socket.py", line 717, in readinto
    return self._sock.recv_into(b)
TimeoutError: [Errno 110] Connection timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 696, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 842, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 498, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 788, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 367, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 334, in _send_request
    resp = requests_method(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 712, in post
    return self.request("POST", url, data=data, json=json, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 651, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 784, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 742, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
_______ TestDownstreamClassConnectivityDataFrame.test_returns_dataframe ________

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f42647e5c90>

    @pytest.mark.integration
    def test_returns_dataframe(self):
        df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )
        assert isinstance(df, pd.DataFrame)
>       assert not df.empty
E       assert not True
E        +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty

src/test/test_downstream_class_connectivity.py:82: AssertionError
----------------------------- Captured stdout call -----------------------------
Error querying Solr for downstream_connectivity_query: Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/?q=id%3A%2A&fq=%7B%21terms+f%3Did%7DFBbt_00001482%2CFBbt_20009301%2CFBbt_20009313%2CFBbt_20009302%2CFBbt_00047819%2CFBbt_20009333%2CFBbt_20009300%2CFBbt_20009305%2CFBbt_20009306%2CFBbt_20009303%2CFBbt_00048628%2CFBbt_00047019%2CFBbt_20009297%2CFBbt_00047852%2CFBbt_20009298%2CFBbt_20009362%2CFBbt_00047020%2CFBbt_20009309%2CFBbt_20009308&fl=downstream_connectivity_query&rows=19&wt=json' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:457 Error clearing cache entry: HTTPSConnectionPool(host='solr.virtualflybrain.org', port=443): Read timed out. (read timeout=5)
WARNING  vfbquery.solr_result_cache:solr_result_cache.py:403 Solr cache write failed; disabling cache for 60s: HTTPSConnectionPool(host='solr.virtualflybrain.org', port=443): Read timed out. (read timeout=30)
ERROR    pysolr:pysolr.py:344 Connection to server 'http://solr.virtualflybrain.org/solr/vfb_json/select/?q=id%3A%2A&fq=%7B%21terms+f%3Did%7DFBbt_00001482%2CFBbt_20009301%2CFBbt_20009313%2CFBbt_20009302%2CFBbt_00047819%2CFBbt_20009333%2CFBbt_20009300%2CFBbt_20009305%2CFBbt_20009306%2CFBbt_20009303%2CFBbt_00048628%2CFBbt_00047019%2CFBbt_20009297%2CFBbt_00047852%2CFBbt_20009298%2CFBbt_20009362%2CFBbt_00047020%2CFBbt_20009309%2CFBbt_20009308&fl=downstream_connectivity_query&rows=19&wt=json' timed out: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 534, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connection.py", line 571, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 1395, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 323, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/http/client.py", line 284, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/socket.py", line 717, in readinto
    return self._sock.recv_into(b)
TimeoutError: [Errno 110] Connection timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 696, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 842, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 498, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 788, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 367, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/pysolr.py", line 334, in _send_request
    resp = requests_method(
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 671, in get
    return self.request("GET", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 651, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/sessions.py", line 784, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.20/x64/lib/python3.10/site-packages/requests/adapters.py", line 742, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='solr.virtualflybrain.org', port=80): Read timed out. (read timeout=990)
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
=========================== short test summary info ============================
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present - AssertionError: assert 'downstream_class' in {}
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe - assert not True
 +  where True = Empty DataFrame\nColumns: []\nIndex: [].empty
============ 2 failed, 53 passed, 64 warnings in 3570.78s (0:59:30) ============
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures


---

## Historical Performance

Track performance trends across commits:
- [GitHub Actions History](https://github.com/VirtualFlyBrain/VFBquery/actions/workflows/performance-test.yml)

---
*Last updated: 2026-05-28 07:05:50 UTC*
