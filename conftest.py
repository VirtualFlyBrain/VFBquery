"""Root pytest configuration shared by the whole suite (``src/test`` + ``tests``).

For how to WRITE a good test (assert real content, never suppress empty
results, verify fixtures), see ``TESTING.md``. This file is the runtime
mechanics that make those rules safe on CI.

Everything here is about one thing: how the suite reacts to the live VFB
backend (SOLR / Neo4j / Owlery / FlyBase Chado) being unreachable on CI.

Policy:
  * A **connection failure SKIPS** the test rather than failing it, so a backend
    outage does not turn every PR red (``pytest_runtest_makereport`` below). The
    CI job surfaces the skip count as a ``::warning::`` annotation, so a mass
    skip is visible on the PR instead of hiding behind a green check.
  * A genuinely **empty result still FAILS** — a query that reaches the backend
    and returns no rows is a real defect, not an outage. The skip path is
    reserved for transport-level failures (can't connect / timed out), never for
    an empty-but-successful response.

The Neo4j REST client is the awkward case. ``neo4j_client.commit_list`` returns
``False`` on a connection failure (``dict_cursor`` then turns that into an empty
list) instead of raising, so a dead Neo4j looks identical to an empty result at
the call site. To keep the two apart we probe the backend once per session and
only when that probe shows Neo4j is down do we make ``commit_list`` raise on
``False`` (so it routes into the skip path). When Neo4j is up, a ``False`` means
a real server/query error and is left to fail. This shim is test-only; the
library's production behaviour is untouched.

Finally, a mid-run circuit breaker: if the backend dies PART-WAY through a run
(healthy at session start, so the shim above never armed), the remaining
backend tests would each burn their full 300s timeout. Instead, the first
connection failure / timeout sets a shared latch; subsequent tests do a short
health probe and skip fast while the backend stays down, resuming the moment it
answers again. Zero cost on a healthy run.
"""
import os
import socket
import tempfile
import time
import concurrent.futures

import pytest
import requests


# --------------------------------------------------------------------------
# Connection-failure detection
# --------------------------------------------------------------------------

# Exception type *names* (matched by name so optional deps needn't be imported)
# that always mean "couldn't reach / talk to the backend".
_CONNECTION_TYPE_NAMES = frozenset({
    "ConnectionError", "ConnectionResetError", "ConnectionRefusedError",
    "ConnectionAbortedError", "TimeoutError", "ConnectTimeout",
    "ConnectTimeoutError", "ReadTimeout", "ReadTimeoutError", "MaxRetryError",
    "NewConnectionError", "ProtocolError", "ServiceUnavailable",
    "SessionExpired", "OperationalError",
})

# Substrings that mark a transport failure even when the concrete exception is a
# generic wrapper (pysolr.SolrError, RuntimeError, …). Deliberately narrow:
# gateway 502/503/504 and socket phrases only — NOT bare "500" / "server error",
# which can be a genuine query bug that must stay a failure.
_CONNECTION_MESSAGE_MARKERS = (
    "failed to establish a new connection", "max retries exceeded",
    "connection refused", "connection reset", "connection aborted",
    "connection timed out", "read timed out", "name or service not known",
    "temporary failure in name resolution", "no route to host",
    "network is unreachable", "neo4j unreachable",
    "502 bad gateway", "503 service unavailable", "504 gateway",
)


def _is_connection_failure(exc):
    """True if ``exc`` (or a cause/context in its chain) is a transport failure."""
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, (socket.timeout, socket.gaierror,
                            concurrent.futures.TimeoutError)):
            return True
        if type(exc).__name__ in _CONNECTION_TYPE_NAMES:
            return True
        if any(m in str(exc).lower() for m in _CONNECTION_MESSAGE_MARKERS):
            return True
        exc = exc.__cause__ or exc.__context__
    return False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Turn a transport-level failure into a skip (never an empty result), and
    arm the mid-run circuit breaker on a connection failure or a timeout."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when in ("setup", "call") and rep.failed and call.excinfo is not None:
        exc = call.excinfo.value
        if _is_connection_failure(exc):
            rep.outcome = "skipped"
            rep.longrepr = (
                str(item.fspath),
                item.location[1] or 0,
                f"VFB backend unreachable: {type(exc).__name__}: {exc}",
            )
            _mark_outage()
        elif "pytest-timeout" in str(exc):
            # A test hit the per-test ceiling. If the backend is down this is an
            # outage casualty, not a slow query — record it and let it read as a
            # skip; otherwise it's a genuine hang/perf failure, left untouched.
            #
            # A single instantaneous probe is not enough here: a heavy query
            # (term-info fan-out) hangs the moment the backend degrades, but the
            # lightweight HTTP health endpoints keep answering for up to ~a
            # minute after — so the first in-flight tests to hit the 300s ceiling
            # would see a "healthy" ping and be left as failures while every
            # later test correctly skipped. Poll for a short window so the lagging
            # transport symptom is caught and the canary tests skip too.
            _mark_outage()
            if _backend_down_confirm():
                rep.outcome = "skipped"
                rep.longrepr = (
                    str(item.fspath),
                    item.location[1] or 0,
                    "VFB backend outage: test timed out and a health probe "
                    "confirms the backend is down",
                )


# --------------------------------------------------------------------------
# One-shot Neo4j probe + False->raise shim (see module docstring)
# --------------------------------------------------------------------------

def _neo4j_is_down():
    try:
        from vfbquery import vfb_queries as vq
        return not vq.vc.nc.commit_list(["RETURN 1 AS ok"])
    except Exception as exc:  # a raising client on a dead host also means down
        return _is_connection_failure(exc) or True


@pytest.fixture(scope="session", autouse=True)
def _neo4j_connection_shim():
    """Only when Neo4j is unreachable, make ``commit_list`` raise on its
    ``False`` connection-failure return so the skip hook catches it. No-op when
    Neo4j is up — a ``False`` then is a real error and must still fail. Only
    tests that actually call ``commit_list`` are affected, so pure/offline tests
    are untouched."""
    if not _neo4j_is_down():
        yield
        return
    from vfbquery import vfb_queries as vq
    nc = vq.vc.nc
    original = nc.commit_list

    def _raising_commit_list(*args, **kwargs):
        result = original(*args, **kwargs)
        if result is False:
            raise ConnectionError("Neo4j unreachable (commit_list returned False)")
        return result

    nc.commit_list = _raising_commit_list
    try:
        yield
    finally:
        nc.commit_list = original


# --------------------------------------------------------------------------
# Mid-run outage circuit breaker (see module docstring)
# --------------------------------------------------------------------------

# Shared across xdist workers via a file — each worker is a separate process, so
# in-memory state would not be seen by the others. Keyed on the run so parallel
# invocations don't collide.
_OUTAGE_LATCH = os.path.join(
    tempfile.gettempdir(),
    "vfbquery_outage_" + os.environ.get("PYTEST_XDIST_TESTRUNUID", str(os.getppid())),
)
_OUTAGE_RECENT_S = 60      # a failure newer than this means "trouble right now"
_PROBE_CACHE_S = 10        # re-probe at most this often, per worker
_PROBE_TIMEOUT_S = 5

# Cheap health endpoints. Any HTTP answer — even Owlery's 404 on the base path —
# means the host is reachable; a 5xx or a transport error means it is not.
_PROBE_URLS = (
    "http://solr.virtualflybrain.org/solr/vfb_json/admin/ping",
    "http://pdb.virtualflybrain.org/",
    "http://owl.virtualflybrain.org/kbs/vfb/",
)
_probe_cache = {"at": 0.0, "down": False}


def pytest_sessionstart(session):
    # Start every run with a clean latch — the latch path can be reused across
    # runs launched from the same shell, and a stale one would make the first
    # tests probe needlessly.
    _clear_outage()


def _mark_outage():
    try:
        with open(_OUTAGE_LATCH, "w") as fh:
            fh.write(repr(time.time()))
    except OSError:
        pass


def _outage_signalled_recently():
    try:
        with open(_OUTAGE_LATCH) as fh:
            return (time.time() - float(fh.read().strip())) < _OUTAGE_RECENT_S
    except (OSError, ValueError):
        return False


def _clear_outage():
    try:
        os.remove(_OUTAGE_LATCH)
    except OSError:
        pass


def _backend_down():
    """Short, per-worker-cached health probe. True if any VFB backend is
    unreachable or returning 5xx. Errs toward 'down' so a partial outage still
    trips the breaker rather than letting those tests time out."""
    now = time.time()
    if now - _probe_cache["at"] < _PROBE_CACHE_S:
        return _probe_cache["down"]
    down = False
    for url in _PROBE_URLS:
        try:
            if requests.get(url, timeout=_PROBE_TIMEOUT_S).status_code >= 500:
                down = True
                break
        except requests.RequestException:
            down = True
            break
    _probe_cache.update(at=now, down=down)
    return down


# How long, and how often, to keep re-probing after a pytest-timeout before
# concluding the backend is genuinely healthy (so the hang was a real code
# defect, not an outage). Sized to cover the observed lag between a heavy query
# hanging and the HTTP health endpoints degrading (~40-70s in run 32834691217).
_CONFIRM_WINDOW_S = 90
_CONFIRM_INTERVAL_S = 5


def _backend_down_confirm():
    """Stronger version of :func:`_backend_down` used only after a pytest
    timeout. An outage's transport symptoms can lag a heavy query's hang by up
    to a minute, so poll the health endpoints for a short window and report
    down as soon as any probe fails; only conclude 'healthy' (a real hang, kept
    as a failure) after the whole window stays up."""
    deadline = time.time() + _CONFIRM_WINDOW_S
    while True:
        _probe_cache["at"] = 0.0  # bypass the 10s cache — we want a fresh read
        if _backend_down():
            return True
        if time.time() >= deadline:
            return False
        time.sleep(_CONFIRM_INTERVAL_S)


def pytest_runtest_setup(item):
    """Fast-skip a test when a backend outage was signalled recently AND a fresh
    probe confirms the backend is still down — rather than letting it burn the
    full per-test timeout. Clears the latch and resumes once the backend answers
    again, so a transient blip only pauses the suite briefly."""
    if _outage_signalled_recently():
        if _backend_down():
            pytest.skip("VFB backend outage detected mid-run — skipping to avoid "
                        "per-test timeouts; re-run once the backend is healthy")
        else:
            _clear_outage()
