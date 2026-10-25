# VFBquery Performance Test Results

**Test Date:** 2026-10-25 02:19:57 UTC
**Git Commit:** 400f86596ee72b0074f27240f57450f288f56fe8
**Branch:** main
**Workflow Run:** [40153278072](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/40153278072)

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
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
============================= test session starts ==============================
platform linux -- Python 3.10.22, pytest-9.1.1, pluggy-1.7.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: platformdirs-4.12.4, timeout-2.4.0, xdist-3.8.0
timeout: 300.0s
timeout method: signal
timeout func_only: False
created: 4/4 workers
4 workers [18 items]

scheduling tests via LoadScheduling

src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw0] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 5764, in _owlery_query_to_results
    results = vfb_solr.search(
  File "/opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/pysolr.py", line 735, in search
    response = self._select(params, handler=search_handler)
  File "/opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/pysolr.py", line 413, in _select
    return self._send_request(
  File "/opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/pysolr.py", line 381, in _send_request
    raise SolrError(error_message % (resp.status_code, solr_message))
pysolr.SolrError: Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>

[gw2] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

=================================== FAILURES ===================================
________________ QueryPerformanceTest.test_01_term_info_queries ________________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_01_term_info_queries>

    def test_01_term_info_queries(self):
        """Test term info query performance"""
        print("\n" + "="*80)
        print("TERM INFO QUERIES")
        print("="*80)
    
        # Test basic term info retrieval
>       result, duration, success = self._time_query(
            "get_term_info (mushroom body)",
            get_term_info,
            self.test_terms['mushroom_body'],
            preview=True
        )

src/test/test_query_performance.py:128: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/test/test_query_performance.py:108: in _time_query
    self.assertIsNotNone(result, f"{query_name} returned None")
E   AssertionError: unexpectedly None : get_term_info (mushroom body) returned None
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
____________ QueryPerformanceTest.test_04_anatomy_hierarchy_queries ____________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_04_anatomy_hierarchy_queries>

    def test_04_anatomy_hierarchy_queries(self):
        """Test anatomical hierarchy queries"""
        print("\n" + "="*80)
        print("ANATOMICAL HIERARCHY QUERIES")
        print("="*80)
    
        test_term = self.test_terms['mushroom_body']
    
        result, duration, success = self._time_query(
            "ComponentsOf",
            get_components_of,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"ComponentsOf: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_SLOW, "ComponentsOf exceeded threshold")
    
        result, duration, success = self._time_query(
            "PartsOf",
            get_parts_of,
            test_term,
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )
        print(f"PartsOf: {duration:.4f}s {'✅' if success else '❌'}")
        self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "PartsOf exceeded threshold")
    
>       result, duration, success = self._time_query(
            "SubclassesOf",
            get_subclasses_of,
            "FBbt_00048516",  # wedge projection neuron has ~56 subclasses
            # (mushroom body / test_term is a leaf with none, which returned 0)
            return_dataframe=False,
            limit=-1  # Enable caching for performance tests
        )

src/test/test_query_performance.py:241: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/test/test_query_performance.py:110: in _time_query
    self.assertGreater(self._result_size(result), 0,
E   AssertionError: 0 not greater than 0 : SubclassesOf returned no rows
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:751 Failed to cache result: HTTP 401 - <html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 401 Authentication failed, Response code: 401</title>
</head>
<body><h2>HTTP ERROR 401 Authentication failed, Response code: 401</h2>
<table>
<tr><th>URI:</th><td>/solr/vfbquery_cache/update</td></tr>
<tr><th>STATUS:</th><td>401</td></tr>
<tr><th>MESSAGE:</th><td>Authentication failed, Response code: 401</td></tr>
<tr><th>SERVLET:</th><td>default</td></tr>
</table>

</body>
</html>

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:751 Failed to cache result: HTTP 404 - <!--
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->
<p>
  Searching for Solr?<br/>
  You must type the correct path.<br/>
  Solr will respond.
</p>

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:751 Failed to cache result: HTTP 401 - <html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 401 Authentication failed, Response code: 401</title>
</head>
<body><h2>HTTP ERROR 401 Authentication failed, Response code: 401</h2>
<table>
<tr><th>URI:</th><td>/solr/vfbquery_cache/update</td></tr>
<tr><th>STATUS:</th><td>401</td></tr>
<tr><th>MESSAGE:</th><td>Authentication failed, Response code: 401</td></tr>
<tr><th>SERVLET:</th><td>default</td></tr>
</table>

</body>
</html>

ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
WARNING  vfbquery.solr_result_cache:solr_result_cache.py:1565 Not caching result with count > 0 but no rows for subclasses_of(FBbt_00048516)
____________ QueryPerformanceTest.test_13_dataset_template_queries _____________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_13_dataset_template_queries>

    def test_13_dataset_template_queries(self):
        """Test dataset and template queries"""
        print("\n" + "="*80)
        print("DATASET/TEMPLATE QUERIES")
        print("="*80)
    
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_painted_domains,
            get_dataset_images,
            get_all_aligned_images,
            get_aligned_datasets,
            get_all_datasets
        )
    
        # Test terms for templates and datasets
        template_term = 'VFB_00101567'  # Adult Brain template
        dataset_term = 'JRC2018'   # Example dataset
    
        # PaintedDomains - Template painted anatomy domains
        # Warm up cache with full results
        try:
            get_painted_domains(template_term, return_dataframe=False, limit=-1)
        except Exception:
            pass  # Ignore warm-up failures
    
        result, duration, success = self._time_query(
            "PaintedDomains",
            get_painted_domains,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"PaintedDomains: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} painted domains" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "PaintedDomains exceeded threshold")
    
        # DatasetImages - Images in a dataset
        result, duration, success = self._time_query(
            "DatasetImages",
            get_dataset_images,
            dataset_term,
            return_dataframe=False,
            limit=10
        )
        print(f"DatasetImages: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} images in dataset" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "DatasetImages exceeded threshold")
    
        # AllAlignedImages - All images aligned to template
        result, duration, success = self._time_query(
            "AllAlignedImages",
            get_all_aligned_images,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"AllAlignedImages: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} aligned images" + (", returned 10" if count > 10 else ""))
        # AllAlignedImages computes the full aligned-image set for the template
        # (~398MB for a major template), which exceeds the 10MB result-cache cap,
        # so it is never cached and is recomputed live on every call — observed
        # ~120-155s on CI, even on the writable warming run (the limit=10 above
        # doesn't help: the cache layer computes the full result before slicing).
        # Allow a cold-realistic budget until the result size is reduced so it
        # can cache; see get_all_aligned_images.
        self.assertLess(duration, 240.0, "AllAlignedImages exceeded threshold")
    
        # AlignedDatasets - All datasets aligned to template
        # Warm up cache with full results
        try:
            get_aligned_datasets(template_term, return_dataframe=False, limit=-1)
        except Exception:
            pass  # Ignore warm-up failures
    
        result, duration, success = self._time_query(
            "AlignedDatasets",
            get_aligned_datasets,
            template_term,
            return_dataframe=False,
            limit=10
        )
        print(f"AlignedDatasets: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} aligned datasets" + (", returned 10" if count > 10 else ""))
>       self.assertLess(duration, self.THRESHOLD_MEDIUM, "AlignedDatasets exceeded threshold")
E       AssertionError: 17.06182098388672 not less than 3.0 : AlignedDatasets exceeded threshold

src/test/test_query_performance.py:784: AssertionError
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:751 Failed to cache result: HTTP 401 - <html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=ISO-8859-1"/>
<title>Error 401 Authentication failed, Response code: 401</title>
</head>
<body><h2>HTTP ERROR 401 Authentication failed, Response code: 401</h2>
<table>
<tr><th>URI:</th><td>/solr/vfbquery_cache/update</td></tr>
<tr><th>STATUS:</th><td>401</td></tr>
<tr><th>MESSAGE:</th><td>Authentication failed, Response code: 401</td></tr>
<tr><th>SERVLET:</th><td>default</td></tr>
</table>

</body>
</html>
=========================== short test summary info ============================
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries - AssertionError: unexpectedly None : get_term_info (mushroom body) returned None
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries - AssertionError: 0 not greater than 0 : SubclassesOf returned no rows
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries - AssertionError: 17.06182098388672 not less than 3.0 : AlignedDatasets exceeded threshold
======================== 3 failed, 15 passed in 29.59s =========================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.154s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.5690 seconds
VFB_00101567 query took: 0.5845 seconds
Total time for both queries: 1.1535 seconds
Performance Level: 🟢 Excellent (< 1.5 seconds)
==================================================
Performance test completed successfully!
=== CONNECTIVITY RETRY ATTEMPT ===
============================= test session starts ==============================
platform linux -- Python 3.10.22, pytest-9.1.1, pluggy-1.7.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
cachedir: .pytest_cache
rootdir: /home/runner/work/VFBquery/VFBquery
configfile: pyproject.toml
plugins: platformdirs-4.12.4, timeout-2.4.0, xdist-3.8.0
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
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw1] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
[gw1] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw0] ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw1] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw0] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw1] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw1] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw1] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw3] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw0] ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 
[gw2] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw2] ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw2] ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw2] ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 

==================================== ERRORS ====================================
_ ERROR at setup of TestUpstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7f8965707460>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_upstream_class_connectivity.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log setup ------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f974494c730>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:160: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log setup ------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_total_n_constant_within_each_query_class _
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f974494c730>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:160: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f974494c730>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:160: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
_ ERROR at setup of TestDownstreamClassConnectivityHierarchyRollup.test_no_rows_above_neuron_root _
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityHierarchyRollup object at 0x7f8965747310>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_downstream_class_connectivity.py:160: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log setup ------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_ ERROR at setup of TestUpstreamClassConnectivityHierarchyRollup.test_parent_class_appears_with_sensible_counts _
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7fe82e1173d0>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_upstream_class_connectivity.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log setup ------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_ ERROR at setup of TestUpstreamClassConnectivityHierarchyRollup.test_total_n_is_per_partner _
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7fe82e1173d0>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_upstream_class_connectivity.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
_ ERROR at setup of TestUpstreamClassConnectivityHierarchyRollup.test_includes_subclass_breakdown _
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityHierarchyRollup object at 0x7fe82e1173d0>

    @pytest.fixture(scope='class')
    def result(self):
>       return get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True,
        )

src/test/test_upstream_class_connectivity.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
=================================== FAILURES ===================================
___ TestNeuronRegionConnectivityAttachment.test_query_attached_to_term_info ____
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityAttachment object at 0x7f974494e110>

    @pytest.mark.integration
    def test_query_attached_to_term_info(self):
        """Regression: the query must be offered on a neuron's term-info page.
    
        NeuronRegionConnectivityQuery_to_schema existed and worked, but was
        never called from get_term_info, so the query never appeared on any
        term. The gate is has_region_connectivity in the neuron's SuperTypes.
        """
        term_info = get_term_info(TEST_NEURON)
>       query_names = {q.get("query") for q in term_info.get("Queries", [])}
E       AttributeError: 'NoneType' object has no attribute 'get'

src/test/test_neuron_region_connectivity.py:131: AttributeError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
____________ TestUpstreamClassConnectivityDict.test_returns_results ____________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7f974494f5b0>

    @pytest.mark.integration
    def test_returns_results(self):
>       result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
___________ TestDownstreamClassConnectivityDict.test_returns_results ___________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f8965707520>

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
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
___________ TestDownstreamClassConnectivityDict.test_headers_present ___________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f974496ce80>

    @pytest.mark.integration
    def test_headers_present(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:89: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
________ TestDownstreamClassConnectivityDict.test_row_has_expected_keys ________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f8965768310>

    @pytest.mark.integration
    def test_row_has_expected_keys(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:75: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
___________ TestDownstreamClassConnectivityDict.test_limit_respected ___________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f974496c880>

    @pytest.mark.integration
    def test_limit_respected(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, limit=3, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:97: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_ TestDownstreamClassConnectivityDataFrame.test_dataframe_has_expected_columns _
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f896576a620>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
>       df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=1, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:126: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_______ TestDownstreamClassConnectivityDataFrame.test_returns_dataframe ________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f974496dfc0>

    @pytest.mark.integration
    def test_returns_dataframe(self):
>       df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:118: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
________ TestDownstreamClassConnectivityDataFrame.test_limit_respected _________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDataFrame object at 0x7f896576a980>

    @pytest.mark.integration
    def test_limit_respected(self):
>       df = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=5, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:138: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5155: in get_downstream_class_connectivity
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
_________ TestUpstreamClassConnectivityDataFrame.test_limit_respected __________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDataFrame object at 0x7fe82e15b640>

    @pytest.mark.integration
    def test_limit_respected(self):
>       df = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=True, limit=5, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:138: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1199: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1192: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5229: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
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
>               raise ConnectivityBackendError(
                    f"No partner classes resolved for {short_form} although its "
                    f"instances have {direction} connectivity"
                )
E               vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity

src/vfbquery/vfb_queries.py:4956: ConnectivityBackendError
------------------------------ Captured log call -------------------------------
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
ERROR    pysolr:pysolr.py:368 Solr responded with an error (HTTP 404): [Reason: None]
<p>  Searching for Solr?  You must type the correct path.  Solr will respond.</p>
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
  /opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info - AttributeError: 'NoneType' object has no attribute 'get'
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
ERROR src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have downstream connectivity
ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
ERROR src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown - vfbquery.vfb_queries.ConnectivityBackendError: No partner classes resolved for FBbt_00001482 although its instances have upstream connectivity
======= 10 failed, 60 passed, 6 warnings, 8 errors in 214.10s (0:03:34) ========
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 108
- **Passed**: 76 ✅
- **Failed**: 32 ❌
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
*Last updated: 2026-10-25 02:19:57 UTC*
