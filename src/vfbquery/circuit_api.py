"""Circuit mode: a small server that holds the circuit graphs and serves
``/circuit_paths`` (#114).

Run with ``python -m vfbquery.ha_api --mode circuit`` (or
``VFBQUERY_MODE=circuit``). It is the same image as the main API, deployed
separately so that loading the graphs, or a memory problem, cannot affect the
other endpoints.

Where the graphs come from (one of):

* ``VFBQUERY_CIRCUIT_DIR``: a fixed run folder (the one holding
  ``manifest.json``), e.g. ``pipeline-out/<run>/circuit`` on p3;
* ``VFBQUERY_CIRCUIT_ROOT``: a folder with a ``CURRENT`` file naming the run
  folder to serve, e.g. ``pipeline-out/circuit``. CURRENT is polled every
  ``VFBQUERY_CIRCUIT_POLL`` seconds (default 60); a new run is loaded in the
  background and swapped in only once it has loaded.

Until the first run has loaded, ``/health`` and ``/circuit_paths`` return 503.
If a later run fails to load, the last good one keeps being served and
``/status`` reports the error. Every response names the run it came from.

Searches run in ``VFBQUERY_CIRCUIT_WORKERS`` processes (default 2), forked
after the graphs are loaded so they share the parent's memory. ``0`` runs
searches in threads in the server process (for tests and local use).
"""
import asyncio
import gc
import logging
import multiprocessing
import os
import time
from concurrent.futures import ProcessPoolExecutor

from aiohttp import web

from . import vfb_circuit as vc
from .ha_api import (BadParam, ResultCache, _flag_warning, _query_flag, _query_float,
                     _query_int, _resolve_exclude_dbs, _unknown_param_warnings,
                     security_middleware)
from .vfb_connectivity import DEFAULT_EXCLUDE_DBS

log = logging.getLogger("vfbquery.circuit")

#: Loaded runs by name. Module-level so that forked worker processes inherit
#: them; a worker looks its run up by the name sent with each task.
_STORES = {}

CIRCUIT_PARAMS = frozenset({
    "source", "target", "k", "min_synapses", "min_inprop", "normalise",
    "exclude_dbs", "instance_graph", "instance_k",
})

#: How long to wait before retrying a run that failed to load.
RETRY_FAILED = 600


def _search(run, kwargs):
    """Worker entry point: search the named run."""
    return vc.find_paths(_STORES[run], **kwargs)


def _ping():
    return os.getpid()


def _keep_only(run):
    """Worker initialiser: drop every run but ``run``.

    A worker is forked while the server still holds the run it is replacing;
    without this the new workers keep the old run's graphs in memory until the
    next swap, so each pod would carry two runs.
    """
    for name in [n for n in _STORES if n != run]:
        del _STORES[name]
    gc.collect()


class CircuitState:
    """The run being served, its worker pool, and what is happening to them."""

    def __init__(self, fixed_dir=None, root=None, workers=2, poll=60):
        if bool(fixed_dir) == bool(root):
            raise ValueError("give exactly one of VFBQUERY_CIRCUIT_DIR or VFBQUERY_CIRCUIT_ROOT")
        self.fixed_dir, self.root = fixed_dir, root
        self.workers, self.poll = workers, poll
        self.store = None
        self.pool = None
        self.loaded_at = None
        self.loading = None            # folder being loaded
        self.last_error = None
        self.failed = {}               # folder -> time of failure

    def source(self):
        return ({"dir": self.fixed_dir} if self.fixed_dir
                else {"root": self.root, "current": os.path.join(self.root, "CURRENT")})

    def wanted(self):
        """The folder that should be served now."""
        return self.fixed_dir or vc.resolve_current(self.root)

    async def refresh(self):
        """Load the wanted run if it differs from the one being served."""
        try:
            folder = os.path.realpath(self.wanted())
        except (OSError, vc.CircuitDataError) as exc:
            self.last_error = f"{type(exc).__name__}: {exc}"
            return
        if self.store is not None and os.path.realpath(self.store.folder) == folder:
            return
        failed = self.failed.get(folder)
        if failed and time.time() - failed < RETRY_FAILED:
            return
        self.loading = folder
        loop = asyncio.get_running_loop()
        try:
            store = await loop.run_in_executor(None, lambda: vc.load_run(folder, log=log.info))
        except Exception as exc:                          # noqa: BLE001 - keep serving
            self.failed[folder] = time.time()
            self.last_error = f"{folder}: {type(exc).__name__}: {exc}"
            log.error("circuit: failed to load %s: %s", folder, exc)
            return
        finally:
            self.loading = None
        await self._swap(store)

    async def _swap(self, store):
        old_store, old_pool = self.store, self.pool
        _STORES[store.run] = store
        pool = None
        if self.workers > 0:
            # Fork, so the workers share the loaded graphs copy-on-write. gc.freeze()
            # first: the workers inherit the frozen state, so their garbage collector
            # never walks (and so never copies) the graphs' pages. The server unfreezes
            # straight after, so the run it later drops can still be collected.
            gc.collect()
            gc.freeze()
            try:
                pool = ProcessPoolExecutor(self.workers,
                                           mp_context=multiprocessing.get_context("fork"),
                                           initializer=_keep_only, initargs=(store.run,))
                loop = asyncio.get_running_loop()
                await asyncio.gather(*(loop.run_in_executor(pool, _ping)
                                       for _ in range(self.workers)))
            finally:
                gc.unfreeze()
        self.store, self.pool = store, pool
        self.loaded_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.last_error = None
        log.info("circuit: serving run %s from %s (%d datasets, loaded in %.0fs)",
                 store.run, store.folder, len(store.datasets), store.load_seconds)
        if old_pool is not None:
            await asyncio.get_running_loop().run_in_executor(None, old_pool.shutdown, True)
        if old_store is not None and old_store.run != store.run:
            _STORES.pop(old_store.run, None)

    async def search(self, kwargs):
        store, pool = self.store, self.pool
        loop = asyncio.get_running_loop()
        if pool is None:
            return await loop.run_in_executor(None, lambda: vc.find_paths(store, **kwargs))
        return await loop.run_in_executor(pool, _search, store.run, kwargs)

    def close(self):
        if self.pool is not None:
            self.pool.shutdown(wait=False)


def _terms(request, name):
    raw = request.query.get(name) or ""
    return [t.strip() for t in raw.split(",") if t.strip()]


def _unavailable(state):
    body = {"error": "Circuit graphs are not loaded yet." if state.loading or not state.last_error
            else "Circuit graphs could not be loaded.",
            "loading": state.loading, "detail": state.last_error}
    return web.json_response(body, status=503, headers={"Retry-After": "30"})


async def handle_circuit_paths(request):
    """GET /circuit_paths?source=FBbt_00100484&target=FBbt_00004020&k=5

    ``source`` and ``target`` are comma-separated FBbt class ids or VFB neuron
    ids. ``exclude_dbs`` works as on /query_connectivity (default: hemibrain
    and CATMAID FAFB). See :mod:`vfbquery.vfb_circuit` for the scoring.
    """
    state = request.app["circuit"]
    if state.store is None:
        return _unavailable(state)
    sources, targets = _terms(request, "source"), _terms(request, "target")
    if not sources or not targets:
        return web.json_response({"error": "source and target are both required "
                                           "(comma-separated FBbt class or VFB neuron ids)"},
                                 status=400)
    try:
        kwargs = {
            "k": _query_int(request, "k", vc.DEFAULT_K, 1, vc.MAX_K),
            "min_synapses": _query_int(request, "min_synapses", vc.DEFAULT_MIN_SYNAPSES, 0),
            "min_inprop": _query_float(request, "min_inprop", 0.0, 0.0, 1.0),
            "normalise": (request.query.get("normalise") or "input").strip().lower(),
            "instance_graph": _query_flag(request, "instance_graph"),
            "instance_k": _query_int(request, "instance_k", vc.DEFAULT_INSTANCE_K,
                                     1, vc.MAX_INSTANCE_K),
        }
        if kwargs["normalise"] not in vc.NORMALISE:
            raise BadParam("normalise must be one of: " + ", ".join(vc.NORMALISE))
        store = state.store
        sites = store.sites()
        raw = request.query.get("exclude_dbs")
        if raw is None:
            # Defaults exclude whichever of them this run has; only names the
            # caller typed are checked against the run's datasets.
            resolved = list(DEFAULT_EXCLUDE_DBS)
        else:
            resolved, _ = _resolve_exclude_dbs(
                [s.strip() for s in raw.split(",") if s.strip()], sites)
    except BadParam as exc:
        return web.json_response({"error": str(exc)}, status=400)
    exclude = {s["short_form"] for s in sites
               if s["symbol"] in resolved or s["short_form"] in resolved}

    warnings = _unknown_param_warnings(request, CIRCUIT_PARAMS)
    warn = _flag_warning(request, "instance_graph")
    if warn:
        warnings.append(warn)

    key = (f"circuit:{store.run}:{','.join(sources)}:{','.join(targets)}:"
           f"{sorted(exclude)}:{sorted(kwargs.items())}")
    cache = request.app["result_cache"]
    result = cache.get(key)
    if result is None:
        result = await state.search(dict(kwargs, sources=sources, targets=targets,
                                         exclude=exclude))
        cache.put(key, result)
    if warnings:
        result = dict(result, warnings=list(result.get("warnings") or []) + warnings)
    return web.json_response(result)


async def handle_circuit_terms(request):
    """GET /circuit_paths/terms: every FBbt class with neurons in some dataset of
    the run being served, so a client can tell which classes /circuit_paths can
    find before asking (a class with none is reported as not found)."""
    state = request.app["circuit"]
    if state.store is None:
        return _unavailable(state)
    store = state.store
    resp = web.json_response({"run": store.run, "built": store.built,
                              "count": len(store.terms()), "terms": store.terms()},
                             headers={"Cache-Control": "public, max-age=300"})
    resp.enable_compression()
    return resp


async def handle_health(request):
    state = request.app["circuit"]
    if state.store is None:
        return _unavailable(state)
    return web.json_response({"status": "ok", "run": state.store.run})


async def handle_status(request):
    state = request.app["circuit"]
    return web.json_response({
        "mode": "circuit",
        "source": state.source(),
        "serving": state.store.summary() if state.store else None,
        "loaded_at": state.loaded_at,
        "loading": state.loading,
        "last_error": state.last_error,
        "workers": state.workers,
        "cache_entries": request.app["result_cache"].size,
    })


async def handle_index(request):
    return web.json_response({"mode": "circuit",
                              "endpoints": ["/circuit_paths", "/circuit_paths/terms",
                                            "/health", "/status"]})


def create_circuit_app(fixed_dir=None, root=None, workers=None, poll=None, cache_ttl=None):
    """Build the circuit-mode aiohttp app (settings default to the env vars)."""
    fixed_dir = fixed_dir or os.getenv("VFBQUERY_CIRCUIT_DIR") or None
    root = root or os.getenv("VFBQUERY_CIRCUIT_ROOT") or None
    workers = int(os.getenv("VFBQUERY_CIRCUIT_WORKERS", "2")) if workers is None else workers
    poll = float(os.getenv("VFBQUERY_CIRCUIT_POLL", "60")) if poll is None else poll
    cache_ttl = int(os.getenv("VFBQUERY_CACHE_TTL", "300")) if cache_ttl is None else cache_ttl
    state = CircuitState(fixed_dir, root, workers, poll)

    app = web.Application(middlewares=[security_middleware])
    app.router.add_get("/", handle_index)
    app.router.add_get("/circuit_paths", handle_circuit_paths)
    app.router.add_get("/circuit_paths/terms", handle_circuit_terms)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/status", handle_status)
    app["circuit"] = state

    async def watch(app):
        try:
            while True:
                await state.refresh()
                if state.fixed_dir and state.store is not None:
                    return                      # a fixed folder never changes
                await asyncio.sleep(state.poll)
        except asyncio.CancelledError:
            pass

    async def on_startup(app):
        app["result_cache"] = ResultCache(ttl_seconds=cache_ttl)
        app["_scanner_probes"] = {"count": 0}
        app["circuit_watch"] = asyncio.ensure_future(watch(app))

    async def on_cleanup(app):
        task = app.get("circuit_watch")
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        state.close()

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    return app
