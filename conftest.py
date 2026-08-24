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
"""
import socket
import concurrent.futures

import pytest


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
    """Turn a transport-level failure into a skip (never an empty result)."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when in ("setup", "call") and rep.failed and call.excinfo is not None:
        if _is_connection_failure(call.excinfo.value):
            rep.outcome = "skipped"
            rep.longrepr = (
                str(item.fspath),
                item.location[1] or 0,
                f"VFB backend unreachable: "
                f"{type(call.excinfo.value).__name__}: {call.excinfo.value}",
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
