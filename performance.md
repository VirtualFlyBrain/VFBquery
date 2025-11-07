# VFBquery Performance Test Results

**Test Date:** 2025-11-07 14:03:11 UTC
**Git Commit:** b6863bce7f450b11d9e9bf5db7712b9b721d6763
**Branch:** dev
**Workflow Run:** [19170039180](https://github.com/VirtualFlyBrain/VFBquery/actions/runs/19170039180)

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
Test term info query performance ... ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_part_here(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002130%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_synaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002113%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_presynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002110%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_postsynaptic(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for parts_of(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3CFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for subclasses_of(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005099%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002134%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for tracts_nerves_innervating_here(FBbt_00003748), clearing cache entry
ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007683%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for lineage_clones_in(FBbt_00003748), clearing cache entry
ERROR: Owlery instances query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/instances?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2577, in _owlery_instances_query_to_results
    instance_ids = vc.vfb.oc.get_instances(
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/owlery_client.py", line 223, in get_instances
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for images_neurons(FBbt_00003748), clearing cache entry
FAIL
test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries ... ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002131%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007401%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_part_here(FBbt_00007401), clearing cache entry
FAIL
test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries ... ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002130%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00007401%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neurons_synaptic(FBbt_00007401), clearing cache entry
FAIL
test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries ... ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003748%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for components_of(FBbt_00003748), clearing cache entry
FAIL
test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries ... ERROR: Owlery query failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
       Test URL: http://owl.virtualflybrain.org/kbs/vfb/subclasses?object=%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00005106%3E%20and%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002101%3E%20some%20%3Chttp%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FFBbt_00003987%3E
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
urllib3.exceptions.ReadTimeoutError: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.8.18/x64/lib/python3.8/site-packages/vfbquery/vfb_queries.py", line 2395, in _owlery_query_to_results
    class_ids = vc.vfb.oc.get_subclasses(
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
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
Query returned error result for neuron_classes_fasciculating_here(FBbt_00003987), clearing cache entry
FAIL
test_06_instance_queries (src.test.test_query_performance.QueryPerformanceTest)
Test instance retrieval queries ... ok

======================================================================
FAIL: test_01_term_info_queries (src.test.test_query_performance.QueryPerformanceTest)
Test term info query performance
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 96, in test_01_term_info_queries
    self.assertLess(duration, self.THRESHOLD_MEDIUM, "term_info query exceeded threshold")
AssertionError: 1089.6295518875122 not less than 3.0 : term_info query exceeded threshold

======================================================================
FAIL: test_02_neuron_part_queries (src.test.test_query_performance.QueryPerformanceTest)
Test neuron part overlap queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 121, in test_02_neuron_part_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronsPartHere exceeded threshold")
AssertionError: 120.97685861587524 not less than 10.0 : NeuronsPartHere exceeded threshold

======================================================================
FAIL: test_03_synaptic_queries (src.test.test_query_performance.QueryPerformanceTest)
Test synaptic terminal queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 139, in test_03_synaptic_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronsSynaptic exceeded threshold")
AssertionError: 120.82902216911316 not less than 10.0 : NeuronsSynaptic exceeded threshold

======================================================================
FAIL: test_04_anatomy_hierarchy_queries (src.test.test_query_performance.QueryPerformanceTest)
Test anatomical hierarchy queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 177, in test_04_anatomy_hierarchy_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "ComponentsOf exceeded threshold")
AssertionError: 120.80693650245667 not less than 10.0 : ComponentsOf exceeded threshold

======================================================================
FAIL: test_05_new_queries (src.test.test_query_performance.QueryPerformanceTest)
Test newly implemented queries
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/runner/work/VFBquery/VFBquery/src/test/test_query_performance.py", line 214, in test_05_new_queries
    self.assertLess(duration, self.THRESHOLD_SLOW, "NeuronClassesFasciculatingHere exceeded threshold")
AssertionError: 120.92229533195496 not less than 10.0 : NeuronClassesFasciculatingHere exceeded threshold

----------------------------------------------------------------------
Ran 6 tests in 1574.040s

FAILED (failures=5)
VFBquery caching enabled: TTL=2160h (90 days), Memory=2048MB
VFBquery functions patched with caching support
VFBquery: Caching enabled by default (3-month TTL, 2GB memory)
         Disable with: export VFBQUERY_CACHE_ENABLED=false

================================================================================
TERM INFO QUERIES
================================================================================
DEBUG: Cache lookup for FBbt_00003748: MISS
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ERROR: Owlery instances request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
get_term_info (mushroom body): 1089.6296s ✅

================================================================================
NEURON PART OVERLAP QUERIES
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
NeuronsPartHere: 120.9769s ✅

================================================================================
SYNAPTIC TERMINAL QUERIES
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
NeuronsSynaptic: 120.8290s ✅

================================================================================
ANATOMICAL HIERARCHY QUERIES
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
ComponentsOf: 120.8069s ✅

================================================================================
NEW QUERIES (2025)
================================================================================
ERROR: Owlery request failed: HTTPConnectionPool(host='owl.virtualflybrain.org', port=80): Read timed out. (read timeout=120)
NeuronClassesFasciculatingHere: 120.9223s ✅

================================================================================
INSTANCE QUERIES
================================================================================
ListAllAvailableImages: 0.8736s ✅

================================================================================
PERFORMANCE TEST SUMMARY
================================================================================
All performance tests completed!
================================================================================
test_term_info_performance (src.test.term_info_queries_test.TermInfoQueriesTest)
Performance test for specific term info queries. ... ok

----------------------------------------------------------------------
Ran 1 test in 1.614s

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
FBbt_00003748 query took: 0.8482 seconds
VFB_00101567 query took: 0.7654 seconds
Total time for both queries: 1.6136 seconds
Performance Level: 🟡 Good (1.5-3 seconds)
==================================================
Performance test completed successfully!
```

## Summary

✅ **Test Status**: Performance tests completed

### Test Statistics

- **Total Tests**: 7
- **Passed**: -24 ✅
- **Failed**: 5 ❌
- **Errors**: 26 ⚠️

### Query Performance Details

| Query | Duration | Status |
|-------|----------|--------|
| NeuronsPartHere | 120.9769s | ✅ Pass |
| NeuronsSynaptic | 120.8290s | ✅ Pass |
| ComponentsOf | 120.8069s | ✅ Pass |
| NeuronClassesFasciculatingHere | 120.9223s | ✅ Pass |
| ListAllAvailableImages | 0.8736s | ✅ Pass |

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
*Last updated: 2025-11-07 14:03:11 UTC*
