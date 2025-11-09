# VFBquery Performance Test Results

**Test Date:** 2025-11-09 19:40:32 UTC
**Git Commit:** 6200965dc34fd48a78dd4ee0dcb1f99bbc74c96a
**Branch:** dev
**Workflow Run:** [19213004173](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19213004173)

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
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
Query returned error result for tracts_nerves_innervating_here(FBbt_00003748), clearing cache entry

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
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2907, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_instances(
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
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry

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
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
AssertionError: 1148.44305062294 not less than 31.0 : term_info query exceeded threshold

======================================================================
FAIL: test_08_similarity_queries (src.test.test_query_performance.QueryPerformanceTest)
Test NBLAST similarity queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 373, in test_08_similarity_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "SimilarMorphologyTo exceeded threshold")
AssertionError: 13.25633430480957 not less than 10.0 : SimilarMorphologyTo exceeded threshold

----------------------------------------------------------------------
Ran 15 tests in 1198.192s

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
get_term_info (mushroom body): 1148.4431s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.5407s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 1.2555s ✅
NeuronsPresynapticHere: 0.9175s ✅
NeuronsPostsynapticHere: 1.4218s ✅
NeuronNeuronConnectivity: 0.9073s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 0.9146s ✅
PartsOf: 0.9469s ✅
SubclassesOf: 1.2028s ✅

================================================================================
TRACT/NERVE AND LINEAGE QUERIES
================================================================================
NeuronClassesFasciculatingHere: 0.9304s ✅
TractsNervesInnervatingHere: 0.9401s ✅
LineageClonesIn: 0.9374s ✅

================================================================================
IMAGE AND DEVELOPMENTAL QUERIES
================================================================================
ImagesNeurons: 1.4715s ✅
ImagesThatDevelopFrom: 0.9265s ✅
epFrag: 0.9452s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.9200s ✅

================================================================================
CONNECTIVITY QUERIES
================================================================================
NeuronNeuronConnectivityQuery: 1.0735s ✅
NeuronRegionConnectivityQuery: 0.9426s ✅

================================================================================
SIMILARITY QUERIES (Neo4j NBLAST)
================================================================================
SimilarMorphologyTo: 13.2563s ✅

================================================================================
NEURON INPUT QUERIES (Neo4j)
================================================================================
NeuronInputsTo: 3.7424s ✅

================================================================================
EXPRESSION PATTERN QUERIES (Neo4j)
================================================================================
ExpressionOverlapsHere: 1.1592s ✅
  └─ Found 3922 total expression patterns, returned 10

================================================================================
TRANSCRIPTOMICS QUERIES (Neo4j scRNAseq)
================================================================================
anatScRNAseqQuery: 0.8951s ✅
  └─ Found 0 total clusters
clusterExpression: 0.7270s ✅
  └─ Found 0 genes expressed
expressionCluster: 0.9236s ✅
  └─ Found 0 clusters expressing gene
scRNAdatasetData: 1.0077s ✅
  └─ Found 0 clusters in dataset

================================================================================
NBLAST SIMILARITY QUERIES
================================================================================
SimilarMorphologyTo: 1.0668s ✅
  └─ Found 227 NBLAST matches, returned 10
SimilarMorphologyToPartOf: 0.8720s ✅
  └─ Found 0 NBLASTexp matches
SimilarMorphologyToPartOfexp: 0.6986s ✅
  └─ Found 0 reverse NBLASTexp matches
SimilarMorphologyToNB: 0.7245s ✅
  └─ Found 15 NeuronBridge matches, returned 10
SimilarMorphologyToNBexp: 0.7209s ✅
  └─ Found 15 NeuronBridge expression matches, returned 10
✅ All NBLAST similarity queries completed

================================================================================
DATASET/TEMPLATE QUERIES
================================================================================
PaintedDomains: 0.7559s ✅
  └─ Found 0 painted domains
DatasetImages: 0.7375s ✅
  └─ Found 0 images in dataset
AllAlignedImages: 0.7102s ✅
  └─ Found 0 aligned images
AlignedDatasets: 1.0367s ✅
  └─ Found 0 aligned datasets
AllDatasets: 1.0002s ✅
  └─ Found 115 total datasets, returned 20
✅ All dataset/template queries completed

================================================================================
PUBLICATION/TRANSGENE QUERIES
================================================================================
TermsForPub: 0.6812s ✅
  └─ Found 0 terms for publication
TransgeneExpressionHere: 0.8340s ✅
  └─ Found 2339 transgene expressions, returned 10
✅ All publication/transgene queries completed

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... Cached result incomplete for FBbt_00003748, re-executing function
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/FBbt_00003748>
ERROR: Owlery instances query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=true&includeDeprecated=false
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 942, in urlopen
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
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
Query returned error result for neurons_postsynaptic(FBbt_00003748), clearing cache entry
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 942, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 841, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/util/retry.py", line 519, in increment
    raise MaxRetryError(_pool, url, reason) from reason  # type: ignore[arg-type]
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2907, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_instances(
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
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true
       Query string: <http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
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
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/requests/adapters.py", line 644, in send
    resp = conn.urlopen(
requests.exceptions.ConnectionError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
  File "/opt/hostedtoolcache/Python/3.10.19/x64/lib/python3.10/site-packages/urllib3/connectionpool.py", line 871, in urlopen
    return self.urlopen(
Query returned error result for lineage_clones_in(FBbt_00003748), clearing cache entry
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
  File "/home/runner/work/VFBquery/VFBquery/src/vfbquery/vfb_queries.py", line 2913, in _owlery_query_to_results
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
FAIL

======================================================================
FAIL: test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries.
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/term_info_queries_test.py", line 575, in test_term_info_performance
    self.assertLess(duration_1, max_single_query_time,
AssertionError: 1146.4664962291718 not less than 3.0 : FBbt_00003748 query took 1146.4665s, exceeding 3.0s threshold

----------------------------------------------------------------------
Ran 1 test in 1147.879s

FAILED (failures=1)
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false
✅ Neo4j connection established
✅ Neo4j connection established
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
ERROR: Owlery instances request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Max retries exceeded with url: /kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true (Caused by ProtocolError('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer')))

==================================================
Performance Test Results:
==================================================
FBbt_00003748 query took: 1146.4665 seconds
VFB_00101567 query took: 1.4110 seconds
Total time for both queries: 1147.8775 seconds
Performance Level: 🔴 Slow (> 6 seconds)
==================================================
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 16
- **Passed**: -3 ✅
- **Failed**: 3 ❌
- **Errors**: 16 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|
| NeuronsPartHere | 1.5407s | ✅ Pass |
| NeuronsSynaptic | 1.2555s | ✅ Pass |
| NeuronsPresynapticHere | 0.9175s | ✅ Pass |
| NeuronsPostsynapticHere | 1.4218s | ✅ Pass |
| ComponentsOf | 0.9146s | ✅ Pass |
| PartsOf | 0.9469s | ✅ Pass |
| SubclassesOf | 1.2028s | ✅ Pass |
| NeuronClassesFasciculatingHere | 0.9304s | ✅ Pass |
| TractsNervesInnervatingHere | 0.9401s | ✅ Pass |
| LineageClonesIn | 0.9374s | ✅ Pass |
| ListAllAvailableImages | 0.9200s | ✅ Pass |

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
*Last updated: 2025-11-09 19:40:32 UTC*
