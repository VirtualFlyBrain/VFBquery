"""
VFBquery High-Availability API Server

Drop-in replacement for the V3 backend that serves VFBquery results
over HTTP. Uses a bounded process pool (default: 10 workers) so that
Neo4j is never hit by more than N simultaneous connections. Incoming
requests that exceed the pool size are queued and held open until a
worker becomes available.

Backpressure features:
    - Request coalescing:  identical in-flight queries share one worker
    - In-memory result cache (default TTL 5 min): recent results bypass the queue
    - Queue depth limit:   returns 503 when the backlog exceeds a threshold

Endpoints (mirrors v3-cached.virtualflybrain.org):
    GET /get_term_info?id=<short_form>
    GET /run_query?id=<short_form>&query_type=<QueryType>
    GET /resolve_entity?query=<name_or_symbol>         # IDs rewritten to names
    GET /find_stocks?id=<resolved_flybase_feature_id>
    GET /resolve_combination?query=<name_or_synonym>   # IDs rewritten to names
    GET /find_combo_publications?id=<resolved_fbco_id>
    GET /list_connectome_datasets
    GET /query_connectivity?upstream_type=<name>&downstream_type=<name>
    GET /get_hierarchy?id=<VFB id>[&relationship=&direction=&max_depth=]
    GET /search?query=<free_text>                      # canonical website search
    GET /xref?id=<VFB id> | ?accession=<external id>[&db=<site>]
    GET /health
    GET /status          — queue depth, cache stats & worker utilisation

Usage:
    python -m vfbquery.ha_api                    # default: port 8080, 10 workers
    python -m vfbquery.ha_api --port 8080 --workers 8
    VFBQUERY_WORKERS=10 python -m vfbquery.ha_api
"""

import argparse
import collections
import ipaddress
import json
import logging
import os
import re
import sys
import asyncio
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from functools import partial

import aiohttp
from aiohttp import web
import numpy as np

# Pure standard-library module: the /combine expression language, its set
# algebra and its explanations. Imported at module scope because it costs
# nothing to import (no pysolr, no neo4j, no navis) — everything expensive in
# this file is still imported lazily inside the handler that needs it.
from . import combine

# ---------------------------------------------------------------------------
# Running-version helper — surfaced in /health and /status so v2-dev and
# Rancher operators can confirm which build is actually serving a request
# without having to inspect Docker tags. Source of truth, in order:
#   1. importlib.metadata.version("vfbquery") — set by the CI tag-sync step
#      in docker.yml, so it reflects the deployed image's git tag.
#   2. vfbquery.__version__ — module constant; lags the tag until the CI
#      sync rewrites it, kept as a fallback for local/dev runs.
#   3. "unknown" — if both fail (would indicate a broken install).
# ---------------------------------------------------------------------------
def _get_running_version() -> str:
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version("vfbquery")
        except PackageNotFoundError:
            pass
    except Exception:
        pass
    try:
        import vfbquery
        return getattr(vfbquery, "__version__", "unknown")
    except Exception:
        return "unknown"


VFBQUERY_VERSION = _get_running_version()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("vfbquery.ha_api")

# Default number of worker processes — deliberately low to limit the number
# of concurrent Neo4j connections.  Override with VFBQUERY_WORKERS env var
# or --workers CLI flag.
DEFAULT_WORKERS = 10
DEFAULT_MAX_QUEUE_DEPTH = 200
_FLYBASE_FEATURE_ID_RE = re.compile(r"^FB(?:gn|al|ti|st|co)\d+$", re.IGNORECASE)
_FBCO_ID_RE = re.compile(r"^FBco\d+$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Result cache — short-lived L1 cache in the event-loop process so that
# recently-computed results are returned without dispatching a worker.
# ---------------------------------------------------------------------------

#: Cache ceilings. Two of them, because the cache holds two very different
#: shapes and either one alone leaves a hole:
#:
#: * ``MAX_ENTRIES`` bounds *how many* results are held. Before ``/search`` every
#:   cache key was derived from a resolvable VFB id, so the key space was
#:   roughly the size of the corpus. ``/search`` keys on arbitrary text — Solr
#:   answers 200 to any string — and ``rows`` is a second free dimension, so a
#:   crawler (or a load test) mints a fresh entry per request and nothing but
#:   the 300 s TTL ever lets go of it.
#: * ``MAX_ROWS`` bounds *how big* they are. A few results are enormous on their
#:   own (``RESULT_ROW_CAP`` allows 25 000 rows; an unlimited ``/search`` for a
#:   common word ranks ~1 500), so an entry count alone does not bound memory.
#:
#: Eviction is LRU, so the generous row ceiling only bites when memory is
#: genuinely at risk and it takes the coldest entries first rather than the
#: biggest.
#: Named so a test can assert the relationship between the shipped defaults
#: without reading the deploy's environment (see ``RESULT_ROW_CAP`` below).
DEFAULT_CACHE_MAX_ENTRIES = 1000
DEFAULT_CACHE_MAX_ROWS = 100000


def _int_env(name, default):
    """A deploy knob read from the environment, with one rule for every way of
    not setting it.

    Unset, empty and unparseable all give the shipped default. Empty matters
    because that is what an unset value looks like coming out of a k8s env
    block (``value: ""``, or a ConfigMap key that isn't there); unparseable
    matters because the alternative is a process that won't start over a typo
    in a tuning parameter.
    """
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        log.warning("%s=%r is not an integer; using %s", name, raw, default)
        return default


CACHE_MAX_ENTRIES = _int_env("VFBQUERY_CACHE_MAX_ENTRIES",
                             DEFAULT_CACHE_MAX_ENTRIES)
CACHE_MAX_ROWS = _int_env("VFBQUERY_CACHE_MAX_ROWS", DEFAULT_CACHE_MAX_ROWS)


class ResultCache:
    """In-memory LRU cache with a TTL and a bound on both entries and rows.

    Runs in the single-threaded event loop so no locks are needed.
    """

    def __init__(self, ttl_seconds: int = 300,
                 max_entries: int = None, max_rows: int = None):
        # OrderedDict, not dict: eviction needs "least recently *used*", and a
        # plain dict can only give least recently *inserted*.
        self._store = collections.OrderedDict()   # key -> (result, ts, weight)
        self._ttl = ttl_seconds
        self._max_entries = (CACHE_MAX_ENTRIES if max_entries is None
                             else max_entries)
        self._max_rows = CACHE_MAX_ROWS if max_rows is None else max_rows
        self._rows = 0
        self._hits = 0
        self._evicted = 0

    @staticmethod
    def _weight(result):
        """Size of a result in list elements, floored at 1.

        The bulk of any payload here is a single list, and it is the only part
        that varies by orders of magnitude — so it is a good enough proxy for
        size without paying for a serialisation. Which *key* holds that list
        varies (``rows`` across the query endpoints, ``connections`` for
        ``/query_connectivity``), so this takes the longest top-level list
        rather than naming keys.

        Naming them is how this bound was first defeated: ``/query_connectivity``
        answers ``{"connections": [...], "warnings": [...], "count": n}`` with no
        ``rows`` key at all, and a real one (Tm1 -> T3 neuron at the default
        weight) carries ~12 000 connections. Weighed by name it counted 1, so a
        thousand of them read as 1 000 against the 100 000 ceiling while holding
        twelve million. Taking the longest list means the next endpoint to
        invent a key cannot repeat that.
        """
        if isinstance(result, list):
            return max(1, len(result))
        if isinstance(result, dict):
            longest = 0
            for value in result.values():
                if isinstance(value, list) and len(value) > longest:
                    longest = len(value)
            return max(1, longest)
        return 1

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        result, ts, weight = entry
        if time.monotonic() - ts > self._ttl:
            self._drop(key)
            return None
        self._store.move_to_end(key)
        self._hits += 1
        return result

    def put(self, key: str, result):
        self._drop(key)                 # replacing: don't double-count its rows
        weight = self._weight(result)
        self._store[key] = (result, time.monotonic(), weight)
        self._rows += weight
        self._evict_to_fit()

    def _drop(self, key: str):
        entry = self._store.pop(key, None)
        if entry is not None:
            self._rows -= entry[2]

    def _evict_to_fit(self):
        # popitem(last=False) is the least recently used end; the entry just
        # written is at the other, so it is evicted last rather than first.
        #
        # Last, not never: a result whose own row count exceeds ``max_rows``
        # ends up alone in the store and is then dropped as well. That is
        # deliberate — the ceiling is a bound on memory, and an exemption for
        # one entry means it is not one. The cost is that such a result is
        # never cached (a permanent miss, not a wrong answer), which is why
        # ``max_rows`` sits four times ``RESULT_ROW_CAP``: no single result can
        # reach it in a sane configuration, and an insane one
        # shows up on /status as ``cache_evicted`` climbing against a flat hit
        # rate rather than as a silent memory ceiling nobody set.
        while self._store and (len(self._store) > self._max_entries
                               or self._rows > self._max_rows):
            key, entry = self._store.popitem(last=False)
            self._rows -= entry[2]
            self._evicted += 1

    def invalidate(self, key: str):
        """Forcibly drop an entry — used by handlers that honour
        force_refresh so a known-stale result is replaced rather than
        served from cache. No-op if the key isn't present."""
        self._drop(key)

    def evict_expired(self):
        now = time.monotonic()
        expired = [k for k, (_, ts, _w) in self._store.items()
                   if now - ts > self._ttl]
        for k in expired:
            self._drop(k)
        return len(expired)

    @property
    def size(self):
        return len(self._store)

    @property
    def rows(self):
        return self._rows

    @property
    def evicted(self):
        return self._evicted

    @property
    def hits(self):
        return self._hits


# ---------------------------------------------------------------------------
# Request coalescer — deduplicates concurrent identical queries so that
# only one worker executes each unique (endpoint, id, query_type).
# ---------------------------------------------------------------------------

class Overloaded(Exception):
    """Raised *into* coalesced waiters when the owner sheds instead of running.

    Shedding is the one path where the owner of a coalescer future returns
    without ever producing a result. Dropping the key is not enough: every
    request that already coalesced onto it is awaiting that future, and nothing
    will ever settle it, so those handlers never return. The hang is likeliest
    at exactly the wrong moment, because load-shedding implies concurrent
    identical traffic — which is what coalescing is for.

    Carrying the 503 as an exception lets waiters answer with the same 503 the
    owner sent rather than a 500 about an internal failure that did not happen.
    """

    def __init__(self, message, retry_after="5"):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after


def _overloaded_response(exc):
    return web.json_response({"error": exc.message}, status=503,
                             headers={"Retry-After": exc.retry_after})


def _failure_response(message, exc, context, coalesced=False):
    """A 500 that describes the failure without shipping the traceback.

    Every handler here used to answer ``{"error": ..., "detail":
    traceback.format_exc()}``. Two problems with that. It puts absolute server
    paths, source lines and internal frame names in a body any client can read
    — free reconnaissance for anyone probing the service, and, more mundanely,
    the first workshop attendee to hit a 500 will paste the whole thing into a
    public chat window. And on the coalesced-waiter halves the formatted
    traceback was the *only* record: rendered into the response and never
    logged, so a failure a client saw left nothing behind on the server.

    So the split is: full traceback to the log, exception type and message to
    the client. The type and message are the part a caller can act on
    ("ClientConnectorError: Cannot connect to host solr:8983") — the frames
    only ever mattered to whoever can read the log anyway.

    ``coalesced`` marks the waiter half, which logs at WARNING rather than
    ERROR. The owner logs the same underlying failure at ERROR; a waiter
    logging at ERROR too would multiply one incident by however many requests
    happened to coalesce onto it.
    """
    (log.warning if coalesced else log.error)(
        "%s — FAILED%s\n%s",
        context, " (coalesced waiter)" if coalesced else "",
        traceback.format_exc(),
    )
    return web.json_response(
        {"error": message, "detail": "%s: %s" % (type(exc).__name__, exc)},
        status=500,
    )


async def _shed(coalescer, fut, cache_key, message, retry_after="5"):
    """Unregister the key, fail its future, and build the 503 to return.

    Order matters: remove first, so no fresh request can attach to a future
    that is about to be failed.
    """
    exc = Overloaded(message, retry_after)
    await coalescer.remove(cache_key)
    if not fut.done():
        fut.set_exception(exc)
        # Mark it retrieved. If nobody coalesced onto this key there is no
        # waiter to consume the exception, and asyncio would log a spurious
        # "Future exception was never retrieved" when it is collected.
        fut.exception()
    return _overloaded_response(exc)


def _abandon(coalescer, fut, cache_key):
    """Backstop for the coalescer contract: settle a future its owner left open.

    ``except Exception`` is not enough on its own. ``asyncio.CancelledError`` is
    a ``BaseException``, so an owner cancelled between ``get_or_create`` and the
    ``set_result`` used to return having neither removed the key nor settled the
    future. That is worse than the shed hang it resembles, because it never
    heals: the key stays registered for the life of the process and *every*
    later request for the same query parks on a future nobody will complete.

    Call it from ``finally``. On every path that settled normally the future is
    already done and this is a no-op.

    Deliberately synchronous. It runs while a ``CancelledError`` is propagating,
    where awaiting is exactly the thing that may not get a chance to finish; a
    dict pop on a single-threaded loop needs no await point, which is why
    :meth:`RequestCoalescer.discard` exists alongside ``remove``.
    """
    if fut.done():
        return
    coalescer.discard(cache_key)
    fut.set_exception(Overloaded("Request aborted, please retry", retry_after="1"))
    fut.exception()                     # see _shed: keeps asyncio quiet at GC


class RequestCoalescer:
    """When multiple requests arrive for the same query while it is
    already in-flight, they all await the same Future instead of each
    consuming a worker slot."""

    def __init__(self):
        self._in_flight: dict = {}      # key -> asyncio.Future
        self._lock = asyncio.Lock()
        self._coalesced = 0

    async def get_or_create(self, key: str):
        """Return *(future, is_owner)*.  The owner **must** eventually
        resolve or reject the future and call :meth:`remove`."""
        async with self._lock:
            if key in self._in_flight:
                self._coalesced += 1
                return self._in_flight[key], False
            fut = asyncio.get_event_loop().create_future()
            self._in_flight[key] = fut
            return fut, True

    async def remove(self, key: str):
        async with self._lock:
            self._in_flight.pop(key, None)

    def discard(self, key: str):
        """``remove`` without the await, for cleanup during cancellation.

        The lock guards a check-then-set in ``get_or_create``; this is a single
        pop, and the loop is single-threaded, so there is no window for it to
        interleave with anything. See :func:`_abandon` for why the await has to
        go.
        """
        self._in_flight.pop(key, None)

    @property
    def coalesced_total(self):
        return self._coalesced

    @property
    def in_flight_count(self):
        return len(self._in_flight)


# ---------------------------------------------------------------------------
# Queue tracker — keeps an atomic count of active + waiting requests so the
# /status endpoint and log lines can report backpressure.
# ---------------------------------------------------------------------------

class QueueTracker:
    """Lightweight counters for in-flight and waiting requests."""

    def __init__(self):
        self._active = 0
        self._waiting = 0
        self._total_served = 0
        self._lock = asyncio.Lock()

    async def enter_queue(self):
        async with self._lock:
            self._waiting += 1

    async def leave_queue_start_work(self):
        async with self._lock:
            self._waiting -= 1
            self._active += 1

    async def finish_work(self, started: bool = True):
        """Release whichever counter this request is holding.

        ``started=False`` means it never got a worker slot — cancelled while
        still queued on the semaphore, so ``leave_queue_start_work`` never ran
        and what it holds is a *waiting* slot, not an *active* one. Decrementing
        ``active`` there leaks ``waiting`` permanently and drives ``active``
        negative; once the leaked ``waiting`` reaches ``max_queue_depth`` the
        queue guard answers 503 to every request, on an idle server, until
        restart.
        """
        async with self._lock:
            if started:
                self._active -= 1
                self._total_served += 1
            else:
                self._waiting -= 1

    @property
    def snapshot(self):
        return {
            "active": self._active,
            "waiting": self._waiting,
            "total_served": self._total_served,
        }

# ---------------------------------------------------------------------------
# Security — path allowlist
# Only these paths are served; everything else gets an empty 404 so that
# vulnerability scanners learn nothing about the stack.
# ---------------------------------------------------------------------------

ALLOWED_PATHS = frozenset({
    "/get_term_info", "/run_query", "/health", "/status",
    "/resolve_entity", "/find_stocks",
    "/resolve_combination", "/find_combo_publications",
    "/list_connectome_datasets", "/query_connectivity",
    "/search", "/xref", "/combine", "/get_hierarchy",
})
# NB /get_hierarchy_html is a registered route and is deliberately absent here,
# so it 404s for any client outside TRUSTED_NETWORKS. It is not a query — it is
# the pre-rendered HTML the geppetto site's ROI browser consumes, produced by
# the same worker /get_hierarchy uses. Publishing it would make one consumer's
# markup part of the API's compatibility surface for no gain, since the JSON
# carries the same tree. _warn_unreachable_routes() logs the divergence at
# startup so it stays visible instead of being rediscovered as a mystery 404.


# Trusted internal networks. Traffic from the Rancher/Canal pod network and
# loopback is in-cluster (the V3 cache, the frontend backend, the post-release
# warmup tool) -- never a vulnerability scanner -- so it must not be caught by
# the scanner-probe block. Override with TRUSTED_NETWORKS (comma-separated CIDRs).
def _load_trusted_networks():
    raw = os.environ.get("TRUSTED_NETWORKS", "10.42.0.0/16,127.0.0.0/8,::1/128")
    nets = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        try:
            nets.append(ipaddress.ip_network(token, strict=False))
        except ValueError:
            log.warning("Ignoring invalid TRUSTED_NETWORKS entry: %s", token)
    return tuple(nets)


TRUSTED_NETWORKS = _load_trusted_networks()


def _is_trusted_remote(remote):
    """True if `remote` (request.remote) falls in a trusted internal network."""
    if not remote:
        return False
    try:
        ip = ipaddress.ip_address(remote)
    except ValueError:
        return False
    return any(ip in net for net in TRUSTED_NETWORKS)


def unreachable_routes(app):
    """Registered GET paths that ALLOWED_PATHS will 404 for external clients.

    The two lists are maintained by hand in different parts of this file, so
    they drift silently: a new route works from inside the cluster, passes any
    test run against localhost, and 404s in production. Returns the difference
    so it can be logged rather than discovered.
    """
    registered = set()
    for route in app.router.routes():
        path = getattr(route.resource, "canonical", None)
        if path:
            registered.add(path)
    return sorted(registered - set(ALLOWED_PATHS))


def _warn_unreachable_routes(app):
    missing = unreachable_routes(app)
    if missing:
        log.warning(
            "Routes registered but not in ALLOWED_PATHS — these 404 for any "
            "client outside TRUSTED_NETWORKS: %s", ", ".join(missing))
    return missing


@web.middleware
async def security_middleware(request, handler):
    """Reject requests to unknown paths with a minimal 404.

    Trusted in-cluster traffic (TRUSTED_NETWORKS) bypasses the scanner-probe
    block and is passed to normal routing -- an unknown path still 404s via the
    router, but is not counted or logged as a probe.
    """
    if request.path not in ALLOWED_PATHS and not _is_trusted_remote(request.remote):
        probes = request.app.get("_scanner_probes")
        if probes is None:
            probes = {"count": 0}
            request.app["_scanner_probes"] = probes
        probes["count"] += 1
        count = probes["count"]
        # Log first occurrence per path, then every 100th to avoid flooding
        if count <= 10 or count % 100 == 0:
            log.warning(
                "Blocked probe #%d: %s %s from %s",
                count, request.method, request.path, request.remote,
            )
        return web.Response(status=404)
    return await handler(request)


# ---------------------------------------------------------------------------
# Query-type → VFBquery function mapping
#
# Every key that the V3 caching layer can send as `query_type` is listed
# here.  The value is the function name inside `vfbquery` that should be
# called with  (short_form, return_dataframe=False).
#
# If we ever add new queries to VFBquery we just add a row here and the
# server picks it up automatically on next restart.
# ---------------------------------------------------------------------------
QUERY_TYPE_MAP = {
    # Anatomical / hierarchy
    "PartsOf":                      "get_parts_of",
    "ComponentsOf":                 "get_components_of",
    "SubclassesOf":                 "get_subclasses_of",
    "SplitsTargeting":              "get_splits_targeting",
    "TargetNeurons":                "get_neurons_targeted_by_split",

    # Neurons in region
    "NeuronsPartHere":              "get_neurons_with_part_in",
    "NeuronsCapableOf":             "get_neurons_capable_of",
    "NeuronsSynaptic":              "get_neurons_with_synapses_in",
    "NeuronsPresynapticHere":       "get_neurons_with_presynaptic_terminals_in",
    "NeuronsPostsynapticHere":      "get_neurons_with_postsynaptic_terminals_in",
    "NeuronClassesFasciculatingHere": "get_neuron_classes_fasciculating_here",
    "TractsNervesInnervatingHere":  "get_tracts_nerves_innervating_here",
    "LineageClonesIn":              "get_lineage_clones_in",

    # Individual neuron queries
    "NeuronInputsTo":               "get_individual_neuron_inputs",

    # Connectivity
    "NeuronNeuronConnectivityQuery": "get_neuron_neuron_connectivity",
    "NeuronRegionConnectivityQuery": "get_neuron_region_connectivity",
    "DownstreamClassConnectivity":   "get_downstream_class_connectivity",
    "UpstreamClassConnectivity":     "get_upstream_class_connectivity",

    # Similarity / NBLAST
    "SimilarMorphologyTo":           "get_similar_neurons",
    "SimilarMorphologyToPartOf":     "get_similar_morphology_part_of",
    "SimilarMorphologyToPartOfexp":  "get_similar_morphology_part_of_exp",
    "SimilarMorphologyToNB":         "get_similar_morphology_nb",
    "SimilarMorphologyToNBexp":      "get_similar_morphology_nb_exp",
    "SimilarMorphologyToUserData":   "get_similar_morphology_userdata",

    # Images
    "ListAllAvailableImages":        "get_instances",
    "ImagesNeurons":                 "get_images_neurons",
    "ImagesThatDevelopFrom":         "get_images_that_develop_from",
    "epFrag":                        "get_expression_pattern_fragments",

    # Expression
    "AnatomyExpressedIn":            "get_expression_overlaps_here",
    "TransgeneExpressionHere":       "get_transgene_expression_here",

    # Transcriptomics
    "anatScRNAseqQuery":             "get_anatomy_scrnaseq",
    "clusterExpression":             "get_cluster_expression",
    "expressionCluster":             "get_expression_cluster",
    "scRNAdatasetData":              "get_scrnaseq_dataset_data",

    # Templates / datasets
    "PaintedDomains":                "get_painted_domains",
    "TemplateROIBrowser":            "get_template_roi_tree",
    "DatasetImages":                 "get_dataset_images",
    "AllAlignedImages":              "get_all_aligned_images",
    "AlignedDatasets":               "get_aligned_datasets",
    "AllDatasets":                   "get_all_datasets",

    # Publications
    "TermsForPub":                   "get_terms_for_pub",

    # FlyBase integration
    "FindStocks":                    "get_flybase_stocks",
    "FindComboPublications":         "get_flybase_combo_pubs",
}


# ---------------------------------------------------------------------------
# Worker process — runs in its own process via ProcessPoolExecutor so the
# GIL in the main event-loop process is never blocked.
# ---------------------------------------------------------------------------

def _init_worker():
    """Import vfbquery once per worker process."""
    global _vfb
    # Disable caching print spam in worker processes
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        import vfbquery as _vfb


def _run_term_info(short_form, force_refresh=False):
    """Execute get_term_info in a worker process. Returns JSON-serialisable dict.

    ``force_refresh`` is forwarded to ``get_term_info`` so the underlying
    ``@with_solr_cache('term_info')`` entry is recomputed and rewritten rather
    than served stale.
    """
    result = _vfb.get_term_info(short_form, force_refresh=force_refresh)
    return _convert_numpy_types(result)


def _run_query(short_form, func_name, force_refresh=False, offset=0, limit=0):
    """Execute a named query function in a worker process. Returns JSON-serialisable dict.

    ``force_refresh`` is propagated to the underlying ``vfb_queries`` function
    only when that function declares it in its signature (e.g. anything
    decorated with ``@with_solr_cache``). The same introspection pattern is
    used elsewhere — see ``vfb_queries.fill_query_results`` for the original.
    """
    fn = getattr(_vfb, func_name)
    base_kwargs = {"return_dataframe": False}
    if func_name in PAGED_QUERY_FUNCS:
        base_kwargs["offset"] = offset
        base_kwargs["limit"] = limit if (limit and limit > 0) else -1

    # Defensive force_refresh forwarding.
    #
    # Earlier attempts (v1.12.9, v1.12.10) used inspect.signature() to decide
    # whether the target accepted force_refresh, but neither shape works
    # reliably:
    #   - Without @functools.wraps, signature() reports `(*args, **kwargs)`
    #     and we needed a VAR_KEYWORD check.
    #   - With @functools.wraps (added in v1.12.10), signature() reports the
    #     *inner* function's parameters, hiding the wrapper's **kwargs.
    # In both cases the wrapper still accepts force_refresh at the call
    # level — but introspection can't see that. Stop introspecting; just
    # try the call, and on TypeError fall back to the version without
    # force_refresh. The wrapper pops the flag before delegating, so no
    # inner function ever gets force_refresh as an unexpected kwarg.
    def _call(extra=None):
        kw = {**base_kwargs, **(extra or {})}
        def _invoke(kwargs):
            if func_name == "get_all_datasets":
                return fn(**kwargs)
            return fn(short_form, **kwargs)
        try:
            return _invoke(kw)
        except TypeError as e:
            # Belt-and-braces: a target that does not declare offset/limit (e.g.
            # a cached wrapper not yet updated) must not 500 -- drop the paging
            # kwargs and retry once. Real paging targets never hit this.
            msg = str(e)
            if ("offset" in msg or "limit" in msg) and ("offset" in kw or "limit" in kw):
                stripped = {k: v for k, v in kw.items() if k not in ("offset", "limit")}
                log.warning("_run_query: %s does not accept paging kwargs (%s); retrying without offset/limit.", func_name, e)
                return _invoke(stripped)
            raise

    if force_refresh:
        try:
            result = _call({"force_refresh": True})
        except TypeError as e:
            # Target function didn't accept force_refresh after all.
            # Log and retry without — better to serve a cached value than
            # to error.
            log.warning(
                "_run_query: %s did not accept force_refresh (%s); "
                "retrying without it. SOLR cache may not be invalidated.",
                func_name, e,
            )
            result = _call()
    else:
        result = _call()

    # Convert numpy types to Python types for JSON serialization
    return _convert_numpy_types(result)


def _run_resolve_entity(name_or_id):
    """Execute resolve_entity in a worker process."""
    query = _rewrite_resolve_entity_query(name_or_id)
    return _vfb.resolve_entity(query)


def _run_find_stocks(feature_id, collection_filter):
    """Execute find_stocks in a worker process."""
    return _vfb.find_stocks(feature_id, collection_filter=collection_filter)


def _run_resolve_combination(name_or_id):
    """Execute resolve_combination in a worker process."""
    query = _rewrite_resolve_combination_query(name_or_id)
    return _vfb.resolve_combination(query)


def _run_find_combo_publications(fbco_id):
    """Execute find_combo_publications in a worker process."""
    return _vfb.find_combo_publications(fbco_id)


def _run_list_connectome_datasets():
    """Execute list_connectome_datasets in a worker process."""
    return _vfb.list_connectome_datasets()


def _run_query_connectivity(upstream_type, downstream_type, weight,
                            group_by_class, exclude_dbs, force_refresh=False):
    """Execute query_connectivity in a worker process."""
    return _vfb.query_connectivity(
        upstream_type=upstream_type,
        downstream_type=downstream_type,
        weight=weight,
        group_by_class=group_by_class,
        exclude_dbs=exclude_dbs,
        force_refresh=force_refresh,
    )


# ---------------------------------------------------------------------------
# Graph post-processing — mapping from query function name to graph converter
# ---------------------------------------------------------------------------

_GRAPH_CONVERTERS = {
    "get_neuron_neuron_connectivity": "graph_from_neuron_neuron",
    "get_neuron_region_connectivity": "graph_from_neuron_region",
    "get_downstream_class_connectivity": "graph_from_downstream_class",
    "get_upstream_class_connectivity": "graph_from_upstream_class",
}


def _maybe_add_graph(result, func_name, short_form):
    """Add a graph representation to *result* if the query type supports it.

    Returns a shallow copy with the ``graph`` key added, so the original
    cached dict is never mutated.
    """
    converter_name = _GRAPH_CONVERTERS.get(func_name)
    if not converter_name or not isinstance(result, dict):
        return result

    try:
        from . import graph_builder
        converter = getattr(graph_builder, converter_name)
        rows = result.get("rows", [])
        if not rows:
            return result
        graph = converter(rows, short_form, short_form)
        if graph is not None:
            result = dict(result)  # shallow copy to avoid mutating cache
            result["graph"] = graph
    except Exception as exc:
        log.warning("Graph generation failed for %s(%s): %s", func_name, short_form, exc)
    return result


def _convert_numpy_types(obj):
    """Recursively convert numpy types to Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def _parse_resolver_query(query):
    """Normalise a resolver query parameter."""
    normalized = (query or "").strip()
    if not normalized:
        raise ValueError("Missing required parameter: query")
    return normalized


def _canonicalize_flybase_feature_id(feature_id):
    """Return canonical FlyBase casing for a supported feature ID."""
    match = re.match(r"^FB(gn|al|ti|st|co)(\d+)$", feature_id or "", re.IGNORECASE)
    if not match:
        return feature_id
    return f"FB{match.group(1).lower()}{match.group(2)}"


def _canonicalize_fbco_id(fbco_id):
    """Return canonical FlyBase casing for an FBco ID."""
    match = re.match(r"^FBco(\d+)$", fbco_id or "", re.IGNORECASE)
    if not match:
        return fbco_id
    return f"FBco{match.group(1)}"


def _preferred_term_info_query(term_info):
    """Pick a stable name/label from VFB term_info."""
    if not isinstance(term_info, dict):
        return None

    candidate = (term_info.get("Name") or "").strip()
    if candidate:
        return candidate

    meta = term_info.get("Meta")
    if isinstance(meta, dict):
        for key in ("Symbol", "Name"):
            candidate = (meta.get(key) or "").strip()
            if candidate:
                match = re.match(r"^\[(.+)\]\([^)]+\)$", candidate)
                return match.group(1) if match else candidate

    return None


def _rewrite_resolve_entity_query(name_or_id):
    """Rewrite a FlyBase feature ID to a preferred VFB term name when available."""
    query = _parse_resolver_query(name_or_id)
    if not _FLYBASE_FEATURE_ID_RE.match(query):
        return query

    canonical_id = _canonicalize_flybase_feature_id(query)
    term_info = _vfb.get_term_info(canonical_id, preview=False)
    return _preferred_term_info_query(term_info) or canonical_id


def _rewrite_resolve_combination_query(name_or_id):
    """Rewrite an FBco ID to a preferred VFB term name when available."""
    query = _parse_resolver_query(name_or_id)
    if not _FBCO_ID_RE.match(query):
        return query

    canonical_id = _canonicalize_fbco_id(query)
    term_info = _vfb.get_term_info(canonical_id, preview=False)
    return _preferred_term_info_query(term_info) or canonical_id


# ---------------------------------------------------------------------------
# HTTP handlers
# ---------------------------------------------------------------------------

async def handle_get_term_info(request):
    """GET /get_term_info?id=<short_form>"""
    short_form = request.query.get("id")
    if not short_form:
        return web.json_response(
            {"error": "Missing required parameter: id"}, status=400
        )

    force_refresh = request.query.get("force_refresh", "false").lower() in ("true", "1", "yes")

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]
    key = f"term_info:{short_form}"

    # ---- L1: in-memory result cache ----
    # force_refresh=true skips the cache read AND drops any stale entry so the
    # recomputed result replaces it; it is also propagated to get_term_info so
    # the underlying SOLR term_info cache entry is rewritten.
    if force_refresh:
        rcache.invalidate(key)
        log.info("get_term_info id=%s — force_refresh: cache invalidated", short_form)
    else:
        cached = rcache.get(key)
        if cached is not None:
            log.info("get_term_info id=%s — cache hit", short_form)
            return web.json_response(cached)

    # ---- Coalescing: piggyback on identical in-flight query ----
    fut, is_owner = await coalescer.get_or_create(key)
    if not is_owner:
        log.info("get_term_info id=%s — coalesced", short_form)
        try:
            result = await fut
            return web.json_response(result)
        except Overloaded as exc:
            return _overloaded_response(exc)
        except Exception as exc:
            return _failure_response(
                f"Query failed for id={short_form}", exc,
                f"get_term_info id={short_form}", coalesced=True,
            )

    # ---- Queue depth guard ----
    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            log.warning(
                "get_term_info id=%s — rejected (queue full: waiting=%d >= %d)",
                short_form, snap["waiting"], max_queue,
            )
            return await _shed(coalescer, fut, key,
                               "Server overloaded, please retry later",
                               retry_after="30")

    # ---- Enter the bounded worker queue ----
    pool = request.app["pool"]
    sem = request.app["semaphore"]

    await tracker.enter_queue()
    snap = tracker.snapshot
    log.info(
        "get_term_info id=%s — queued  (active=%d waiting=%d)",
        short_form, snap["active"], snap["waiting"],
    )
    started = False
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            started = True
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(pool, _run_term_info, short_form, force_refresh)
        log.info("get_term_info id=%s — done", short_form)
        rcache.put(key, result)
        await coalescer.remove(key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        await coalescer.remove(key)
        if not fut.done():
            fut.set_exception(exc)
        return _failure_response(
            f"Query failed for id={short_form}", exc,
            f"get_term_info id={short_form}",
        )
    finally:
        # _abandon first, and synchronous: it is the one that must not be
        # skipped if this finally is itself interrupted.
        _abandon(coalescer, fut, key)
        await tracker.finish_work(started=started)


# Query functions that accept offset/limit paging (id ASC pages, <=10000 rows).
PAGED_QUERY_FUNCS = {
    "get_all_aligned_images",
    "get_images_neurons",
    "get_neurons_with_part_in",
    "get_neurons_with_synapses_in",
    "get_neurons_with_presynaptic_terminals_in",
    "get_neurons_with_postsynaptic_terminals_in",
    "get_components_of",
    "get_parts_of",
    "get_subclasses_of",
    "get_neuron_classes_fasciculating_here",
    "get_tracts_nerves_innervating_here",
    "get_lineage_clones_in",
    "get_images_that_develop_from",
    "get_neurons_capable_of",
    "get_expression_pattern_fragments",
    "get_instances",
}

# Hard safety cap on rows returned to the client for ANY query. Broad terms
# make many queries huge or unbounded (e.g. AllAlignedImages ~528k, and
# ListAllAvailableImages / connectivity / SubclassesOf on high-level classes
# return -1/"unresolved" counts = potentially millions). Returning those in one
# response is what caused the 430MB serialise-on-the-event-loop + websocket
# broken-pipe blowup. We always bound the payload here, keep the true total in
# "count", and flag "capped" so the UI can show "first N - refine". Override the
# cap with VFBQUERY_RESULT_ROW_CAP (default 25000; 0 disables). A malformed
# value falls back to the same default an unset one gets — a typo in a k8s env
# block should not quietly hand the deploy a different ceiling.
DEFAULT_RESULT_ROW_CAP = 25000
RESULT_ROW_CAP = _int_env("VFBQUERY_RESULT_ROW_CAP", DEFAULT_RESULT_ROW_CAP)

#: Response keys that carry the bulk list of a payload. ``rows`` is the
#: convention across the query endpoints; ``/query_connectivity`` predates it
#: and answers under ``connections``. The client's ``_ROW_KEYS`` is this same
#: list read from the other end, and the two must agree.
PAYLOAD_LIST_KEYS = ("rows", "connections")


def _cap_result_rows(result, cap=None):
    """Bound a result dict's bulk list to `cap` entries; no-op for anything else.

    ``connections`` is capped on the same terms as ``rows``: the blowup this
    guards against is the size of the serialised response, and
    ``/query_connectivity`` is capable of the largest payloads the service has.
    """
    if cap is None:
        cap = RESULT_ROW_CAP
    if not cap or not isinstance(result, dict):
        return result

    # Cap *every* over-cap key, not just the first one found. The earlier
    # `break`/`else` stopped at the first, which is fine while a payload
    # carries one bulk list — but the whole reason this function takes a tuple
    # of keys is that it cannot assume so, and a payload with both `rows` and
    # `connections` over cap would have gone out with one of them uncapped,
    # defeating the response-size bound this exists to enforce.
    oversized = [key for key in PAYLOAD_LIST_KEYS
                 if isinstance(result.get(key), list) and len(result[key]) > cap]
    if not oversized:
        return result

    capped = dict(result)
    for key in oversized:
        capped[key] = result[key][:cap]

    # `count` can only describe one list, so it describes the payload's primary
    # one: the first PAYLOAD_LIST_KEYS entry actually present. That is `rows`
    # wherever both appear, and is exactly the old behaviour for the
    # single-list payloads that are all this has ever seen in practice.
    primary = next((key for key in PAYLOAD_LIST_KEYS
                    if isinstance(result.get(key), list)), None)
    total = result.get("count")
    if primary is not None and (
            not isinstance(total, (int, float)) or total < len(result[primary])):
        total = len(result[primary])
    if total is not None:
        capped["count"] = total
    capped["limit"] = cap
    capped["capped"] = True
    return capped


# Ceiling for GENERIC (non-AllAlignedImages) paging. Non-paged query functions
# already return their full row set (they run with the default limit=-1); we
# cache that full set once and hand back the requested page slice, so any query
# whose count exceeds one page can be walked to completion by the client. Beyond
# this ceiling the full set is too large to hold/serve, so we truncate + flag.
# AllAlignedImages keeps its dedicated id-index paging (it is far bigger than
# this) and is excluded via PAGED_QUERY_FUNCS.
try:
    PAGING_CEILING = int(os.getenv("VFBQUERY_PAGING_CEILING", "50000") or "50000")
except ValueError:
    PAGING_CEILING = 50000


def _prepare_full_for_cache(result):
    """Cache the FULL processed row set for generic paging; truncate if huge.

    Non-paged functions return every row, so the cached full set lets the
    handler serve any offset slice without recompute. If the set exceeds the
    ceiling we keep the first PAGING_CEILING rows and flag ``truncated`` so the
    slicer reports the true total and stops cleanly.
    """
    if not isinstance(result, dict):
        return result
    rows = result.get("rows")
    if not isinstance(rows, list) or len(rows) <= PAGING_CEILING:
        return result
    total = result.get("count")
    if not isinstance(total, (int, float)) or total < len(rows):
        total = len(rows)
    trunc = dict(result)
    trunc["rows"] = rows[:PAGING_CEILING]
    trunc["count"] = total
    trunc["truncated"] = True
    return trunc


def _slice_page(result, offset=0, page_size=None):
    """Return the [offset, offset+page_size) slice of a cached full result.

    The authoritative total is ``len(rows)`` of the cached full set — so the
    count the client shows always matches the rows it can actually load. Only a
    ceiling-truncated result keeps its stored (larger, true) count.
    """
    page_size = page_size if (page_size and page_size > 0) else RESULT_ROW_CAP
    if not isinstance(result, dict):
        return result
    rows = result.get("rows")
    if not isinstance(rows, list):
        return result
    if result.get("truncated") and isinstance(result.get("count"), (int, float)):
        total = result["count"]
    else:
        total = len(rows)
    page_rows = rows[offset:offset + page_size]
    page = dict(result)
    page["rows"] = page_rows
    page["count"] = total
    page["offset"] = offset
    page["limit"] = page_size
    page["capped"] = (offset + len(page_rows)) < len(rows) or len(rows) < total
    return page


def _page_out(result, func_name, offset=0, page_size=None):
    """Finalise a result for sending: AllAlignedImages is already a single
    server page (just bound it); everything else is sliced from its full set."""
    if func_name in PAGED_QUERY_FUNCS:
        return _cap_result_rows(result)
    return _slice_page(result, offset, page_size)


async def handle_run_query(request):
    """GET /run_query?id=<short_form>&query_type=<QueryType>&include_graph=false"""
    short_form = request.query.get("id")
    query_type = request.query.get("query_type")

    if not query_type:
        return web.json_response(
            {"error": "Missing required parameter: query_type"}, status=400
        )

    func_name = QUERY_TYPE_MAP.get(query_type)
    if func_name is None:
        return web.json_response(
            {"error": f"Unknown query_type: {query_type}",
             "available": sorted(QUERY_TYPE_MAP.keys())},
            status=400,
        )

    # AllDatasets doesn't need an id; everything else does
    if func_name != "get_all_datasets" and not short_form:
        return web.json_response(
            {"error": "Missing required parameter: id"}, status=400
        )

    include_graph = request.query.get("include_graph", "false").lower() in ("true", "1", "yes")
    force_refresh = request.query.get("force_refresh", "false").lower() in ("true", "1", "yes")

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]
    # Paging params — only consumed by PAGED_QUERY_FUNCS; harmless otherwise.
    def _int_param(name, default):
        try:
            return int(request.query.get(name, default))
        except (TypeError, ValueError):
            return default
    offset = max(0, _int_param("offset", 0))
    limit = _int_param("limit", 0)  # 0/absent -> function default page size
    page_size = limit if (limit and limit > 0) else RESULT_ROW_CAP

    # Normalize key — AllDatasets ignores the id parameter
    if func_name == "get_all_datasets":
        key = "run_query::AllDatasets"
    else:
        key = f"run_query:{short_form}:{query_type}"
    if func_name in PAGED_QUERY_FUNCS:
        key = f"{key}:{offset}:{limit}"

    # ---- L1: in-memory result cache ----
    # force_refresh=true skips the cache read AND drops any stale entry so
    # the recomputed result replaces it. Otherwise the next request without
    # force_refresh would still get the stale value.
    if force_refresh:
        rcache.invalidate(key)
        log.info("run_query id=%s query_type=%s — force_refresh: cache invalidated",
                 short_form, query_type)
    else:
        cached = rcache.get(key)
        if cached is not None:
            log.info("run_query id=%s query_type=%s — cache hit", short_form, query_type)
            if include_graph:
                cached = _maybe_add_graph(cached, func_name, short_form)
            return web.json_response(_page_out(cached, func_name, offset, page_size))

    # ---- Coalescing: piggyback on identical in-flight query ----
    fut, is_owner = await coalescer.get_or_create(key)
    if not is_owner:
        log.info(
            "run_query id=%s query_type=%s — coalesced", short_form, query_type
        )
        try:
            result = await fut
            if include_graph:
                result = _maybe_add_graph(result, func_name, short_form)
            return web.json_response(_page_out(result, func_name, offset, page_size))
        except Overloaded as exc:
            return _overloaded_response(exc)
        except Exception as exc:
            return _failure_response(
                f"Query failed for id={short_form} query_type={query_type}", exc,
                f"run_query id={short_form} query_type={query_type}", coalesced=True,
            )

    # ---- Queue depth guard ----
    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            log.warning(
                "run_query id=%s query_type=%s — rejected (queue full: waiting=%d >= %d)",
                short_form, query_type, snap["waiting"], max_queue,
            )
            return await _shed(coalescer, fut, key,
                               "Server overloaded, please retry later",
                               retry_after="30")

    # ---- Enter the bounded worker queue ----
    pool = request.app["pool"]
    sem = request.app["semaphore"]

    await tracker.enter_queue()
    snap = tracker.snapshot
    log.info(
        "run_query id=%s query_type=%s — queued  (active=%d waiting=%d)",
        short_form, query_type, snap["active"], snap["waiting"],
    )
    started = False
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            started = True
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                pool, _run_query, short_form, func_name, force_refresh, offset, limit
            )
        log.info("run_query id=%s query_type=%s — done", short_form, query_type)
        # Bound/prepare for cache + coalesced sharing. AllAlignedImages caches a
        # single server page; every other query caches its FULL set so any offset
        # slice can be served (and later pages need no recompute).
        if func_name in PAGED_QUERY_FUNCS:
            cached_result = _cap_result_rows(result)
        else:
            cached_result = _prepare_full_for_cache(result)
        rcache.put(key, cached_result)
        await coalescer.remove(key)
        fut.set_result(cached_result)  # coalesced waiters slice their own page
        out = _page_out(cached_result, func_name, offset, page_size)
        if include_graph:
            out = _maybe_add_graph(out, func_name, short_form)
        return web.json_response(out)
    except Exception as exc:
        await coalescer.remove(key)
        if not fut.done():
            fut.set_exception(exc)
        return _failure_response(
            f"Query failed for id={short_form} query_type={query_type}", exc,
            f"run_query id={short_form} query_type={query_type}",
        )
    finally:
        _abandon(coalescer, fut, key)
        await tracker.finish_work(started=started)


async def handle_health(request):
    """GET /health — lightweight liveness probe for upstream nginx.

    Version field is the source of truth for "which build is serving"; v2-dev
    and Rancher operators can spot-check after a deploy without having to
    inspect Docker tags.
    """
    return web.json_response({"status": "ok", "version": VFBQUERY_VERSION})


async def handle_status(request):
    """GET /status — queue depth, cache stats, and worker utilisation."""
    tracker = request.app["tracker"]
    snap = tracker.snapshot
    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]
    # Solr cache status (best-effort): this may hit Solr briefly in order to
    # determine whether the cache is currently enabled.
    solr_cache_status = {
        "enabled": False,
        "disabled_until": None,
    }
    try:
        from vfbquery.solr_result_cache import get_solr_cache

        solr_cache = get_solr_cache()
        solr_cache_status["enabled"] = solr_cache.solr_cache_enabled
        solr_cache_status["disabled_until"] = solr_cache.solr_cache_disabled_until
    except Exception:
        pass

    return web.json_response({
        "status": "ok",
        "version": VFBQUERY_VERSION,
        "workers": request.app["max_workers"],
        "max_concurrent": request.app["max_concurrent"],
        "max_queue_depth": request.app.get("max_queue_depth"),
        "active": snap["active"],
        "waiting": snap["waiting"],
        "total_served": snap["total_served"],
        "cache_size": rcache.size,
        "cache_hits": rcache.hits,
        # Both ceilings, and the eviction count, because "cache_size sitting at
        # the cap" and "cache_size happens to be that big" look identical
        # otherwise — and a rising evicted with a flat hit rate is the signal
        # that the cache is thrashing rather than working.
        "cache_rows": rcache.rows,
        "cache_evicted": rcache.evicted,
        "cache_max_entries": CACHE_MAX_ENTRIES,
        "cache_max_rows": CACHE_MAX_ROWS,
        "coalesced_total": coalescer.coalesced_total,
        "coalesced_in_flight": coalescer.in_flight_count,
        "scanner_probes_blocked": request.app.get("_scanner_probes", {}).get("count", 0),
        "solr_cache": solr_cache_status,
        # /search runs on its own budget, so report it separately rather than
        # folding it into the Neo4j pool numbers above — a busy search is not a
        # busy worker pool and conflating them would hide both.
        "search": dict(
            request.app.get("search_stats", {}),
            concurrency=request.app.get("search_concurrency"),
            cpu_threads=request.app.get("search_cpu_threads"),
            queue_wait=request.app.get("search_queue_wait"),
        ),
    })


# ---------------------------------------------------------------------------
# FlyBase & connectivity endpoint handlers
# ---------------------------------------------------------------------------

async def _dispatch_to_pool(request, cache_key, worker_fn, *args, post_fn=None):
    """Shared dispatch logic for new endpoints — cache, coalesce, queue, run.

    If *post_fn* is given it is called on the result **after** cache
    retrieval/storage.  This keeps graph generation out of the cache
    while still letting handlers augment results cheaply.  *post_fn*
    receives the result dict and must return the (possibly modified) dict.
    When the result comes from cache, *post_fn* runs in-process (no
    worker needed) because graph builders are lightweight CPU work plus
    a single Neo4j batch lookup.
    """
    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]

    cached = rcache.get(cache_key)
    if cached is not None:
        if post_fn is not None:
            cached = post_fn(cached)
        return web.json_response(_cap_result_rows(cached))

    fut, is_owner = await coalescer.get_or_create(cache_key)
    if not is_owner:
        try:
            result = await fut
            if post_fn is not None:
                result = post_fn(result)
            return web.json_response(_cap_result_rows(result))
        except Overloaded as exc:
            return _overloaded_response(exc)
        except Exception as exc:
            return _failure_response("Query failed", exc, cache_key, coalesced=True)

    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            return await _shed(coalescer, fut, cache_key,
                               "Server overloaded, please retry later",
                               retry_after="30")

    pool = request.app["pool"]
    sem = request.app["semaphore"]
    await tracker.enter_queue()
    started = False
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            started = True
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(pool, worker_fn, *args)
        result = _cap_result_rows(result)
        rcache.put(cache_key, result)
        await coalescer.remove(cache_key)
        fut.set_result(result)
        if post_fn is not None:
            result = post_fn(result)
        return web.json_response(result)
    except Exception as exc:
        await coalescer.remove(cache_key)
        if not fut.done():
            fut.set_exception(exc)
        return _failure_response("Query failed", exc, cache_key)
    finally:
        _abandon(coalescer, fut, cache_key)
        await tracker.finish_work(started=started)


async def handle_resolve_entity(request):
    """GET /resolve_entity?query=<name_or_symbol>"""
    try:
        query = _parse_resolver_query(request.query.get("query"))
    except ValueError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    return await _dispatch_to_pool(
        request, f"resolve_entity:{query}", _run_resolve_entity, query
    )


async def handle_find_stocks(request):
    """GET /find_stocks?id=<feature_id>&collection=<optional_filter>"""
    feature_id = request.query.get("id")
    if not feature_id:
        return web.json_response({"error": "Missing required parameter: id"}, status=400)
    collection = request.query.get("collection") or None
    return await _dispatch_to_pool(
        request, f"find_stocks:{feature_id}:{collection}",
        _run_find_stocks, feature_id, collection,
    )


async def handle_resolve_combination(request):
    """GET /resolve_combination?query=<name_or_synonym>"""
    try:
        query = _parse_resolver_query(request.query.get("query"))
    except ValueError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    return await _dispatch_to_pool(
        request, f"resolve_combination:{query}", _run_resolve_combination, query
    )


async def handle_find_combo_publications(request):
    """GET /find_combo_publications?id=<FBco_ID>"""
    fbco_id = request.query.get("id")
    if not fbco_id:
        return web.json_response({"error": "Missing required parameter: id"}, status=400)
    return await _dispatch_to_pool(
        request, f"find_combo_publications:{fbco_id}",
        _run_find_combo_publications, fbco_id,
    )


async def handle_list_connectome_datasets(request):
    """GET /list_connectome_datasets"""
    return await _dispatch_to_pool(
        request, "list_connectome_datasets", _run_list_connectome_datasets,
    )


async def handle_query_connectivity(request):
    """GET /query_connectivity?upstream_type=X&downstream_type=Y&weight=5&group_by_class=false&exclude_dbs=hb,fafb&include_graph=false

    A neuron type means itself or any of its subclasses, so ``Kenyon cell``
    finds Kenyon cells even though nothing is typed directly to that class.
    ``exclude_dbs`` defaults to ``DEFAULT_EXCLUDE_DBS`` (hemibrain and CATMAID
    FAFB, both of which double-count against datasets that are kept — see that
    constant for the reasoning); pass ``exclude_dbs=`` empty for all datasets.
    """
    upstream = request.query.get("upstream_type") or None
    downstream = request.query.get("downstream_type") or None
    if upstream is None and downstream is None:
        return web.json_response(
            {"error": "At least one of upstream_type or downstream_type required"},
            status=400,
        )
    weight = int(request.query.get("weight", "5"))
    group_by_class = request.query.get("group_by_class", "false").lower() in ("true", "1", "yes")
    exclude_dbs_raw = request.query.get("exclude_dbs")
    if exclude_dbs_raw is not None:
        exclude_dbs = [s.strip() for s in exclude_dbs_raw.split(",") if s.strip()]
    else:
        from .vfb_connectivity import DEFAULT_EXCLUDE_DBS
        exclude_dbs = list(DEFAULT_EXCLUDE_DBS)
    include_graph = request.query.get("include_graph", "false").lower() in ("true", "1", "yes")
    force_refresh = request.query.get("force_refresh", "false").lower() in ("true", "1", "yes")

    post_fn = None
    if include_graph:
        def post_fn(result):
            from .graph_builder import graph_from_query_connectivity
            conns = result.get("connections") if isinstance(result, dict) else None
            if conns:
                graph = graph_from_query_connectivity(
                    conns, group_by_class, upstream, downstream,
                )
                if graph is not None:
                    result = dict(result)  # shallow copy to avoid mutating cache
                    result["graph"] = graph
            return result

    key = f"query_connectivity:{upstream}:{downstream}:{weight}:{group_by_class}:{exclude_dbs}"
    # force_refresh=true drops the in-memory L1 entry so the recomputed result
    # replaces it; the SOLR layer is invalidated inside query_connectivity.
    if force_refresh:
        request.app["result_cache"].invalidate(key)
    return await _dispatch_to_pool(
        request, key, _run_query_connectivity,
        upstream, downstream, weight, group_by_class, exclude_dbs, force_refresh,
        post_fn=post_fn,
    )


def _run_get_hierarchy(short_form, relationship, direction, max_depth):
    """Worker: run get_hierarchy in a subprocess."""
    from . import vfb_queries as _vfb
    return _convert_numpy_types(
        _vfb.get_hierarchy(short_form, relationship=relationship,
                           direction=direction, max_depth=max_depth)
    )


async def handle_get_hierarchy(request):
    """GET /get_hierarchy?id=FBbt_00005801&relationship=part_of&direction=both&max_depth=1"""
    short_form = request.query.get("id")
    if not short_form:
        return web.json_response({"error": "id parameter is required"}, status=400)
    relationship = request.query.get("relationship", "part_of")
    if relationship not in ("part_of", "subclass_of"):
        return web.json_response(
            {"error": "relationship must be 'part_of' or 'subclass_of'"}, status=400
        )
    direction = request.query.get("direction", "both")
    if direction not in ("descendants", "ancestors", "both"):
        return web.json_response(
            {"error": "direction must be 'descendants', 'ancestors', or 'both'"}, status=400
        )
    max_depth = int(request.query.get("max_depth", "1"))

    key = f"get_hierarchy:{short_form}:{relationship}:{direction}:{max_depth}"
    return await _dispatch_to_pool(
        request, key, _run_get_hierarchy,
        short_form, relationship, direction, max_depth,
    )


async def handle_get_hierarchy_html(request):
    """GET /get_hierarchy_html?id=FBbt_00005801&relationship=part_of&direction=both&max_depth=1

    Serves the hierarchy as a self-contained HTML page (Content-Type: text/html).

    This is a rendering wrapper over the same worker :func:`handle_get_hierarchy`
    uses, written for the geppetto site's ROI browser. It is intentionally not in
    ``ALLOWED_PATHS``: the markup is one consumer's presentation detail, and
    anything else wanting the tree should take the JSON.
    """
    short_form = request.query.get("id")
    if not short_form:
        return web.Response(text="Error: id parameter is required", status=400)
    relationship = request.query.get("relationship", "part_of")
    if relationship not in ("part_of", "subclass_of"):
        return web.Response(text="Error: relationship must be 'part_of' or 'subclass_of'", status=400)
    direction = request.query.get("direction", "both")
    if direction not in ("descendants", "ancestors", "both"):
        return web.Response(text="Error: direction must be 'descendants', 'ancestors', or 'both'", status=400)
    max_depth = int(request.query.get("max_depth", "1"))

    key = f"get_hierarchy:{short_form}:{relationship}:{direction}:{max_depth}"
    json_response = await _dispatch_to_pool(
        request, key, _run_get_hierarchy,
        short_form, relationship, direction, max_depth,
    )

    # Extract HTML from the JSON result
    import json as _json
    result = _json.loads(json_response.body)
    html = result.get("html", "")
    if not html:
        return web.Response(text="No hierarchy data found", status=404)
    return web.Response(text=html, content_type="text/html")


# ---------------------------------------------------------------------------
# Canonical free-text search  (GET /search)
# ---------------------------------------------------------------------------
#
# This is the single source of truth for VFB free-text search: the same query
# construction, filters, boosts, synonym expansion and ranking that
# virtualflybrain.org uses, served once here instead of being reimplemented in
# the website, the MCP server, the Python client and the circuit browser. See
# docs/search-config-comparison.md for what those copies had drifted into, and
# search_config.py for the port and its parity harness.
#
# Why this endpoint does NOT go through _dispatch_to_pool like its neighbours:
# the cost profile is the opposite way round. A search is 150 ms–1.2 s of Solr
# I/O plus 6–300 ms of pure-Python ranking, and it has no Neo4j leg at all.
# Occupying one of the (default) 10 Neo4j pool workers for a second of waiting
# on a socket would cap search at well under the ~4 searches/s a 80-person
# workshop generates, and — worse — would put every search behind whatever slow
# connectivity queries happen to be in the queue. Search is the one thing that
# has to stay responsive while the rest of the box is busy, because it is how
# people find the IDs they feed to everything else.
#
# So: the Solr round trip is awaited on the event loop over a shared keep-alive
# session, and only the ranking is offloaded — to its own small thread pool, so
# a burst of broad searches degrades search latency and nothing else. Threads
# rather than processes because the work is a few hundred ms of comparator
# bytecode over ~2000 dicts; shipping those dicts to a subprocess would cost
# more in pickling than the sort costs to run.
#
# Cache and request-coalescing are shared with every other endpoint, which is
# what actually carries workshop load: 80 people working through the same
# exercises hit the same handful of queries, so almost everything is a cache hit
# inside the 300 s TTL.

#: Bounds concurrent Solr round trips. Well above expected load — it exists to
#: stop a scripted client turning this endpoint into a Solr amplifier, not to
#: ration normal use.
DEFAULT_SEARCH_CONCURRENCY = 40

#: Threads for refine+sort. Small on purpose: the GIL means extra threads add
#: contention rather than throughput, and this only needs to keep the ranking
#: off the event loop.
DEFAULT_SEARCH_CPU_THREADS = 4

#: How long a request will wait for a concurrency slot before being shed with
#: 503. Measured: 80 simultaneous *distinct* searches (nothing cacheable, nothing
#: coalescable — 80 people each looking up their own neuron) saturate Solr at
#: ~2 s per query, so the 40 that arrive over the limit need ~2–4 s of queueing.
#: Refusing them outright, which an availability-only check does, turns a
#: recoverable 4 s into half the room seeing an error. Waiting is bounded so a
#: genuine overload — or a scripted client — still sheds rather than piling up
#: an unbounded queue of sockets.
DEFAULT_SEARCH_QUEUE_WAIT = 10.0


#: A facet name as it appears in ``facets_annotation`` — "Class", "Individual",
#: "Nervous_system", "pub". Nothing else is a legitimate value.
_FACET_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

#: Longest accepted free-text query. ``build_q`` expands every whitespace token
#: into a four-clause OR group, so an unbounded query becomes an unbounded
#: boolean query against Solr's ``maxBooleanClauses``. 300 characters is far
#: past the longest real VFB label.
MAX_QUERY_LEN = 300

#: Longest accepted id or accession. Both are short identifiers; anything
#: longer is not one.
MAX_ID_LEN = 120


def _parse_type_list(raw):
    """Comma-separated facet list -> list, or None when absent/empty.

    These values are interpolated into ``fq`` and ``bq`` clauses, so they are
    validated against a charset rather than escaped: a facet name has no
    business containing a parenthesis or a colon, and accepting one on a public
    endpoint would let a caller rewrite the filter it is supposed to be
    choosing from. Raises ``ValueError`` so the handler can answer 400.
    """
    if not raw:
        return None
    values = [v.strip() for v in raw.split(",") if v.strip()]
    for value in values:
        if not _FACET_RE.match(value):
            raise ValueError("invalid facet name: %r" % value)
    return values or None


def _rank_search_docs(docs, query, limit):
    """Refine + sort + clean. Runs in a thread; pure CPU, no I/O."""
    from . import search_config as _sc

    ranked = _sc.sort_results(_sc.refine_results(docs), query)
    total = len(ranked)
    if limit is not None:
        ranked = ranked[:limit]
    for row in ranked:
        row["label"] = _sc.clean_label(row.get("label"))
        row["original_label"] = _sc.clean_label(row.get("original_label"))
    return ranked, total


async def _solr_search_ranked(app, query, rows, limit=None, **facets):
    """Ask Solr for candidates and rank them exactly as ``/search`` does.

    Shared by ``/search`` and ``/xref`` so the reverse xref lookup searches with
    the website's own construction rather than a second copy of it that drifts.
    Returns ``(ranked, total, response_block, n_docs_fetched)``.

    The caller owns the concurrency slot: this does the Solr I/O and the CPU
    ranking, and nothing else, so the slot covers exactly the expensive part.
    """
    from . import search_config as _sc

    params = _sc.build_params(query, rows=rows, **facets)
    session = app["http"]
    # aiohttp needs repeated keys as pairs; `fq` is multi-valued.
    async with session.get(_sc.SOLR_ONTOLOGY_URL,
                           params=_sc.params_as_pairs(params)) as resp:
        resp.raise_for_status()
        # VFB's Solr answers `wt=json` with Content-Type
        # text/plain;charset=utf-8, so aiohttp's mimetype check has to be
        # switched off — `requests` never enforced it, which is why the
        # module-level client works without this.
        payload = await resp.json(content_type=None)
    response_block = payload.get("response", {})
    docs = response_block.get("docs", [])

    loop = asyncio.get_event_loop()
    ranked, total = await loop.run_in_executor(
        app["search_cpu"], _rank_search_docs, docs, query, limit
    )
    return ranked, total, response_block, len(docs)


async def handle_search(request):
    """GET /search?query=<text>&rows=500&limit=&filter_types=&exclude_types=&boost_types=&demote_types=

    Returns the website's own ranked result list:

        {"query", "rows": [...], "count", "solr_num_found", "rows_fetched"}

    Each row carries ``short_form``, the refined display ``label``
    ("synonym (label)" or "label (short_form)"), ``original_label``, ``id``,
    ``facets_annotation`` and ``unique_facets``.

    ``rows`` is how many candidates to ask Solr for and therefore affects
    *ranking*, not just page size — the comparator can only promote what was
    retrieved, and 500 is what the website uses. ``limit`` truncates the ranked
    list afterwards, so ``limit=1`` still gets the answer ranked against the
    full candidate set.
    """
    from . import search_config as _sc

    query = request.query.get("query")
    if query is None:
        query = request.query.get("q")
    if not query or not query.strip():
        return web.json_response(
            {"error": "Missing required parameter: query"}, status=400
        )
    if len(query) > MAX_QUERY_LEN:
        return web.json_response(
            {"error": "query must be at most %d characters" % MAX_QUERY_LEN},
            status=400)

    try:
        rows = int(request.query.get("rows", _sc.DEFAULT_ROWS))
    except ValueError:
        return web.json_response({"error": "rows must be an integer"}, status=400)
    rows = max(1, min(rows, _sc.MAX_ROWS))

    limit_raw = request.query.get("limit")
    limit = None
    if limit_raw:
        try:
            limit = max(0, int(limit_raw))
        except ValueError:
            return web.json_response({"error": "limit must be an integer"}, status=400)

    try:
        filter_types = _parse_type_list(request.query.get("filter_types"))
        exclude_types = _parse_type_list(request.query.get("exclude_types"))
        boost_types = _parse_type_list(request.query.get("boost_types"))
        demote_types = _parse_type_list(request.query.get("demote_types"))
    except ValueError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    cache_key = "|".join([
        "search", query, str(rows), str(limit),
        ",".join(filter_types or []), ",".join(exclude_types or []),
        ",".join(boost_types or []), ",".join(demote_types or []),
    ])

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]

    cached = rcache.get(cache_key)
    if cached is not None:
        return web.json_response(_cap_result_rows(cached))

    fut, is_owner = await coalescer.get_or_create(cache_key)
    if not is_owner:
        try:
            return web.json_response(_cap_result_rows(await fut))
        except Overloaded as exc:
            return _overloaded_response(exc)
        except Exception as exc:
            return _failure_response("Search failed", exc, cache_key, coalesced=True)

    stats = request.app["search_stats"]
    sem = request.app["search_semaphore"]

    # Queue for a slot rather than refusing the moment the limit is reached: a
    # burst of distinct queries is normal (a room full of people each looking up
    # a different neuron) and drains in a few seconds, whereas sustained
    # saturation does not — so wait, but only for a bounded time.
    if sem.locked():
        stats["queued"] += 1
    # One try from here to the end, so the _abandon backstop also covers a
    # cancellation while queued on the semaphore — that window is the ten-second
    # search_queue_wait, the longest this handler is ever parked with the key
    # registered and the future unsettled.
    try:
        try:
            await asyncio.wait_for(
                sem.acquire(), timeout=request.app["search_queue_wait"]
            )
        except asyncio.TimeoutError:
            stats["shed"] += 1
            return await _shed(coalescer, fut, cache_key,
                               "Search overloaded, please retry later")

        stats["in_flight"] += 1
        try:
            ranked, total, response_block, n_docs = await _solr_search_ranked(
                request.app, query, rows, limit,
                filter_types=filter_types, exclude_types=exclude_types,
                boost_types=boost_types, demote_types=demote_types,
            )
        finally:
            # Hold the slot for exactly the Solr call plus the ranking, then let
            # the next waiter in — the JSON serialisation below needs no slot.
            stats["in_flight"] -= 1
            sem.release()

        result = {
            "query": query,
            "rows": ranked,
            "count": total,
            "solr_num_found": response_block.get("numFound"),
            "rows_fetched": n_docs,
        }
        result = _cap_result_rows(result)
        rcache.put(cache_key, result)
        stats["served"] += 1
        await coalescer.remove(cache_key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        stats["failed"] += 1
        await coalescer.remove(cache_key)
        if not fut.done():
            fut.set_exception(exc)
        return _failure_response("Search failed", exc, cache_key)
    finally:
        _abandon(coalescer, fut, cache_key)


# ---------------------------------------------------------------------------
# /xref — VFB id <-> external database accession
# ---------------------------------------------------------------------------

#: The content store. Cross-references live *inside* the ``term_info`` JSON blob
#: on this core; neither core indexes an accession field (both schemas checked).
#: That is the whole reason the reverse lookup below is two steps rather than
#: one Solr query.
SOLR_JSON_URL = os.getenv(
    "VFBQUERY_SOLR_JSON_URL",
    "https://solr.virtualflybrain.org/solr/vfb_json/select")

#: How many ranked ``/search`` candidates the reverse lookup opens and checks.
#: Each one is confirmed against its own xref list before it is returned, so
#: this bounds cost, not correctness — raising it can only find more true
#: matches, never admit a false one.
XREF_MAX_CANDIDATES = 25


def _xref_site_names(site):
    """Every string a caller might reasonably pass as ``db`` for one site."""
    if not isinstance(site, dict):
        return []
    return [str(site.get(key) or "")
            for key in ("symbol", "short_form", "label")]


def _xref_matches_db(site, db):
    """``db`` is optional; when given it may be the symbol, short_form or label."""
    if not db:
        return True
    want = db.strip().lower()
    return any(name.lower() == want for name in _xref_site_names(site) if name)


def _parse_term_info(doc):
    """``term_info`` is a JSON string (sometimes wrapped in a list) -> dict."""
    raw = doc.get("term_info")
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        log.warning("Unparseable term_info for %s", doc.get("id"))
        return None


def _xref_rows(short_form, term_info, db=None):
    """Flatten one term's ``xrefs`` into result rows, optionally filtered by db."""
    core = (term_info.get("term") or {}).get("core") or {}
    label = core.get("label") or core.get("symbol") or ""
    rows = []
    for xref in term_info.get("xrefs") or []:
        site = xref.get("site") or {}
        if not _xref_matches_db(site, db):
            continue
        accession = str(xref.get("accession") or "")
        link = ""
        if xref.get("link_base"):
            link = "%s%s%s" % (xref["link_base"], accession,
                               xref.get("link_postfix") or "")
        rows.append({
            "id": short_form,
            "label": label,
            "db": site.get("symbol") or site.get("short_form") or "",
            "db_label": site.get("label") or "",
            "site_id": site.get("short_form") or "",
            "accession": accession,
            "is_data_source": bool(xref.get("is_data_source")),
            "link": link,
        })
    return rows


async def _fetch_term_info_docs(session, ids):
    """One Solr request for many ids -> ``{short_form: parsed term_info}``.

    Batched on purpose: the reverse lookup checks up to ``XREF_MAX_CANDIDATES``
    terms, and doing that as N round trips would make the honest confirmation
    step expensive enough to be tempting to skip.
    """
    ids = [i for i in ids if i]
    if not ids:
        return {}
    # Backslash first: escaping the quote before the backslash would leave a
    # trailing `\` escaping the *closing* quote, giving an unterminated phrase
    # and a Solr 400.
    clause = " OR ".join(
        '"%s"' % i.replace("\\", "\\\\").replace('"', '\\"') for i in ids)
    params = {"q": "id:(%s)" % clause, "defType": "lucene",
              "fl": "id,term_info", "rows": str(len(ids)), "wt": "json"}
    async with session.get(SOLR_JSON_URL, params=params) as resp:
        resp.raise_for_status()
        payload = await resp.json(content_type=None)
    out = {}
    for doc in payload.get("response", {}).get("docs", []):
        parsed = _parse_term_info(doc)
        if parsed is not None:
            out[doc.get("id")] = parsed
    return out


async def handle_xref(request):
    """GET /xref?id=<VFB id>   |   GET /xref?accession=<external id>[&db=<site>]

    Both directions of the VFB id <-> external accession mapping:

        {"query", "direction", "rows": [...], "count", "candidates_checked"}

    ``direction`` is ``id_to_accession`` or ``accession_to_id``, and
    ``candidates_checked`` is how many terms were opened and confirmed (1 in the
    forward direction, up to ``XREF_MAX_CANDIDATES`` in the reverse one).

    Each row carries ``id``, ``label``, ``db``, ``db_label``, ``site_id``,
    ``accession``, ``is_data_source`` and a resolved ``link``.

    Cross-references are not indexed as fields on either Solr core — they live
    inside the ``term_info`` JSON — so the forward direction is one document
    fetch, and the reverse direction is the canonical ``/search`` for the
    accession followed by an exact confirmation against each candidate's own
    xref list. The confirmation is the point, not a formality: free-text search
    on a bare numeric bodyId will cheerfully rank a near-miss first, which is
    exactly how the MCP came to resolve one to the wrong neuron. A row is
    returned only if that term really does carry that accession.

    ``db`` is optional and matches a site's symbol ("hb"), short_form
    ("neuprint_JRC_Hemibrain_1point2point1") or label.

    Known limit of the reverse direction: it can only confirm a term that the
    search reached, and the only reason an accession is searchable at all is
    that VFB writes it into the label ("DA1_lPN_R (FlyEM-HB:1734350908)").
    Connectome bodyIds therefore resolve; an accession that appears in no
    indexed text — a short numeric id from a site VFB only links out to — will
    return no rows. This is a property of the index, not of the query:
    ``term_info`` is ``indexed=false`` on ``vfb_json`` and neither core has an
    accession field, so there is nothing better to query. Returning empty is
    the correct answer to give until one exists; the alternative would be to
    return the best-ranked guess, which is the failure this endpoint exists to
    avoid.
    """
    from . import search_config as _sc

    term_id = (request.query.get("id") or "").strip()
    accession = (request.query.get("accession") or "").strip()
    db = (request.query.get("db") or "").strip() or None

    if bool(term_id) == bool(accession):
        return web.json_response(
            {"error": "Provide exactly one of: id (VFB id -> accessions) or "
                      "accession (external accession -> VFB id)"}, status=400)
    if max(len(term_id), len(accession), len(db or "")) > MAX_ID_LEN:
        return web.json_response(
            {"error": "id, accession and db must each be at most %d characters"
                      % MAX_ID_LEN}, status=400)

    # JSON rather than "|".join: `accession` and `db` are free text (only a
    # length cap validates them), so a bare join is not injective —
    # `?accession=A|B` and `?accession=A&db=B|` both flatten to
    # `xref||A|B|`, which is one cache entry answering two different
    # questions. /search's key gets away with the join because every
    # component there is validated to a fixed shape first; this one is not,
    # and a cache that conflates requests is a correctness bug, not a
    # performance one.
    cache_key = "xref|" + json.dumps(
        [term_id, accession, db or ""], separators=(",", ":"))

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]

    cached = rcache.get(cache_key)
    if cached is not None:
        return web.json_response(_cap_result_rows(cached))

    fut, is_owner = await coalescer.get_or_create(cache_key)
    if not is_owner:
        try:
            return web.json_response(_cap_result_rows(await fut))
        except Overloaded as exc:
            return _overloaded_response(exc)
        except Exception as exc:
            return _failure_response("Xref lookup failed", exc, cache_key,
                                     coalesced=True)

    stats = request.app["search_stats"]
    sem = request.app["search_semaphore"]

    # Same Solr concurrency budget as /search, deliberately: these are the two
    # endpoints that talk to Solr directly, so they should queue against each
    # other rather than each getting a private allowance that Solr never agreed
    # to.
    if sem.locked():
        stats["queued"] += 1
    # Single try to the end — same reason as /search: the wait for a slot is the
    # long window where the key is registered and the future is not yet settled.
    try:
        try:
            await asyncio.wait_for(
                sem.acquire(), timeout=request.app["search_queue_wait"])
        except asyncio.TimeoutError:
            stats["shed"] += 1
            return await _shed(coalescer, fut, cache_key,
                               "Search overloaded, please retry later")

        stats["in_flight"] += 1
        try:
            session = request.app["http"]
            if term_id:
                infos = await _fetch_term_info_docs(session, [term_id])
                rows = []
                for short_form, info in infos.items():
                    rows.extend(_xref_rows(short_form, info, db))
                candidates = list(infos)
            else:
                # No `limit`: the sorter ranks the whole candidate set either
                # way, so truncating before de-duplication would only make
                # XREF_MAX_CANDIDATES mean an unpredictable number of *terms*.
                ranked, _total, _block, _n = await _solr_search_ranked(
                    request.app, accession, _sc.DEFAULT_ROWS)
                # One term can occupy several ranked rows — refine_results
                # explodes a term into one row per matching synonym for
                # display. De-duplicate (order-preserving) or the same term is
                # fetched, confirmed and returned once per synonym.
                candidates = list(dict.fromkeys(
                    r.get("short_form") for r in ranked
                    if r.get("short_form")))[:XREF_MAX_CANDIDATES]
                infos = await _fetch_term_info_docs(session, candidates)
                want = accession.lower()
                rows = []
                for short_form in candidates:   # keep the search's rank order
                    info = infos.get(short_form)
                    if info is None:
                        continue
                    rows.extend(row for row in _xref_rows(short_form, info, db)
                                if row["accession"].lower() == want)
        finally:
            stats["in_flight"] -= 1
            sem.release()

        result = {
            "query": term_id or accession,
            "direction": "id_to_accession" if term_id else "accession_to_id",
            "rows": rows,
            "count": len(rows),
            "candidates_checked": len(candidates),
        }
        result = _cap_result_rows(result)
        rcache.put(cache_key, result)
        stats["served"] += 1
        await coalescer.remove(cache_key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        stats["failed"] += 1
        await coalescer.remove(cache_key)
        if not fut.done():
            fut.set_exception(exc)
        return _failure_response("Xref lookup failed", exc, cache_key)
    finally:
        _abandon(coalescer, fut, cache_key)


# ---------------------------------------------------------------------------
# /combine — set algebra over the results of several queries
#
# The endpoint is thin on purpose. Everything that can be decided without the
# network — parsing, precedence, bracketing, the set algebra, the explanations,
# the lossless column merge — lives in `vfbquery.combine`, which imports nothing
# but the standard library and can therefore be unit-tested at full speed and
# reused by the client to explain an expression before it is sent. What is left
# here is the part that genuinely needs the server: turning each named operand
# into rows, under the same cache, coalescer and backpressure as every other
# endpoint.
# ---------------------------------------------------------------------------

#: How many operands one expression may name. Not a parser limit — the parser is
#: happy with any number — but a cost limit: every operand is a separate query
#: against Neo4j or Solr, issued concurrently, and one request that fans out to
#: fifty is a denial of service against the other seventy-nine people using the
#: service. Twelve is well past any expression a human writes by hand (the
#: documented use cases top out at four) while still leaving room for a client
#: that generates them.
MAX_COMBINE_OPERANDS = _int_env("VFBQUERY_MAX_COMBINE_OPERANDS", 12)

#: Longest accepted expression. Guards the tokeniser against a megabyte of
#: brackets; 2000 characters is roughly 150 operators.
MAX_COMBINE_EXPR_LEN = 2000


def _parse_operand_spec(name, raw):
    """Turn one ``name=<spec>`` parameter into a dict describing what to run.

    Three forms, distinguished by their prefix:

        a=NeuronsPartHere:FBbt_00007401   run a query — any /run_query type
        a=search:kenyon cell              run a free-text /search
        a=ids:VFB_00000001,VFB_00000002   a literal set, no query at all

    The lowercase prefixes cannot collide with a query type: every key of
    QUERY_TYPE_MAP is CamelCase, and the query-type branch is tried first
    regardless, so a query type called `search` would still win.

    `ids:` exists because it is the only way to bring an outside set into the
    algebra — a list from a paper's supplementary table, a hand-curated set of
    neurons, or the ids of a previous /combine result — and because it makes the
    endpoint testable without a network.
    """
    raw = (raw or "").strip()
    if not raw:
        raise combine.CombineError(
            f"Operand '{name}' has no query. Give it one, e.g. "
            f"{name}=NeuronsPartHere:FBbt_00007401")

    head, sep, rest = raw.partition(":")
    head, rest = head.strip(), rest.strip()
    if not sep:
        raise combine.CombineError(
            f"Operand '{name}' = {raw!r} is not a query. Expected "
            "'<QueryType>:<id>' (e.g. NeuronsPartHere:FBbt_00007401), "
            "'search:<text>' or 'ids:<id>,<id>'.")

    if head in QUERY_TYPE_MAP:
        if not rest and QUERY_TYPE_MAP[head] != "get_all_datasets":
            raise combine.CombineError(
                f"Operand '{name}' = {raw!r} names the query type but no term. "
                f"Expected {head}:<id>.")
        if len(rest) > MAX_ID_LEN:
            raise combine.CombineError(
                f"Operand '{name}': id is longer than {MAX_ID_LEN} characters.")
        return {"kind": "query", "query_type": head, "id": rest,
                "label": f"{head} of {rest}" if rest else head, "raw": raw}

    if head == "search":
        if not rest:
            raise combine.CombineError(
                f"Operand '{name}': search needs some text, e.g. "
                f"{name}=search:kenyon cell")
        if len(rest) > MAX_QUERY_LEN:
            raise combine.CombineError(
                f"Operand '{name}': search text is longer than "
                f"{MAX_QUERY_LEN} characters.")
        return {"kind": "search", "query": rest,
                "label": f"search for {rest!r}", "raw": raw}

    if head == "ids":
        ids = [token.strip() for token in rest.replace(";", ",").split(",")]
        ids = [token for token in ids if token]
        if not ids:
            raise combine.CombineError(
                f"Operand '{name}': ids needs at least one id, e.g. "
                f"{name}=ids:VFB_00000001,VFB_00000002")
        return {"kind": "ids", "ids": ids,
                "label": f"a list of {len(ids)} ids", "raw": raw}

    raise combine.CombineError(
        f"Operand '{name}': unknown query type {head!r}. Use one of the "
        f"/run_query types, 'search:' or 'ids:'. Available query types: "
        f"{', '.join(sorted(QUERY_TYPE_MAP))}")


#: Headers synthesised for the operand kinds that do not come from a query
#: function. `type: selection_id` is the contract `combine.id_column` reads, so
#: declaring it here is what lets a search result or a pasted id list combine on
#: the same axis as a query table instead of falling through to a guess.
_SEARCH_HEADERS = {
    "short_form": {"title": "Add to search", "type": "selection_id", "order": 0},
    "label": {"title": "Name", "type": "markdown", "order": 1},
}
_IDS_HEADERS = {
    "id": {"title": "Add to search", "type": "selection_id", "order": 0},
}


async def _run_query_payload(request, short_form, query_type):
    """Run one /run_query and return its payload dict rather than a Response.

    Deliberately keyed exactly as `handle_run_query` keys it, so an operand and
    a direct call to /run_query for the same thing share one cache entry and one
    in-flight computation. At a workshop where forty people run the same
    documented example that is the difference between forty Neo4j queries and
    one.
    """
    func_name = QUERY_TYPE_MAP[query_type]
    if func_name == "get_all_datasets":
        key = "run_query::AllDatasets"
    else:
        key = f"run_query:{short_form}:{query_type}"
    # Paged functions key on their window. Combine always wants the whole
    # answer, which is offset=0/limit=0 — the same window a bare /run_query
    # asks for, so the cache is still shared.
    if func_name in PAGED_QUERY_FUNCS:
        key = f"{key}:0:0"

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]

    cached = rcache.get(key)
    if cached is not None:
        return cached

    fut, is_owner = await coalescer.get_or_create(key)
    if not is_owner:
        return await fut

    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            # Raise rather than return a Response: the caller is holding N of
            # these in an asyncio.gather and needs one place to turn any of them
            # into the 503. _shed settles the coalescer future for the waiters.
            await _shed(coalescer, fut, key,
                        "Server overloaded, please retry later", retry_after="30")
            raise Overloaded("Server overloaded, please retry later", "30")

    pool = request.app["pool"]
    sem = request.app["semaphore"]
    await tracker.enter_queue()
    started = False
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            started = True
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                pool, _run_query, short_form, func_name, False, 0, 0)
        if func_name in PAGED_QUERY_FUNCS:
            result = _cap_result_rows(result)
        else:
            result = _prepare_full_for_cache(result)
        rcache.put(key, result)
        await coalescer.remove(key)
        fut.set_result(result)
        return result
    except Exception as exc:
        await coalescer.remove(key)
        if not fut.done():
            fut.set_exception(exc)
        raise
    finally:
        _abandon(coalescer, fut, key)
        await tracker.finish_work(started=started)


async def _search_payload(request, text):
    """Run one /search and shape it as a combinable table."""
    from . import search_config as _sc

    key = "|".join(["search", text, str(_sc.DEFAULT_ROWS), "None", "", "", "", ""])
    rcache = request.app["result_cache"]
    cached = rcache.get(key)
    if cached is not None:
        return dict(cached, headers=_SEARCH_HEADERS)

    stats = request.app["search_stats"]
    sem = request.app["search_semaphore"]
    if sem.locked():
        stats["queued"] += 1
    try:
        await asyncio.wait_for(sem.acquire(),
                               timeout=request.app["search_queue_wait"])
    except asyncio.TimeoutError:
        stats["shed"] += 1
        raise Overloaded("Search overloaded, please retry later")
    stats["in_flight"] += 1
    try:
        ranked, total, block, n_docs = await _solr_search_ranked(
            request.app, text, _sc.DEFAULT_ROWS)
    finally:
        stats["in_flight"] -= 1
        sem.release()

    result = _cap_result_rows({
        "query": text, "rows": ranked, "count": total,
        "solr_num_found": block.get("numFound"), "rows_fetched": n_docs,
    })
    rcache.put(key, result)
    stats["served"] += 1
    return dict(result, headers=_SEARCH_HEADERS)


async def _fetch_operand(request, name, spec):
    """Resolve one operand spec to an `OperandResult`."""
    if spec["kind"] == "ids":
        payload = {"headers": _IDS_HEADERS,
                   "rows": [{"id": i} for i in spec["ids"]],
                   "count": len(spec["ids"])}
    elif spec["kind"] == "search":
        payload = await _search_payload(request, spec["query"])
    else:
        payload = await _run_query_payload(request, spec["id"],
                                           spec["query_type"])
    try:
        return combine.OperandResult(name, payload, spec=spec["raw"],
                                     description=spec["label"])
    except combine.CombineError as exc:
        # Re-raised with the operand named. Without this the user is told that
        # "a result" has no identifiable term column while looking at an
        # expression with four of them.
        raise combine.CombineError(
            f"Operand '{name}' ({spec['raw']}) cannot take part in a "
            f"combination: {exc}") from exc


#: Query-string keys `/combine` consumes itself; everything else is an operand
#: name. Spelling the reserved set out is what lets operands be named freely
#: (`calyx`, `lh`, `pn`) instead of forcing a `op1=`/`op2=` convention that makes
#: an expression unreadable.
#:
#: Three of these — `offset`, `order_by`, `force_refresh` — are **reserved but
#: not implemented**: the endpoint ignores them today. That is deliberate and is
#: the cheaper half of a decision made once. Adding paging or caller-chosen
#: ordering later is a small change; discovering then that somebody's saved
#: expression names an operand `offset` — and that honouring the new parameter
#: silently changes what their expression means — is not. Reserving the name now
#: costs a user the inconvenience of picking a different operand name; reserving
#: it later costs them a wrong answer. Either implement one of these or leave it
#: here; do not quietly free it.
_COMBINE_RESERVED = frozenset({
    "expr", "expression", "q", "universe", "limit", "offset",
    "require_complete", "explain_only", "order_by", "force_refresh",
})


class _StubOperand:
    """Just enough of an OperandResult for `explain_only` to describe a query it
    has deliberately not run."""

    def __init__(self, name, description):
        self.name = name
        self.description = description


async def handle_combine(request):
    """GET /combine?expr=<expression>&<name>=<query>&...

    Set algebra over the rows of two or more queries, compared on each row's
    term id.

        /combine?expr=calyx AND lh
                &calyx=NeuronsPartHere:FBbt_00007401
                &lh=NeuronsPartHere:FBbt_00007053

    Operators: OR AND NOT XOR NAND NOR XNOR, plus unary NOT, plus brackets, plus
    plain-English aliases ("but not", "in both", "either but not both") and
    symbols (| & - ^). Precedence, loosest first: OR/NOR, XOR/XNOR, AND/NAND/NOT
    — all left-associative. The response echoes the grouping actually used, so a
    user can check it rather than assume it.

    The answer carries its own explanation: a step-by-step trace with the size
    of every intermediate set, a one-sentence plain-English reading of the whole
    expression, and warnings for the three ways a combination is silently wrong
    (a truncated operand, two sides in different id namespaces, and a complement
    against an implicit universe).
    """
    query_params = request.query

    expr = query_params.get("expr") or query_params.get("expression") \
        or query_params.get("q")
    if not expr or not expr.strip():
        return web.json_response({
            "error": "Missing required parameter: expr",
            "example": ("/combine?expr=a AND b"
                        "&a=NeuronsPartHere:FBbt_00007401"
                        "&b=NeuronsPartHere:FBbt_00007053"),
        }, status=400)
    if len(expr) > MAX_COMBINE_EXPR_LEN:
        return web.json_response(
            {"error": f"expr must be at most {MAX_COMBINE_EXPR_LEN} characters"},
            status=400)

    # ---- operand specs ----
    specs = {}
    try:
        for name in query_params:
            if name in _COMBINE_RESERVED:
                continue
            specs[name] = _parse_operand_spec(name, query_params[name])
    except combine.CombineError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    if not specs:
        return web.json_response({
            "error": "No operands given. Every name in the expression needs a "
                     "query of its own, e.g. &a=NeuronsPartHere:FBbt_00007401",
        }, status=400)
    if len(specs) > MAX_COMBINE_OPERANDS:
        return web.json_response({
            "error": f"Too many operands ({len(specs)}); at most "
                     f"{MAX_COMBINE_OPERANDS} per expression. Each one is a "
                     "separate query, so this is a limit on how much work one "
                     "request may ask for. Combine in stages: run part of the "
                     "expression, then feed its ids back in with 'ids:'.",
        }, status=400)

    # ---- parse ----
    try:
        tree = combine.parse(expr, known_names=set(specs))
    except combine.CombineError as exc:
        return web.json_response({"error": str(exc), "expression": expr},
                                 status=400)

    used = sorted(set(tree.names()))
    unused = sorted(set(specs) - set(used))

    universe_spec = None
    if query_params.get("universe"):
        try:
            universe_spec = _parse_operand_spec("universe",
                                                query_params["universe"])
        except combine.CombineError as exc:
            return web.json_response({"error": str(exc)}, status=400)

    # ---- explain without running anything ----
    # The whole point of the explanation is that a user can check the reading
    # *before* paying for the queries; explain_only makes that a request of its
    # own so a client can offer "what will this do?" as a button.
    if query_params.get("explain_only", "").lower() in ("true", "1", "yes"):
        return web.json_response({
            "expression": expr,
            "as_read": combine.to_expression(tree),
            "plain_english": combine.plain_english(
                tree, {n: _StubOperand(n, specs[n]["label"]) for n in used}),
            "operands": {n: specs[n]["raw"] for n in used},
            "unused_operands": unused,
            "universe_note": combine.UNIVERSE_NOTE,
        })

    try:
        limit = int(query_params.get("limit", 0) or 0)
    except ValueError:
        return web.json_response({"error": "limit must be an integer"},
                                 status=400)
    require_complete = query_params.get("require_complete", "").lower() in (
        "true", "1", "yes")

    # ---- run the operands ----
    # Concurrently: they are independent, and the alternative is that a
    # four-operand expression takes four times as long as the slowest one for no
    # reason. The pool semaphore and the queue-depth guard still bound the work.
    jobs = [(name, specs[name]) for name in used]
    if universe_spec is not None:
        jobs.append(("universe", universe_spec))
    try:
        fetched = await asyncio.gather(
            *[_fetch_operand(request, name, spec) for name, spec in jobs])
    except Overloaded as exc:
        return _overloaded_response(exc)
    except combine.CombineError as exc:
        return web.json_response({"error": str(exc)}, status=400)
    except Exception as exc:
        return _failure_response("Combine failed while running its queries",
                                 exc, f"combine {expr!r}")

    operands = {name: result for (name, _spec), result in zip(jobs, fetched)}
    universe_operand = operands.pop("universe", None)

    warnings = []
    for name in used:
        operand = operands[name]
        if not operand.by_id:
            warnings.append(
                f"'{name}' ({operand.description}) returned nothing. Anything "
                "AND-ed with it is empty and anything NOT-ed by it is "
                "unchanged, so check this query on its own before reading the "
                "combination as a biological result.")
        if operand.truncated:
            message = (
                f"'{name}' ({operand.description}) was cut short: it has "
                f"{operand.reported_count} results but only "
                f"{operand.rows_returned} were returned. Any combination using "
                "it is unreliable — an AND can silently lose members and a NOT "
                "can silently keep them. Narrow the query, or re-run with "
                "require_complete=true to make this an error instead of a "
                "warning.")
            if require_complete:
                return web.json_response(
                    {"error": message, "operand": name}, status=409)
            warnings.append(message)
        if operand.rows_without_id:
            warnings.append(
                f"'{name}': {operand.rows_without_id} row(s) had no value in "
                f"the '{operand.id_column}' column and were left out of the "
                "comparison.")

    if universe_operand is not None:
        universe = combine.Universe(
            universe_operand.ids, "explicit",
            f"the {len(universe_operand.ids)} terms returned by "
            f"{universe_spec['label']}")
        operands["universe"] = universe_operand   # so its columns survive
    else:
        universe = combine.implicit_universe(
            {n: operands[n] for n in used})

    steps = []
    try:
        result_ids = combine.evaluate(tree, operands, universe, steps, warnings)
    except combine.CombineError as exc:
        return web.json_response({"error": str(exc)}, status=400)

    # Column order follows the expression, so the left-hand query's columns come
    # first — which is what someone reading `calyx AND lh` expects to see.
    order = list(used) + (["universe"] if universe_operand is not None else [])
    rows = combine.build_rows(result_ids, operands, order)
    headers = combine.merge_headers(operands, order, rows)
    total = len(rows)
    if limit and limit > 0:
        rows = rows[:limit]

    if not result_ids and not warnings:
        warnings.append(
            "The combination is empty. That can be a real biological result, "
            "but check the step counts below first: if one side is 0 the query "
            "itself found nothing, and if both sides are large but the overlap "
            "is 0 the two queries are probably returning different kinds of "
            "thing (classes vs individual images, say) that can never match.")

    result = {
        "expression": expr,
        "as_read": combine.to_expression(tree),
        "plain_english": combine.plain_english(tree, operands),
        "steps": steps,
        "headers": headers,
        "rows": rows,
        "count": total,
        "operands": {
            name: {
                "query": specs[name]["raw"],
                "description": operands[name].description,
                "id_column": operands[name].id_column,
                "rows_returned": operands[name].rows_returned,
                "distinct_terms": len(operands[name].by_id),
                "reported_count": operands[name].reported_count,
                "truncated": operands[name].truncated,
            } for name in used
        },
        "universe": {
            "source": universe.source,
            "size": len(universe.ids),
            "description": universe.description,
            "note": combine.UNIVERSE_NOTE,
        },
    }
    if unused:
        result["unused_operands"] = unused
        warnings.append(
            "Defined but never used in the expression: "
            f"{', '.join(unused)}. They were not run.")
    if limit and limit > 0 and total > limit:
        result["limit"] = limit
        result["capped"] = True
    if warnings:
        result["warnings"] = warnings
    return web.json_response(_cap_result_rows(result))


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(max_workers=None, max_concurrent=None, max_queue_depth=None,
               cache_ttl=None, search_concurrency=None, search_cpu_threads=None,
               search_queue_wait=None):
    """
    Build the aiohttp Application.

    Args:
        max_workers:     number of OS processes in the pool  (default: 10)
        max_concurrent:  max queries executing at once       (default: workers × 2)
        max_queue_depth: reject with 503 when waiting queue  (default: 200)
                         exceeds this depth (0 = unlimited)
        cache_ttl:       result cache TTL in seconds         (default: 300)
        search_concurrency:  concurrent /search Solr calls   (default: 40)
        search_cpu_threads:  threads ranking /search results (default: 4)
        search_queue_wait:   seconds a /search waits for a   (default: 10)
                             slot before 503
    """
    if search_queue_wait is None:
        search_queue_wait = float(os.getenv("VFBQUERY_SEARCH_QUEUE_WAIT",
                                            DEFAULT_SEARCH_QUEUE_WAIT))
    if search_concurrency is None:
        search_concurrency = int(os.getenv("VFBQUERY_SEARCH_CONCURRENCY",
                                           DEFAULT_SEARCH_CONCURRENCY))
    if search_cpu_threads is None:
        search_cpu_threads = int(os.getenv("VFBQUERY_SEARCH_CPU_THREADS",
                                           DEFAULT_SEARCH_CPU_THREADS))
    if max_workers is None:
        max_workers = int(os.getenv("VFBQUERY_WORKERS", DEFAULT_WORKERS))
    if max_concurrent is None:
        max_concurrent = int(os.getenv("VFBQUERY_MAX_CONCURRENT", max_workers * 2))
    if max_queue_depth is None:
        max_queue_depth = int(os.getenv("VFBQUERY_MAX_QUEUE_DEPTH", DEFAULT_MAX_QUEUE_DEPTH))
    if cache_ttl is None:
        cache_ttl = int(os.getenv("VFBQUERY_CACHE_TTL", "300"))

    app = web.Application(middlewares=[security_middleware])

    # Routes
    app.router.add_get("/get_term_info", handle_get_term_info)
    app.router.add_get("/run_query", handle_run_query)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/status", handle_status)

    # FlyBase & connectivity endpoints
    app.router.add_get("/resolve_entity", handle_resolve_entity)
    app.router.add_get("/find_stocks", handle_find_stocks)
    app.router.add_get("/resolve_combination", handle_resolve_combination)
    app.router.add_get("/find_combo_publications", handle_find_combo_publications)
    app.router.add_get("/list_connectome_datasets", handle_list_connectome_datasets)
    app.router.add_get("/query_connectivity", handle_query_connectivity)
    app.router.add_get("/get_hierarchy", handle_get_hierarchy)
    app.router.add_get("/get_hierarchy_html", handle_get_hierarchy_html)

    # Canonical free-text search (website-equivalent ranking)
    app.router.add_get("/search", handle_search)
    app.router.add_get("/xref", handle_xref)

    # Set algebra over query results
    app.router.add_get("/combine", handle_combine)

    _warn_unreachable_routes(app)

    # Store config for /status and handlers
    app["max_workers"] = max_workers
    app["max_concurrent"] = max_concurrent
    app["max_queue_depth"] = max_queue_depth or None  # 0 means unlimited
    app["search_concurrency"] = search_concurrency
    app["search_cpu_threads"] = search_cpu_threads
    app["search_queue_wait"] = search_queue_wait

    async def _cache_cleanup_loop(app):
        """Periodically evict expired result-cache entries."""
        cache = app["result_cache"]
        try:
            while True:
                await asyncio.sleep(60)
                n = cache.evict_expired()
                if n:
                    log.debug("Evicted %d expired result-cache entries", n)
        except asyncio.CancelledError:
            pass

    async def on_startup(app):
        log.info(
            "Starting process pool: %d workers, %d max concurrent queries, "
            "max queue depth: %s, cache TTL: %ds",
            max_workers, max_concurrent,
            max_queue_depth or "unlimited", cache_ttl,
        )
        app["pool"] = ProcessPoolExecutor(
            max_workers=max_workers, initializer=_init_worker
        )
        app["semaphore"] = asyncio.Semaphore(max_concurrent)
        app["tracker"] = QueueTracker()
        app["result_cache"] = ResultCache(ttl_seconds=cache_ttl)
        app["coalescer"] = RequestCoalescer()
        # /search resources — deliberately separate from the Neo4j pool so that
        # search latency is independent of connectivity-query load.
        app["search_semaphore"] = asyncio.Semaphore(search_concurrency)
        app["search_cpu"] = ThreadPoolExecutor(
            max_workers=search_cpu_threads, thread_name_prefix="search-rank"
        )
        app["http"] = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(limit=search_concurrency),
        )
        app["search_stats"] = {
            "in_flight": 0, "queued": 0, "served": 0, "shed": 0, "failed": 0,
        }
        # Avoid setting attributes after startup (aiohttp deprecation warning)
        app["_scanner_probes"] = {"count": 0}
        app["_cache_cleanup_task"] = asyncio.ensure_future(_cache_cleanup_loop(app))

    async def on_cleanup(app):
        # Every lookup is `.get()`, because aiohttp runs on_cleanup even when
        # on_startup raised part-way through — and the keys above are set in
        # order, so a failure at, say, the ClientSession leaves "http" and
        # everything after it absent. Indexing would then raise KeyError from
        # the cleanup handler, and that KeyError is what the operator sees in
        # the logs instead of the startup exception that actually caused the
        # shutdown. Guarding here costs a few `if`s and keeps the real cause on
        # top.
        task = app.get("_cache_cleanup_task")
        if task is not None:
            task.cancel()
            # The loop suppresses CancelledError and returns, so awaiting it
            # normally completes — except when cancellation lands before the
            # coroutine ever ran a step (a startup failure immediately after
            # ensure_future), where the task ends up genuinely cancelled and
            # the await re-raises. Suppress it: we asked for the cancellation.
            try:
                await task
            except asyncio.CancelledError:
                pass
        session = app.get("http")
        if session is not None:
            await session.close()
        for key in ("search_cpu", "pool"):
            executor = app.get(key)
            if executor is not None:
                executor.shutdown(wait=False)
        log.info("Process pool shut down")

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    return app


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="VFBquery HA API server")
    parser.add_argument(
        "--port", type=int,
        default=int(os.getenv("VFBQUERY_PORT", "8080")),
        help="Port to listen on (default: 8080)",
    )
    parser.add_argument(
        "--host", type=str,
        default=os.getenv("VFBQUERY_HOST", "0.0.0.0"),
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--workers", type=int,
        default=int(os.getenv("VFBQUERY_WORKERS", DEFAULT_WORKERS)),
        help=f"Number of worker processes (default: {DEFAULT_WORKERS})",
    )
    parser.add_argument(
        "--max-concurrent", type=int,
        default=None,
        help="Max concurrent queries (default: workers × 2)",
    )
    parser.add_argument(
        "--max-queue-depth", type=int,
        default=None,
        help=f"Reject requests with 503 when queue exceeds this depth (default: {DEFAULT_MAX_QUEUE_DEPTH}, 0=unlimited)",
    )
    parser.add_argument(
        "--cache-ttl", type=int,
        default=None,
        help="Result cache TTL in seconds (default: 300)",
    )
    parser.add_argument(
        "--search-concurrency", type=int,
        default=None,
        help=f"Max concurrent /search Solr calls (default: {DEFAULT_SEARCH_CONCURRENCY})",
    )
    parser.add_argument(
        "--search-cpu-threads", type=int,
        default=None,
        help=f"Threads ranking /search results (default: {DEFAULT_SEARCH_CPU_THREADS})",
    )
    parser.add_argument(
        "--search-queue-wait", type=float,
        default=None,
        help=f"Seconds a /search waits for a slot before 503 (default: {DEFAULT_SEARCH_QUEUE_WAIT})",
    )
    args = parser.parse_args()

    app = create_app(
        max_workers=args.workers,
        max_concurrent=args.max_concurrent,
        max_queue_depth=args.max_queue_depth,
        cache_ttl=args.cache_ttl,
        search_concurrency=args.search_concurrency,
        search_cpu_threads=args.search_cpu_threads,
        search_queue_wait=args.search_queue_wait,
    )

    log.info("VFBquery HA API v%s starting on %s:%d", VFBQUERY_VERSION, args.host, args.port)
    web.run_app(
        app,
        host=args.host,
        port=args.port,
        # No TCP-level timeout — queries can run for up to an hour.
        # The upstream nginx cache controls client-facing timeouts.
        keepalive_timeout=75,
    )


if __name__ == "__main__":
    main()
