"""
VFBquery High-Availability API Server

Drop-in replacement for the V3 backend that serves VFBquery results
over HTTP. Uses a bounded process pool (default: 10 workers) so that
Neo4j is never hit by more than N simultaneous connections. Incoming
requests that exceed the pool size are queued and held open until a
worker becomes available.

Endpoints (mirrors v3-cached.virtualflybrain.org):
    GET /get_term_info?id=<short_form>
    GET /run_query?id=<short_form>&query_type=<QueryType>
    GET /health
    GET /status          — queue depth & worker utilisation

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

    pool = request.app["pool"]
    sem = request.app["semaphore"]
    tracker = request.app["tracker"]

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
        return web.json_response(result)
    except Exception:
        tb = traceback.format_exc()
        log.error("get_term_info id=%s — FAILED\n%s", short_form, tb)
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

    pool = request.app["pool"]
    sem = request.app["semaphore"]
    tracker = request.app["tracker"]

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
        return web.json_response(result)
    except Exception:
        tb = traceback.format_exc()
        log.error(
            "run_query id=%s query_type=%s — FAILED\n%s",
            short_form, query_type, tb,
        )
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
    """GET /status — queue depth and worker utilisation."""
    tracker = request.app["tracker"]
    snap = tracker.snapshot
    max_workers = request.app["max_workers"]
    max_concurrent = request.app["max_concurrent"]
    return web.json_response({
        "status": "ok",
        "workers": max_workers,
        "max_concurrent": max_concurrent,
        "active": snap["active"],
        "waiting": snap["waiting"],
        "total_served": snap["total_served"],
    })


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(max_workers=None, max_concurrent=None):
    """
    Build the aiohttp Application.

    Args:
        max_workers:   number of OS processes in the pool  (default: 10)
        max_concurrent: max queries executing at once       (default: workers × 2)

    Requests beyond max_concurrent are queued in the async event loop
    and held open until a worker becomes available — no request is
    dropped or timed out by the queue itself.
    """
    if max_workers is None:
        max_workers = int(os.getenv("VFBQUERY_WORKERS", DEFAULT_WORKERS))
    if max_concurrent is None:
        max_concurrent = int(os.getenv("VFBQUERY_MAX_CONCURRENT", max_workers * 2))

    app = web.Application()

    # Routes
    app.router.add_get("/get_term_info", handle_get_term_info)
    app.router.add_get("/run_query", handle_run_query)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/status", handle_status)

    # Store config for /status
    app["max_workers"] = max_workers
    app["max_concurrent"] = max_concurrent

    async def on_startup(app):
        log.info(
            "Starting process pool: %d workers, %d max concurrent queries",
            max_workers, max_concurrent,
        )
        app["pool"] = ProcessPoolExecutor(
            max_workers=max_workers, initializer=_init_worker
        )
        app["semaphore"] = asyncio.Semaphore(max_concurrent)
        app["tracker"] = QueueTracker()

    async def on_cleanup(app):
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
    args = parser.parse_args()

    app = create_app(
        max_workers=args.workers,
        max_concurrent=args.max_concurrent,
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
