# VFBquery Performance Test Results

**Test Date:** 2025-11-09 12:21:01 UTC
**Git Commit:** b2fa7f92464e5d7053edeb73494af1eb0601d0bb
**Branch:** dev
**Workflow Run:** [19208120587](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19208120587)

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
Test term info query performance ... ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <http://purl.obolibrary.org/obo/FBbt_00003748>
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2898, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/owlery_client.py", line 129, in get_subclasses
    response = session.get(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 602, in get
    return self.request("GET", url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 677, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
Query returned error result for tracts_nerves_innervating_here(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/FBbt_00003748>
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2898, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/owlery_client.py", line 129, in get_subclasses
    response = session.get(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 602, in get
    return self.request("GET", url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 677, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
Query returned error result for neurons_postsynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery instances query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=true&includeDeprecated=false
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true
       Query string: <http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2892, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_instances(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/owlery_client.py", line 249, in get_instances
    response = session.get(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 602, in get
    return self.request("GET", url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 677, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2898, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/owlery_client.py", line 129, in get_subclasses
    response = session.get(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 602, in get
    return self.request("GET", url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 677, in send
    raise ConnectionError(e, request=request)
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
Query returned error result for lineage_clones_in(FBbt_00003748), clearing cache entry
FAIL
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
test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries ... FAIL
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

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 117, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_VERY_SLOW, "term_info query exceeded threshold")
AssertionError: 1098.845538854599 not less than 31.0 : term_info query exceeded threshold

======================================================================
FAIL: test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 373, in test_08_similarity_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
AssertionError: 13.769211292266846 not less than 10.0 : SimilarMorphologyTo exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 1147.252s

FAILED (failures=2)
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB

🔥 Caching enabled for performance tests

================================================================================
TERM INFO QUERIES
================================================================================
DEBUG: Cache lookup for FBbt_00003748: MISS
✅ Neo4j connection established
✅ Neo4j connection established
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
ERROR: Owlery instances request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
get_term_info (mushroom body): 1098.8455s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.2711s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.4015s ✅
NeuronsPresynapticHere: 1.2048s ✅
NeuronsPostsynapticHere: 1.2492s ✅
NeuronNeuronConnectivity: 0.9501s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 0.9065s ✅
PartsOf: 0.9149s ✅
SubclassesOf: 0.9148s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 0.9598s ✅
TractsNervesInnervatingHere: 0.9351s ✅
LineageClonesIn: 0.9286s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 1.4203s ✅
ImagesThatDevelopFrom: 0.9244s ✅
epFrag: 1.0553s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.9229s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 0.9628s ✅
NeuronRegionConnectivityQuery: 0.9253s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 13.7692s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 2.6567s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 0.9715s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.9016s ✅
  └─ Found 0 total clusters
clusterExpression: 0.8645s ✅
  └─ Found 0 genes expressed
expressionCluster: 1.0007s ✅
  └─ Found 0 clusters expressing gene
scRNAdatasetData: 0.8872s ✅
  └─ Found 0 clusters in dataset

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.0148s ✅
  └─ Found 227 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.7035s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.6997s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.7460s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.7259s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.7137s ✅
  └─ Found 0 painted domains
DatasetImages: 0.7294s ✅
  └─ Found 0 images in dataset
AllAlignedImages: 0.7232s ✅
  └─ Found 0 aligned images
AlignedDatasets: 0.9277s ✅
  └─ Found 0 aligned datasets
AllDatasets: 0.9640s ✅
  └─ Found 115 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.7016s ✅
  └─ Found 0 terms for publication
TransgeneExpressionHere: 0.8538s ✅
  └─ Found 2339 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 2.008s

OK
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 0.9445 seconds
VFB_00101567 query took: 1.0633 seconds
Total time for both queries: 2.0079 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 16
- **Passed**: 6 ✅
- **Failed**: 2 ❌
- **Errors**: 8 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|
| NeuronsPartHere | 1.2711s | ✅ Pass |
| NeuronsSynaptic | 1.4015s | ✅ Pass |
| NeuronsPresynapticHere | 1.2048s | ✅ Pass |
| NeuronsPostsynapticHere | 1.2492s | ✅ Pass |
| ComponentsOf | 0.9065s | ✅ Pass |
| PartsOf | 0.9149s | ✅ Pass |
| SubclassesOf | 0.9148s | ✅ Pass |
| NeuronClassesFasciculatingHere | 0.9598s | ✅ Pass |
| TractsNervesInnervatingHere | 0.9351s | ✅ Pass |
| LineageClonesIn | 0.9286s | ✅ Pass |
| ListAllAvailableImages | 0.9229s | ✅ Pass |

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
*Last updated: 2025-11-09 12:21:01 UTC*
