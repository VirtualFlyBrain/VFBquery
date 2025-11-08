# VFBquery Performance Test Results

**Test Date:** 2025-11-08 10:07:36 UTC
**Git Commit:** 4a51cba50a2406a737223086a49a4e4318c38de4
**Branch:** dev
**Workflow Run:** [19191339389](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19191339389)

## Test Overview

This performance test measures the execution time of all implemented VFB queries including:

### Core Queries
- **Term Info Queries**: Basic term information retrieval
- **Neuron Part Queries**: Neurons with parts overlapping regions
- **Synaptic Terminal Queries**: Pre/post synaptic terminals
- **Anatomical Hierarchy**: Components, parts, subclasses
- **Instance Queries**: Available images and instances

### New Queries (2025)
- **NeuronClassesFasciculatingHere**: Neurons fasciculating with tracts
- **TractsNervesInnervatingHere**: Tracts/nerves innervating neuropils
- **LineageClonesIn**: Lineage clones in neuropils

## Performance Thresholds

- **Fast queries**: < 1 second (SOLR lookups)
- **Medium queries**: < 3 seconds (Owlery + SOLR)
- **Slow queries**: < 10 seconds (Neo4j + complex processing)

## Test Results

```
test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance ... ERROR: Owlery subclasses query failed: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connection.py", line 507, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 1348, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 316, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 277, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/socket.py", line 669, in readinto
    return self._sock.recv_into(b)
ConnectionResetError: [Errno 104] Connection reset by peer

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 38, in reraise
    raise value.with_traceback(tb)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connection.py", line 507, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 1348, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 316, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 277, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/socket.py", line 669, in readinto
    return self._sock.recv_into(b)
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 119, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 682, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
Query returned error result for neurons_part_here(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002113%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connection.py", line 507, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 1348, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 316, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 277, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/socket.py", line 669, in readinto
    return self._sock.recv_into(b)
ConnectionResetError: [Errno 104] Connection reset by peer

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 38, in reraise
    raise value.with_traceback(tb)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 536, in _make_request
    response = conn.getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connection.py", line 507, in getresponse
    httplib_response = super().getresponse()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 1348, in getresponse
    response.begin()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 316, in begin
    version, status, reason = self._read_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/http/client.py", line 277, in _read_status
    line = str(self.fp.readline(_MAXLINE + 1), "iso-8859-1")
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/socket.py", line 669, in readinto
    return self._sock.recv_into(b)
urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 119, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 682, in send
    raise ConnectionError(err, request=request)
requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
Query returned error result for neurons_presynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%7D
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 128, in get_subclasses
    response.raise_for_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/models.py", line 1026, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%7D
Query returned error result for neurons_postsynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery instances query failed: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2510, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_instances(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 237, in get_instances
    response.raise_for_status()
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/models.py", line 1026, in raise_for_status
    raise HTTPError(http_error_msg, response=self)
requests.exceptions.HTTPError: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry
FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ok
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ok
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... ok
test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries ... FAIL
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 109, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
AssertionError: 1144.6471083164215 not less than 3.0 : term_info query exceeded threshold

======================================================================
FAIL: test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 271, in test_05_new_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "ImagesNeurons exceeded threshold")
AssertionError: 258.8372805118561 not less than 10.0 : ImagesNeurons exceeded threshold

----------------------------------------------------------------------
Ran 6 tests in 1425.555s

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
ERROR: Owlery request failed: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
ERROR: Owlery request failed: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
ERROR: Owlery request failed: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&includeEquivalent=true&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%7D
ERROR: Owlery instances request failed: 502 Server Error: Bad Gateway for url: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
get_term_info (mushroom body): 1144.6471s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
NeuronsPartHere: 1.6706s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
NeuronsSynaptic: 2.4014s ✅
NeuronsPresynapticHere: 7.1245s ✅
NeuronsPostsynapticHere: 2.4474s ✅
✅ Neo4j connection established
NeuronNeuronConnectivity: 0.7642s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 1.6945s ✅
PartsOf: 0.3493s ✅
SubclassesOf: 1.5318s ✅

================================================================================
NEW QUERIES (2025)
================================================================================
NeuronClassesFasciculatingHere: 0.6388s ✅
TractsNervesInnervatingHere: 1.5150s ✅
LineageClonesIn: 1.0390s ✅
ImagesNeurons: 258.8373s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.8926s ✅

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.690s

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
FBbt_00003748 query took: 0.8367 seconds
VFB_00101567 query took: 0.8531 seconds
Total time for both queries: 1.6898 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 7
- **Passed**: -3 ✅
- **Failed**: 2 ❌
- **Errors**: 8 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|
| NeuronsPartHere | 1.6706s | ✅ Pass |
| NeuronsSynaptic | 2.4014s | ✅ Pass |
| NeuronsPresynapticHere | 7.1245s | ✅ Pass |
| NeuronsPostsynapticHere | 2.4474s | ✅ Pass |
| ComponentsOf | 1.6945s | ✅ Pass |
| PartsOf | 0.3493s | ✅ Pass |
| SubclassesOf | 1.5318s | ✅ Pass |
| NeuronClassesFasciculatingHere | 0.6388s | ✅ Pass |
| TractsNervesInnervatingHere | 1.5150s | ✅ Pass |
| LineageClonesIn | 1.0390s | ✅ Pass |
| ListAllAvailableImages | 0.8926s | ✅ Pass |

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
*Last updated: 2025-11-08 10:07:36 UTC*
