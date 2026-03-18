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
    GET /health
    GET /status          — queue depth, cache stats & worker utilisation

Usage:
    python -m vfbquery.ha_api                    # default: port 8080, 10 workers
    python -m vfbquery.ha_api --port 8080 --workers 8
    VFBQUERY_WORKERS=10 python -m vfbquery.ha_api
"""

import argparse
import json
import logging
import os
import sys
import asyncio
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from functools import partial

from aiohttp import web
import numpy as np

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


# ---------------------------------------------------------------------------
# Result cache — short-lived L1 cache in the event-loop process so that
# recently-computed results are returned without dispatching a worker.
# ---------------------------------------------------------------------------

class ResultCache:
    """In-memory LRU-ish cache with TTL.  Runs in the single-threaded
    event loop so no locks are needed."""

    def __init__(self, ttl_seconds: int = 300):
        self._store: dict = {}          # key -> (result, monotonic_ts)
        self._ttl = ttl_seconds
        self._hits = 0

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        result, ts = entry
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None
        self._hits += 1
        return result

    def put(self, key: str, result):
        self._store[key] = (result, time.monotonic())

    def evict_expired(self):
        now = time.monotonic()
        expired = [k for k, (_, ts) in self._store.items() if now - ts > self._ttl]
        for k in expired:
            del self._store[k]
        return len(expired)

    @property
    def size(self):
        return len(self._store)

    @property
    def hits(self):
        return self._hits


# ---------------------------------------------------------------------------
# Request coalescer — deduplicates concurrent identical queries so that
# only one worker executes each unique (endpoint, id, query_type).
# ---------------------------------------------------------------------------

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

    async def finish_work(self):
        async with self._lock:
            self._active -= 1
            self._total_served += 1

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
})


@web.middleware
async def security_middleware(request, handler):
    """Reject requests to unknown paths with a minimal 404."""
    if request.path not in ALLOWED_PATHS:
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

    # Neurons in region
    "NeuronsPartHere":              "get_neurons_with_part_in",
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
    "ExpressionOverlapsHere":        "get_expression_overlaps_here",
    "TransgeneExpressionHere":       "get_transgene_expression_here",

    # Transcriptomics
    "anatScRNAseqQuery":             "get_anatomy_scrnaseq",
    "clusterExpression":             "get_cluster_expression",
    "expressionCluster":             "get_expression_cluster",
    "scRNAdatasetData":              "get_scrnaseq_dataset_data",

    # Templates / datasets
    "PaintedDomains":                "get_painted_domains",
    "DatasetImages":                 "get_dataset_images",
    "AllAlignedImages":              "get_all_aligned_images",
    "AlignedDatasets":               "get_aligned_datasets",
    "AllDatasets":                   "get_all_datasets",

    # Publications
    "TermsForPub":                   "get_terms_for_pub",
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


def _run_term_info(short_form):
    """Execute get_term_info in a worker process. Returns JSON-serialisable dict."""
    result = _vfb.get_term_info(short_form)
    return _convert_numpy_types(result)


def _run_query(short_form, func_name):
    """Execute a named query function in a worker process. Returns JSON-serialisable dict."""
    fn = getattr(_vfb, func_name)
    # AllDatasets is the only query that takes no id argument
    if func_name == "get_all_datasets":
        result = fn(return_dataframe=False)
    else:
        result = fn(short_form, return_dataframe=False)

    # Convert numpy types to Python types for JSON serialization
    return _convert_numpy_types(result)


def _run_resolve_entity(name_or_id):
    """Execute resolve_entity in a worker process."""
    return _vfb.resolve_entity(name_or_id)


def _run_find_stocks(feature_id, collection_filter):
    """Execute find_stocks in a worker process."""
    return _vfb.find_stocks(feature_id, collection_filter=collection_filter)


def _run_resolve_combination(name_or_id):
    """Execute resolve_combination in a worker process."""
    return _vfb.resolve_combination(name_or_id)


def _run_find_combo_publications(fbco_id):
    """Execute find_combo_publications in a worker process."""
    return _vfb.find_combo_publications(fbco_id)


def _run_list_connectome_datasets():
    """Execute list_connectome_datasets in a worker process."""
    return _vfb.list_connectome_datasets()


def _run_query_connectivity(upstream_type, downstream_type, weight,
                            group_by_class, exclude_dbs):
    """Execute query_connectivity in a worker process."""
    return _vfb.query_connectivity(
        upstream_type=upstream_type,
        downstream_type=downstream_type,
        weight=weight,
        group_by_class=group_by_class,
        exclude_dbs=exclude_dbs,
    )


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

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]
    key = f"term_info:{short_form}"

    # ---- L1: in-memory result cache ----
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
        except Exception:
            tb = traceback.format_exc()
            return web.json_response(
                {"error": f"Query failed for id={short_form}", "detail": tb},
                status=500,
            )

    # ---- Queue depth guard ----
    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            await coalescer.remove(key)
            log.warning(
                "get_term_info id=%s — rejected (queue full: waiting=%d >= %d)",
                short_form, snap["waiting"], max_queue,
            )
            return web.json_response(
                {"error": "Server overloaded, please retry later"},
                status=503,
                headers={"Retry-After": "30"},
            )

    # ---- Enter the bounded worker queue ----
    pool = request.app["pool"]
    sem = request.app["semaphore"]

    await tracker.enter_queue()
    snap = tracker.snapshot
    log.info(
        "get_term_info id=%s — queued  (active=%d waiting=%d)",
        short_form, snap["active"], snap["waiting"],
    )
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(pool, _run_term_info, short_form)
        log.info("get_term_info id=%s — done", short_form)
        rcache.put(key, result)
        await coalescer.remove(key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        tb = traceback.format_exc()
        log.error("get_term_info id=%s — FAILED\n%s", short_form, tb)
        await coalescer.remove(key)
        if not fut.done():
            fut.set_exception(exc)
        return web.json_response(
            {"error": f"Query failed for id={short_form}", "detail": tb},
            status=500,
        )
    finally:
        await tracker.finish_work()


async def handle_run_query(request):
    """GET /run_query?id=<short_form>&query_type=<QueryType>"""
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

    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]
    # Normalize key — AllDatasets ignores the id parameter
    if func_name == "get_all_datasets":
        key = "run_query::AllDatasets"
    else:
        key = f"run_query:{short_form}:{query_type}"

    # ---- L1: in-memory result cache ----
    cached = rcache.get(key)
    if cached is not None:
        log.info("run_query id=%s query_type=%s — cache hit", short_form, query_type)
        return web.json_response(cached)

    # ---- Coalescing: piggyback on identical in-flight query ----
    fut, is_owner = await coalescer.get_or_create(key)
    if not is_owner:
        log.info(
            "run_query id=%s query_type=%s — coalesced", short_form, query_type
        )
        try:
            result = await fut
            return web.json_response(result)
        except Exception:
            tb = traceback.format_exc()
            return web.json_response(
                {"error": f"Query failed for id={short_form} query_type={query_type}",
                 "detail": tb},
                status=500,
            )

    # ---- Queue depth guard ----
    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            await coalescer.remove(key)
            log.warning(
                "run_query id=%s query_type=%s — rejected (queue full: waiting=%d >= %d)",
                short_form, query_type, snap["waiting"], max_queue,
            )
            return web.json_response(
                {"error": "Server overloaded, please retry later"},
                status=503,
                headers={"Retry-After": "30"},
            )

    # ---- Enter the bounded worker queue ----
    pool = request.app["pool"]
    sem = request.app["semaphore"]

    await tracker.enter_queue()
    snap = tracker.snapshot
    log.info(
        "run_query id=%s query_type=%s — queued  (active=%d waiting=%d)",
        short_form, query_type, snap["active"], snap["waiting"],
    )
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                pool, _run_query, short_form, func_name
            )
        log.info("run_query id=%s query_type=%s — done", short_form, query_type)
        rcache.put(key, result)
        await coalescer.remove(key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        tb = traceback.format_exc()
        log.error(
            "run_query id=%s query_type=%s — FAILED\n%s",
            short_form, query_type, tb,
        )
        await coalescer.remove(key)
        if not fut.done():
            fut.set_exception(exc)
        return web.json_response(
            {"error": f"Query failed for id={short_form} query_type={query_type}",
             "detail": tb},
            status=500,
        )
    finally:
        await tracker.finish_work()


async def handle_health(request):
    """GET /health — lightweight liveness probe for upstream nginx."""
    return web.json_response({"status": "ok"})


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
        "workers": request.app["max_workers"],
        "max_concurrent": request.app["max_concurrent"],
        "max_queue_depth": request.app.get("max_queue_depth"),
        "active": snap["active"],
        "waiting": snap["waiting"],
        "total_served": snap["total_served"],
        "cache_size": rcache.size,
        "cache_hits": rcache.hits,
        "coalesced_total": coalescer.coalesced_total,
        "coalesced_in_flight": coalescer.in_flight_count,
        "scanner_probes_blocked": request.app.get("_scanner_probes", {}).get("count", 0),
        "solr_cache": solr_cache_status,
    })


# ---------------------------------------------------------------------------
# FlyBase & connectivity endpoint handlers
# ---------------------------------------------------------------------------

async def _dispatch_to_pool(request, cache_key, worker_fn, *args):
    """Shared dispatch logic for new endpoints — cache, coalesce, queue, run."""
    rcache = request.app["result_cache"]
    coalescer = request.app["coalescer"]

    cached = rcache.get(cache_key)
    if cached is not None:
        return web.json_response(cached)

    fut, is_owner = await coalescer.get_or_create(cache_key)
    if not is_owner:
        try:
            result = await fut
            return web.json_response(result)
        except Exception:
            tb = traceback.format_exc()
            return web.json_response({"error": "Query failed", "detail": tb}, status=500)

    tracker = request.app["tracker"]
    max_queue = request.app.get("max_queue_depth")
    if max_queue:
        snap = tracker.snapshot
        if snap["waiting"] >= max_queue:
            await coalescer.remove(cache_key)
            return web.json_response(
                {"error": "Server overloaded, please retry later"},
                status=503, headers={"Retry-After": "30"},
            )

    pool = request.app["pool"]
    sem = request.app["semaphore"]
    await tracker.enter_queue()
    try:
        async with sem:
            await tracker.leave_queue_start_work()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(pool, worker_fn, *args)
        rcache.put(cache_key, result)
        await coalescer.remove(cache_key)
        fut.set_result(result)
        return web.json_response(result)
    except Exception as exc:
        tb = traceback.format_exc()
        log.error("%s — FAILED\n%s", cache_key, tb)
        await coalescer.remove(cache_key)
        if not fut.done():
            fut.set_exception(exc)
        return web.json_response({"error": "Query failed", "detail": tb}, status=500)
    finally:
        await tracker.finish_work()


async def handle_resolve_entity(request):
    """GET /resolve_entity?query=<name_or_id>"""
    query = request.query.get("query")
    if not query:
        return web.json_response({"error": "Missing required parameter: query"}, status=400)
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
    """GET /resolve_combination?query=<name_or_id>"""
    query = request.query.get("query")
    if not query:
        return web.json_response({"error": "Missing required parameter: query"}, status=400)
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
    """GET /query_connectivity?upstream_type=X&downstream_type=Y&weight=5&group_by_class=false&exclude_dbs=hb,fafb"""
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
        exclude_dbs = ["hb", "fafb"]

    key = f"query_connectivity:{upstream}:{downstream}:{weight}:{group_by_class}:{exclude_dbs}"
    return await _dispatch_to_pool(
        request, key, _run_query_connectivity,
        upstream, downstream, weight, group_by_class, exclude_dbs,
    )


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(max_workers=None, max_concurrent=None, max_queue_depth=None,
               cache_ttl=None):
    """
    Build the aiohttp Application.

    Args:
        max_workers:     number of OS processes in the pool  (default: 10)
        max_concurrent:  max queries executing at once       (default: workers × 2)
        max_queue_depth: reject with 503 when waiting queue  (default: 200)
                         exceeds this depth (0 = unlimited)
        cache_ttl:       result cache TTL in seconds         (default: 300)
    """
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

    # Store config for /status and handlers
    app["max_workers"] = max_workers
    app["max_concurrent"] = max_concurrent
    app["max_queue_depth"] = max_queue_depth or None  # 0 means unlimited

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
        # Avoid setting attributes after startup (aiohttp deprecation warning)
        app["_scanner_probes"] = {"count": 0}
        app["_cache_cleanup_task"] = asyncio.ensure_future(_cache_cleanup_loop(app))

    async def on_cleanup(app):
        app["_cache_cleanup_task"].cancel()
        await app["_cache_cleanup_task"]
        app["pool"].shutdown(wait=False)
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
    args = parser.parse_args()

    app = create_app(
        max_workers=args.workers,
        max_concurrent=args.max_concurrent,
        max_queue_depth=args.max_queue_depth,
        cache_ttl=args.cache_ttl,
    )

    log.info("VFBquery HA API starting on %s:%d", args.host, args.port)
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
