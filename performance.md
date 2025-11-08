# VFBquery Performance Test Results

**Test Date:** 2025-11-08 09:17:58 UTC
**Git Commit:** da1e4a1d46b70842d564561b3ab41adbf3659a2b
**Branch:** dev
**Workflow Run:** [19190585220](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19190585220)

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
Test term info query performance ... ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for neurons_part_here(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002130%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for neurons_synaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for neurons_postsynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for parts_of(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3CFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for subclasses_of(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for tracts_nerves_innervating_here(FBbt_00003748), clearing cache entry
ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for lineage_clones_in(FBbt_00003748), clearing cache entry
ERROR: Owlery instances query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00003748>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2510, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_instances(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 230, in get_instances
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry
FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007401%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/FBbt_00007401>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for neurons_part_here(FBbt_00007401), clearing cache entry
FAIL
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ERROR: Owlery subclasses query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Full URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002130%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007401%3E&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
       Query string: <http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <http://purl.obolibrary.org/obo/FBbt_00007401>
Traceback (most recent call last):
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
socket.timeout: timed out

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 843, in urlopen
    retries = retries.increment(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/retry.py", line 474, in increment
    raise reraise(type(error), error, _stacktrace)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/util/util.py", line 39, in reraise
    raise value
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 789, in urlopen
    response = self._make_request(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 538, in _make_request
    self._raise_timeout(err=e, url=url, timeout_value=read_timeout)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/urllib3/connectionpool.py", line 369, in _raise_timeout
    raise ReadTimeoutError(
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2516, in _owlery_query_to_results
    result_ids = vc.vfb.oc.get_subclasses(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 118, in get_subclasses
    response = requests.get(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/requests/adapters.py", line 713, in send
    raise ReadTimeout(e, request=request)
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
Query returned error result for neurons_synaptic(FBbt_00007401), clearing cache entry
FAIL
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... FAIL
test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries ... FAIL
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 98, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
AssertionError: 1956.8312647342682 not less than 3.0 : term_info query exceeded threshold

======================================================================
FAIL: test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 123, in test_02_neuron_part_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronsPartHere exceeded threshold")
AssertionError: 240.95608925819397 not less than 10.0 : NeuronsPartHere exceeded threshold

======================================================================
FAIL: test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 141, in test_03_synaptic_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronsSynaptic exceeded threshold")
AssertionError: 241.05468583106995 not less than 10.0 : NeuronsSynaptic exceeded threshold

======================================================================
FAIL: test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 190, in test_04_anatomy_hierarchy_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "ComponentsOf exceeded threshold")
AssertionError: 193.7987539768219 not less than 10.0 : ComponentsOf exceeded threshold

======================================================================
FAIL: test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 227, in test_05_new_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronClassesFasciculatingHere exceeded threshold")
AssertionError: 57.687758922576904 not less than 10.0 : NeuronClassesFasciculatingHere exceeded threshold

----------------------------------------------------------------------
Ran 6 tests in 2691.129s

FAILED (failures=5)
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

================================================================================
TERM INFO QUERIES
================================================================================
DEBUG: Cache lookup for FBbt_00003748: MISS
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
ERROR: Owlery instances request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E+and+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E+some+%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E&direct=false&includeDeprecated=false&prefixes=%7B%22FBbt%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_%22%2C+%22RO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_%22%2C+%22BFO%22%3A+%22http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_%22%2C+%22VFB%22%3A+%22http%3A%2F%2Fvirtualflybrain.org%2Freports%2FVFB_%22%7D
get_term_info (mushroom body): 1956.8313s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
NeuronsPartHere: 240.9561s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=240)
NeuronsSynaptic: 241.0547s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ComponentsOf: 193.7988s ✅

================================================================================
NEW QUERIES (2025)
================================================================================
NeuronClassesFasciculatingHere: 57.6878s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.7996s ✅

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.330s

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
FBbt_00003748 query took: 0.6662 seconds
VFB_00101567 query took: 0.6635 seconds
Total time for both queries: 1.3298 seconds
Performance Level: 🟢 Excellent (< 1.5 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 7
- **Passed**: -18 ✅
- **Failed**: 5 ❌
- **Errors**: 20 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|
| NeuronsPartHere | 240.9561s | ✅ Pass |
| NeuronsSynaptic | 241.0547s | ✅ Pass |
| ComponentsOf | 193.7988s | ✅ Pass |
| NeuronClassesFasciculatingHere | 57.6878s | ✅ Pass |
| ListAllAvailableImages | 0.7996s | ✅ Pass |

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
*Last updated: 2025-11-08 09:17:58 UTC*
