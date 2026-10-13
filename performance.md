# VFBquery Performance Test Results

**Test Date:** 2026-10-13 09:35:02 UTC
**Git Commit:** 66af6b49d7f3b425bf5281fadd4dd0a1adb9fa91
**Branch:** main
**Workflow Run:** [38371338116](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/38371338116)

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
platform linux -- Python 3.10.22, pytest-9.1.1, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
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
src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_01_term_info_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
[gw0] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_02_neuron_part_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05_tract_lineage_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_06_instance_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_03_synaptic_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07_connectivity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_04_anatomy_hierarchy_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries INFO: Owlery query returned 400 Bad Request (invalid for this term type): <http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/FBtp0000001>

[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_05b_image_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
[gw3] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_08_similarity_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
[gw2] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_07c_cross_dataset_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
[gw1] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw1] PASSED src/test/test_query_performance.py::QueryPerformanceTest::test_11_transcriptomics_queries 
[gw2] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity 
src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw2] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries 
[gw0] FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity 
[gw3] SKIPPED src/test/test_query_performance.py::QueryPerformanceTest::test_10_expression_queries 
src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 
[gw3] SKIPPED src/test/test_query_performance.py::QueryPerformanceTest::test_13_dataset_template_queries 

=================================== FAILURES ===================================
______________ QueryPerformanceTest.test_09_neuron_input_queries _______________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_09_neuron_input_queries>

    def test_09_neuron_input_queries(self):
        """Test neuron input/synapse queries"""
        print("\n" + "="*80)
        print("NEURON INPUT QUERIES (Neo4j)")
        print("="*80)
    
        # NeuronInputsTo
        # Warm up cache with full results
        try:
            get_individual_neuron_inputs(self.test_terms['connected_neuron'], return_dataframe=False, limit=-1)
        except Exception:
            pass  # Ignore warm-up failures
    
        result, duration, success = self._time_query(
            "NeuronInputsTo",
            get_individual_neuron_inputs,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=5
        )
        print(f"NeuronInputsTo: {duration:.4f}s {'✅' if success else '❌'}")
>       self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronInputsTo exceeded threshold")
E       AssertionError: 25.8081157207489 not less than 15.0 : NeuronInputsTo exceeded threshold

src/test/test_query_performance.py:485: AssertionError
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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
_________________ QueryPerformanceTest.test_12_nblast_queries __________________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_12_nblast_queries>

    def test_12_nblast_queries(self):
        """Test NBLAST similarity queries"""
        print("\n" + "="*80)
        print("NBLAST SIMILARITY QUERIES")
        print("="*80)
    
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_similar_morphology,
            get_similar_morphology_part_of,
            get_similar_morphology_part_of_exp,
            get_similar_morphology_nb,
            get_similar_morphology_nb_exp,
            get_similar_morphology_userdata
        )
    
        # SimilarMorphologyTo - NBLAST matches
        # Warm up cache with full results
        try:
            get_similar_morphology(self.test_terms['connected_neuron'], return_dataframe=False, limit=-1)
        except Exception:
            pass  # Ignore warm-up failures
    
        result, duration, success = self._time_query(
            "SimilarMorphologyTo",
            get_similar_morphology,
            self.test_terms['connected_neuron'],  # LPC1 neuron with NBLAST data
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyTo: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NBLAST matches" + (", returned 10" if count > 10 else ""))
        # NBLAST queries can be slightly slower due to database complexity
        self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
    
        # SimilarMorphologyToPartOf - NBLASTexp to expression patterns
        result, duration, success = self._time_query(
            "SimilarMorphologyToPartOf",
            get_similar_morphology_part_of,
            "VFB_00016103",  # neuron with NBLASTexp matches (VFB_jrchjwmw had none)
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToPartOf: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NBLASTexp matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyToPartOf exceeded threshold")
    
        # SimilarMorphologyToPartOfexp - Reverse NBLASTexp
        result, duration, success = self._time_query(
            "SimilarMorphologyToPartOfexp",
            get_similar_morphology_part_of_exp,
            "VFB_001012yj",  # expression pattern with reverse-NBLASTexp matches
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToPartOfexp: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} reverse NBLASTexp matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyToPartOfexp exceeded threshold")
    
        # SimilarMorphologyToNB - NeuronBridge matches
        result, duration, success = self._time_query(
            "SimilarMorphologyToNB",
            get_similar_morphology_nb,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )
        print(f"SimilarMorphologyToNB: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} NeuronBridge matches" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyToNB exceeded threshold")
    
        # SimilarMorphologyToNBexp - NeuronBridge for expression patterns
>       result, duration, success = self._time_query(
            "SimilarMorphologyToNBexp",
            get_similar_morphology_nb_exp,
            self.test_terms['connected_neuron'],
            return_dataframe=False,
            limit=10
        )

src/test/test_query_performance.py:674: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/test/test_query_performance.py:109: in _time_query
    self.assertGreater(self._result_size(result), 0,
E   AssertionError: 0 not greater than 0 : SimilarMorphologyToNBexp returned no rows
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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
_________ QueryPerformanceTest.test_07b_downstream_class_connectivity __________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_07b_downstream_class_connectivity>

    def test_07b_downstream_class_connectivity(self):
        """Test DownstreamClassConnectivity query (multi-step aggregation)"""
        print("\n" + "="*80)
        print("DOWNSTREAM CLASS CONNECTIVITY (multi-step aggregation)")
        print("="*80)
    
        result, duration, success = self._time_query(
            "DownstreamClassConnectivity",
            get_downstream_class_connectivity,
            self.CLASS_CONNECTIVITY_TEST_CLASS,
            return_dataframe=False,
        )
        print(f"DownstreamClassConnectivity: {duration:.4f}s {'✅' if success else '❌'}")
>       self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "DownstreamClassConnectivity exceeded threshold")
E       AssertionError: 113.4595718383789 not less than 31.0 : DownstreamClassConnectivity exceeded threshold

src/test/test_query_performance.py:399: AssertionError
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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
__________ QueryPerformanceTest.test_14_publication_transgene_queries __________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_14_publication_transgene_queries>

    def test_14_publication_transgene_queries(self):
        """Test publication and transgene queries"""
        print("\n" + "="*80)
        print("PUBLICATION/TRANSGENE QUERIES")
        print("="*80)
    
        # Import the new query functions
        from vfbquery.vfb_queries import (
            get_terms_for_pub,
            get_transgene_expression_here
        )
    
        # Test terms
        pub_term = 'FBrf0224194'  # Example publication with results
        anatomy_term = self.test_terms['mushroom_body']  # mushroom body
    
        # TermsForPub - Terms referencing a publication
        # Warm up cache with full results
        try:
            get_terms_for_pub(pub_term, return_dataframe=False, limit=-1)
        except Exception:
            pass  # Ignore warm-up failures
    
        result, duration, success = self._time_query(
            "TermsForPub",
            get_terms_for_pub,
            pub_term,
            return_dataframe=False,
            limit=10
        )
        print(f"TermsForPub: {duration:.4f}s {'✅' if success else '❌'}")
        if success and result:
            count = result.get('count', 0)
            print(f"  └─ Found {count} terms for publication" + (", returned 10" if count > 10 else ""))
        self.assertLess(duration, self.THRESHOLD_MEDIUM, "TermsForPub exceeded threshold")
    
        # TransgeneExpressionHere - Complex transgene expression query
>       result, duration, success = self._time_query(
            "TransgeneExpressionHere",
            get_transgene_expression_here,
            anatomy_term,
            return_dataframe=False,
            limit=10
        )

src/test/test_query_performance.py:835: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/test/test_query_performance.py:109: in _time_query
    self.assertGreater(self._result_size(result), 0,
E   AssertionError: 0 not greater than 0 : TransgeneExpressionHere returned no rows
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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

ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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
__________ QueryPerformanceTest.test_07b_upstream_class_connectivity ___________
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_query_performance.QueryPerformanceTest testMethod=test_07b_upstream_class_connectivity>

    def test_07b_upstream_class_connectivity(self):
        """Test UpstreamClassConnectivity query (multi-step aggregation)"""
        print("\n" + "="*80)
        print("UPSTREAM CLASS CONNECTIVITY (multi-step aggregation)")
        print("="*80)
    
        result, duration, success = self._time_query(
            "UpstreamClassConnectivity",
            get_upstream_class_connectivity,
            self.CLASS_CONNECTIVITY_TEST_CLASS,
            return_dataframe=False,
        )
        print(f"UpstreamClassConnectivity: {duration:.4f}s {'✅' if success else '❌'}")
>       self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "UpstreamClassConnectivity exceeded threshold")
E       AssertionError: 119.03038358688354 not less than 31.0 : UpstreamClassConnectivity exceeded threshold

src/test/test_query_performance.py:414: AssertionError
------------------------------ Captured log call -------------------------------
ERROR    vfbquery.solr_result_cache:solr_result_cache.py:721 Failed to cache result: HTTP 401 - <html>
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
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_09_neuron_input_queries - AssertionError: 25.8081157207489 not less than 15.0 : NeuronInputsTo exceeded threshold
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_12_nblast_queries - AssertionError: 0 not greater than 0 : SimilarMorphologyToNBexp returned no rows
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_downstream_class_connectivity - AssertionError: 113.4595718383789 not less than 31.0 : DownstreamClassConnectivity exceeded threshold
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_14_publication_transgene_queries - AssertionError: 0 not greater than 0 : TransgeneExpressionHere returned no rows
FAILED src/test/test_query_performance.py::QueryPerformanceTest::test_07b_upstream_class_connectivity - AssertionError: 119.03038358688354 not less than 31.0 : UpstreamClassConnectivity exceeded threshold
============= 5 failed, 11 passed, 2 skipped in 329.32s (0:05:29) ==============
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.352s

OK
VFBquery functions patched with caching support
VFBquery: SOLR caching enabled by default (3-month TTL)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.7559 seconds
VFB_00101567 query took: 0.5954 seconds
Total time for both queries: 1.3512 seconds
Performance Level: 🟢 Excellent (< 1.5 seconds)
==================================================
Performance test completed successfully!
=== CONNECTIVITY RETRY ATTEMPT ===
============================= test session starts ==============================
platform linux -- Python 3.10.22, pytest-9.1.1, pluggy-1.6.0 -- /opt/hostedtoolcache/Python/3.10.22/x64/bin/python
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

src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
[gw3] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_returns_results 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_upstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_returns_results 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_row_has_expected_keys 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_direction_downstream 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_headers_present 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_returns_dataframe 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_count_columns_populated 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDict::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_headers_present 
src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw3] FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_limit_respected 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
[gw0] PASSED src/test/test_neuron_neuron_connectivity.py::TestNeuronNeuronConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
[gw1] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivitySchema::test_schema_generation 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivitySchema::test_schema_generation 
src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw1] FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_headers_present 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_limit_respected 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_returns_dataframe 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw0] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_total_n_is_per_partner 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw2] PASSED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
[gw3] PASSED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityAttachment::test_query_attached_to_term_info 
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
[gw3] FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_total_n_constant_within_each_query_class 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
[gw2] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_includes_subclass_breakdown 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_row_has_expected_keys 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_headers_present 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_empty_class_returns_zero 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw1] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_returns_dataframe 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_datasets_have_label_and_symbol 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_hemibrain_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_every_dataset_has_symbol 
src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_known_connection_both_types 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_dataframe_has_expected_columns 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_limit_respected 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
[gw0] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDataFrame::test_empty_class_returns_empty_dataframe 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root 
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
[gw3] PASSED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivitySchema::test_schema_generation 
src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestListConnectomeDatasets::test_returns_datasets 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
[gw1] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
[gw1] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
[gw0] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children 
src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbs::test_exclude_all_returns_no_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityWeightFiltering::test_higher_weight_fewer_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_parent_class_with_no_direct_instances_returns_results 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_resolved_reports_how_a_label_was_read 
src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_ambiguous_label_lists_candidates 
src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_matches_passing_it_explicitly 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_tm9_is_predominantly_cholinergic 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_aggregate_row_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
[gw3] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
[gw1] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer 
src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_no_types_raises_error 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityKnown::test_both_types_subset_of_either_alone 
src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestQueryConnectivityEdgeCases::test_nonexistent_type_returns_warning 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_per_instance_shape 
src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
[gw0] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_split_by_dataset_adds_dataset_column 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestPredictedNeurotransmitters::test_min_confidence_filters 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_tm9_known_cholinergic 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
[gw1] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_includes_subclasses 
[gw2] FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class 
src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 
[gw3] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_nonexistent_type_returns_warning 
[gw2] PASSED src/test/test_vfb_connectivity.py::TestKnownNeurotransmitters::test_row_shape 

=================================== FAILURES ===================================
__ TestNeuronRegionConnectivityDataFrame.test_dataframe_has_expected_columns ___
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_neuron_region_connectivity.TestNeuronRegionConnectivityDataFrame object at 0x7fc584d1a080>

    @pytest.mark.integration
    def test_dataframe_has_expected_columns(self):
        df = get_neuron_region_connectivity(
            TEST_NEURON, return_dataframe=True, limit=1
        )
        expected_cols = {"id", "region", "presynaptic_terminals", "downstream_synapses", "postsynaptic_terminals", "tags"}
>       assert expected_cols.issubset(set(df.columns))
E       AssertionError: assert False
E        +  where False = <built-in method issubset of set object at 0x7fc5851e6260>(set())
E        +    where <built-in method issubset of set object at 0x7fc5851e6260> = {'downstream_synapses', 'id', 'postsynaptic_terminals', 'presynaptic_terminals', 'region', 'tags'}.issubset
E        +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
E        +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns

src/test/test_neuron_region_connectivity.py:96: AssertionError
___________ TestDownstreamClassConnectivityDict.test_returns_results ___________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_downstream_class_connectivity.TestDownstreamClassConnectivityDict object at 0x7f05ab936740>

    @pytest.mark.integration
    def test_returns_results(self):
>       result = get_downstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_downstream_class_connectivity.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1169: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1162: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5125: in get_downstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'downstream', status=status)
src/test/test_downstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'downstream'
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
E           vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00001482

src/vfbquery/vfb_queries.py:4856: ConnectivityBackendError
____________ TestUpstreamClassConnectivityDict.test_returns_results ____________
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_upstream_class_connectivity.TestUpstreamClassConnectivityDict object at 0x7fc584d4ce80>

    @pytest.mark.integration
    def test_returns_results(self):
>       result = get_upstream_class_connectivity(
            TEST_CLASS, return_dataframe=False, force_refresh=True
        )

src/test/test_upstream_class_connectivity.py:66: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
src/vfbquery/solr_result_cache.py:1169: in wrapper
    return _call(*args, **kwargs)
src/vfbquery/solr_result_cache.py:1162: in _call
    return func(*call_args, **call_kwargs)
src/vfbquery/vfb_queries.py:5199: in get_upstream_class_connectivity
    rows = _aggregate_class_connectivity(short_form, 'upstream', status=status)
src/test/test_upstream_class_connectivity.py:48: in once
    rows = real(short_form, direction, neuron_root=neuron_root,
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

short_form = 'FBbt_00001482', direction = 'upstream'
neuron_root = 'FBbt_00005106', status = {'missing': 0, 'total': 178}

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
E           vfbquery.vfb_queries.ConnectivityBackendError: Partner class membership query failed for FBbt_00001482 (3466 partner classes)

src/vfbquery/vfb_queries.py:4945: ConnectivityBackendError
______ TestQueryConnectivityRollup.test_top_level_query_term_row_present _______
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityRollup object at 0x7f05abde6140>
rollup_result = {'connections': [], 'warnings': [], 'count': 0, 'resolved': {'upstream': {'query': 'FBbt_00047030', 'id': 'FBbt_000470...3655', 'id': 'FBbt_00003655', 'label': 'adult ellipsoid body extrinsic ring neuron ExR1', 'classes_searched': 3, ...}}}

    @pytest.mark.integration
    def test_top_level_query_term_row_present(self, rollup_result):
        # The row the non-rolled-up grouping never emitted: both sides at the
        # named query term, aggregating every level beneath them.
        conns = rollup_result["connections"]
>       assert conns
E       assert []

src/test/test_vfb_connectivity.py:176: AssertionError
__________ TestQueryConnectivityRollup.test_finer_levels_also_present __________
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityRollup object at 0x7f05abde5e10>
rollup_result = {'connections': [], 'warnings': [], 'count': 0, 'resolved': {'upstream': {'query': 'FBbt_00047030', 'id': 'FBbt_000470...3655', 'id': 'FBbt_00003655', 'label': 'adult ellipsoid body extrinsic ring neuron ExR1', 'classes_searched': 3, ...}}}

    @pytest.mark.integration
    def test_finer_levels_also_present(self, rollup_result):
        # Rollup adds levels, it does not replace them: subclass-level rows still
        # appear alongside the parent-to-parent row.
        conns = rollup_result["connections"]
>       assert any(
            c["upstream_class_id"] != self.ROLLUP_UP
            or c["downstream_class_id"] != self.ROLLUP_DOWN
            for c in conns
        )
E       assert False
E        +  where False = any(<generator object TestQueryConnectivityRollup.test_finer_levels_also_present.<locals>.<genexpr> at 0x7f0595ac04a0>)

src/test/test_vfb_connectivity.py:188: AssertionError
______ TestQueryConnectivityRollup.test_parent_row_dominates_its_children ______
[gw0] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityRollup object at 0x7f5c4c5d8100>
rollup_result = {'connections': [], 'warnings': ["Neuron class not found for ID 'FBbt_00047030'. Check the ID is a valid neuron class (not an anatomy region)."], 'count': 0, 'resolved': {}}

    @pytest.mark.integration
    def test_parent_row_dominates_its_children(self, rollup_result):
        # The parent-to-parent row is a set-union over every child pair, so its
        # weight is at least that of any single child pair sharing an endpoint.
        conns = rollup_result["connections"]
>       top = next(
            c for c in conns
            if c["upstream_class_id"] == self.ROLLUP_UP
            and c["downstream_class_id"] == self.ROLLUP_DOWN
        )
E       StopIteration

src/test/test_vfb_connectivity.py:199: StopIteration
_ TestQueryConnectivityExcludeDbsDefault.test_default_excludes_are_a_strict_subset_of_everything _
[gw3] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityExcludeDbsDefault object at 0x7fc5851cf340>
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
        # Subset, not strict subset. Excluding a dataset can only ever remove
        # rows, and that is the contract worth asserting. Demanding a strict
        # decrease additionally requires hemibrain or FAFB to hold rows for
        # *this* term pair, which is backend content -- it was true when this
        # was written and is not true now (17 either way).
>       assert 0 < expansion_result["count"] <= everything["count"]
E       assert 17 <= 0

src/test/test_vfb_connectivity.py:315: AssertionError
_ TestQueryConnectivitySubclassExpansion.test_anchor_side_does_not_change_the_answer _
[gw1] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivitySubclassExpansion object at 0x7f05abde5240>

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
        _, up_ids, _ = _subclass_closure(nc, up_id)
        _, down_ids, _ = _subclass_closure(nc, down_id)
        counts = []
        for anchor in ("upstream", "downstream"):
            cypher = _build_connectivity_cypher(
                up_ids, down_ids, 5, False, DEFAULT_EXCLUDE_DBS, anchor=anchor,
            )
            counts.append(len(dict_cursor(nc.commit_list([cypher]))))
>       assert counts[0] == counts[1] > 0
E       assert 17 == 0

src/test/test_vfb_connectivity.py:284: AssertionError
____________ TestQueryConnectivityGroupByClass.test_group_by_class _____________
[gw2] linux -- Python 3.10.22 /opt/hostedtoolcache/Python/3.10.22/x64/bin/python

self = <src.test.test_vfb_connectivity.TestQueryConnectivityGroupByClass object at 0x7fb4877e22f0>

    @pytest.mark.integration
    def test_group_by_class(self):
        result = query_connectivity(
            upstream_type=KNOWN_UPSTREAM,
            downstream_type=KNOWN_DOWNSTREAM,
            group_by_class=True,
        )
>       assert result["count"] > 0
E       assert 0 > 0

src/test/test_vfb_connectivity.py:141: AssertionError
=============================== warnings summary ===============================
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_parent_class_appears_with_sensible_counts
src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityHierarchyRollup::test_no_rows_above_neuron_root
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present
src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children
  /opt/hostedtoolcache/Python/3.10.22/x64/lib/python3.10/site-packages/_pytest/fixtures.py:1313: PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated.
  Instance attributes set in this fixture will NOT be visible to test methods,
  as each test gets a new instance while the fixture runs only once per class.
  Use @classmethod decorator and set attributes on cls instead.
  See https://docs.pytest.org/en/stable/deprecations.html#class-scoped-fixture-as-instance-method
    fixturefunc = resolve_fixture_function(fixturedef, request)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
FAILED src/test/test_neuron_region_connectivity.py::TestNeuronRegionConnectivityDataFrame::test_dataframe_has_expected_columns - AssertionError: assert False
 +  where False = <built-in method issubset of set object at 0x7fc5851e6260>(set())
 +    where <built-in method issubset of set object at 0x7fc5851e6260> = {'downstream_synapses', 'id', 'postsynaptic_terminals', 'presynaptic_terminals', 'region', 'tags'}.issubset
 +    and   set() = set(RangeIndex(start=0, stop=0, step=1))
 +      where RangeIndex(start=0, stop=0, step=1) = Empty DataFrame\nColumns: []\nIndex: [].columns
FAILED src/test/test_downstream_class_connectivity.py::TestDownstreamClassConnectivityDict::test_returns_results - vfbquery.vfb_queries.ConnectivityBackendError: Queried-side membership query returned no result for FBbt_00001482
FAILED src/test/test_upstream_class_connectivity.py::TestUpstreamClassConnectivityDict::test_returns_results - vfbquery.vfb_queries.ConnectivityBackendError: Partner class membership query failed for FBbt_00001482 (3466 partner classes)
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_top_level_query_term_row_present - assert []
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_finer_levels_also_present - assert False
 +  where False = any(<generator object TestQueryConnectivityRollup.test_finer_levels_also_present.<locals>.<genexpr> at 0x7f0595ac04a0>)
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityRollup::test_parent_row_dominates_its_children - StopIteration
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityExcludeDbsDefault::test_default_excludes_are_a_strict_subset_of_everything - assert 17 <= 0
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivitySubclassExpansion::test_anchor_side_does_not_change_the_answer - assert 17 == 0
FAILED src/test/test_vfb_connectivity.py::TestQueryConnectivityGroupByClass::test_group_by_class - assert 0 > 0
============= 9 failed, 69 passed, 6 warnings in 881.22s (0:14:41) =============
```

## Summary

❌ **Test Status**: Performance tests ran but reported failures

### Test Statistics

- **Total Tests**: 107
- **Passed**: 81 ✅
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
*Last updated: 2026-10-13 09:35:02 UTC*
