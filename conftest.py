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
import json
import os
import re
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


_URL_RE = re.compile(r"https?://[^\s'\"<>)\]]+")


def _failure_url(exc):
    """Best-effort URL of the call behind a transport failure.

    Walks the exception chain looking for the attributes ``requests`` (and
    friends) hang the request on, then falls back to the first URL printed in
    any message in the chain. Returns None when nothing URL-shaped is found —
    the report then still carries the exception text.
    """
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        for attr in ("request", "response"):
            url = getattr(getattr(exc, attr, None), "url", None)
            if url:
                return str(url)
        match = _URL_RE.search(str(exc))
        if match:
            return match.group(0).rstrip(".,;:")
        exc = exc.__cause__ or exc.__context__
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Turn a transport-level failure into a skip (never an empty result), and
    arm the mid-run circuit breaker on a connection failure or a timeout."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when in ("setup", "call") and rep.failed and call.excinfo is not None:
        exc = call.excinfo.value
        if _is_connection_failure(exc):
            url = _failure_url(exc)
            suffix = f" (call: {url})" if url else ""
            rep.outcome = "skipped"
            rep.longrepr = (
                str(item.fspath),
                item.location[1] or 0,
                f"VFB backend unreachable: {type(exc).__name__}: {exc}{suffix}",
            )
            _mark_outage()
            _record_event("trigger", test=item.nodeid, kind="connection-failure",
                          error=f"{type(exc).__name__}: {str(exc)[:300]}",
                          url=url)
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
                    "confirms the backend is down"
                    + _probe_failure_suffix(),
                )
                _record_event("trigger", test=item.nodeid, kind="timeout",
                              error=str(exc)[:300], url=None)


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

#: Shared event log for the outage report — same run-keyed scheme as the
#: latch, JSON-lines so xdist workers can append concurrently. The session
#: master aggregates it into outage_report.md/.json at session end.
_OUTAGE_EVENTS = _OUTAGE_LATCH + "_events.jsonl"

#: Where the aggregated report lands (the invocation directory, so CI steps
#: can pick it up next to pytest_output.log).
OUTAGE_REPORT_MD = "outage_report.md"
OUTAGE_REPORT_JSON = "outage_report.json"


def _record_event(event, **fields):
    """Append one outage event; never let reporting break the run."""
    fields.update(event=event, time=time.time(),
                  worker=os.environ.get("PYTEST_XDIST_WORKER", "master"))
    try:
        with open(_OUTAGE_EVENTS, "a") as fh:
            fh.write(json.dumps(fields) + "\n")
    except OSError:
        pass

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
    # tests probe needlessly. The event log is cleared too (only here, never
    # on mid-run recovery: an outage that came and went still gets reported).
    _clear_outage()
    if not os.environ.get("PYTEST_XDIST_WORKER"):
        try:
            os.remove(_OUTAGE_EVENTS)
        except OSError:
            pass


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
    trips the breaker rather than letting those tests time out.

    Alongside the boolean, every probe's outcome (URL, status or error,
    elapsed time) is kept in ``_probe_cache["detail"]`` and recorded to the
    outage report whenever the answer is 'down' — the report is the place a
    person decides whether to debug or to ignore, and it needs to say which
    backend failed and how, not just that one did.
    """
    now = time.time()
    if now - _probe_cache["at"] < _PROBE_CACHE_S:
        return _probe_cache["down"]
    down = False
    detail = []
    for url in _PROBE_URLS:
        started = time.time()
        try:
            status = requests.get(url, timeout=_PROBE_TIMEOUT_S).status_code
            entry = {"url": url, "ok": status < 500, "status": status,
                     "elapsed_s": round(time.time() - started, 2)}
        except requests.RequestException as exc:
            entry = {"url": url, "ok": False, "status": None,
                     "error": f"{type(exc).__name__}: {str(exc)[:200]}",
                     "elapsed_s": round(time.time() - started, 2)}
        detail.append(entry)
        if not entry["ok"]:
            down = True
            break
    _probe_cache.update(at=now, down=down, detail=detail)
    if down:
        _record_event("probe", probes=detail)
    return down


def _probe_failure_suffix():
    """One-line ' (probe: <url> -> <how it failed>)' for skip messages, from
    the most recent probe round; empty when no failing probe is on record."""
    for entry in _probe_cache.get("detail") or []:
        if not entry.get("ok"):
            how = entry.get("error") or f"HTTP {entry.get('status')}"
            return " (probe: %s -> %s after %ss)" % (
                entry["url"], how, entry.get("elapsed_s"))
    return ""


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
            _record_event("skip", test=item.nodeid)
            pytest.skip("VFB backend outage detected mid-run — skipping to avoid "
                        "per-test timeouts; re-run once the backend is healthy"
                        + _probe_failure_suffix())
        else:
            _clear_outage()


# --------------------------------------------------------------------------
# Outage report — aggregate the events into something a person can act on
# --------------------------------------------------------------------------

def _md_link(url):
    return "[%s](%s)" % (url, url)


def build_outage_report(events):
    """(markdown, summary_line) from the recorded events.

    The markdown is what the CI steps embed in the job summary and the
    sticky PR comment, so URLs are rendered as links: the point of the
    report is that the person reading it can click the failing call,
    see how it failed, and decide between debugging and ignoring.
    """
    triggers, skips, probes = [], [], []
    seen_triggers, seen_skips = set(), set()
    for event in events:
        if event.get("event") == "trigger" and event.get("test") not in seen_triggers:
            seen_triggers.add(event.get("test"))
            triggers.append(event)
        elif event.get("event") == "skip" and event.get("test") not in seen_skips:
            seen_skips.add(event.get("test"))
            skips.append(event)
        elif event.get("event") == "probe":
            probes.append(event)

    summary = ("%d test(s) hit the backend directly and failed; %d more were "
               "fast-skipped by the circuit breaker"
               % (len(triggers), len(skips)))

    lines = ["## VFB backend outage report", "",
             summary + ". Details below decide between debugging and "
             "re-running: a transport error against a known-good URL is an "
             "outage (re-run later); anything else deserves a look.", ""]

    if triggers:
        lines += ["### What failed first", ""]
        for event in sorted(triggers, key=lambda e: e.get("time", 0)):
            call = (" — call: " + _md_link(event["url"])) if event.get("url") else ""
            lines.append("- `%s` (%s): %s%s"
                         % (event.get("test"), event.get("kind"),
                            event.get("error", "").replace("\n", " "), call))
        lines.append("")

    if probes:
        lines += ["### Health probes at detection", ""]
        # The latest round is the decisive one; earlier rounds add nothing.
        for entry in probes[-1].get("probes", []):
            if entry.get("ok"):
                lines.append("- OK — %s (HTTP %s in %ss)"
                             % (_md_link(entry["url"]), entry.get("status"),
                                entry.get("elapsed_s")))
            else:
                how = entry.get("error") or ("HTTP %s" % entry.get("status"))
                lines.append("- **FAILED** — %s: %s after %ss"
                             % (_md_link(entry["url"]), how,
                                entry.get("elapsed_s")))
        lines.append("")

    if skips:
        names = sorted(event.get("test", "") for event in skips)
        lines += ["### Tests fast-skipped by the circuit breaker (%d)" % len(names),
                  "", "<details><summary>Full list</summary>", ""]
        lines += ["- `%s`" % name for name in names]
        lines += ["", "</details>", ""]

    return "\n".join(lines), summary


def pytest_sessionfinish(session, exitstatus):
    """On the session master, turn the shared event log into
    ``outage_report.md`` / ``outage_report.json`` beside the invocation
    directory's pytest output, for the CI skip report to embed."""
    if os.environ.get("PYTEST_XDIST_WORKER"):
        return                               # workers report; the master writes
    events = []
    try:
        with open(_OUTAGE_EVENTS) as fh:
            for line in fh:
                try:
                    events.append(json.loads(line))
                except ValueError:
                    continue
    except OSError:
        return                               # no outage this run — no report
    if not events:
        return
    outdir = str(session.config.invocation_params.dir)
    markdown, summary = build_outage_report(events)
    try:
        with open(os.path.join(outdir, OUTAGE_REPORT_MD), "w") as fh:
            fh.write(markdown)
        with open(os.path.join(outdir, OUTAGE_REPORT_JSON), "w") as fh:
            json.dump(events, fh, indent=1)
        print("\nVFB backend outage detected this run: %s.\n"
              "Report written to %s (markdown) and %s (raw events)."
              % (summary, OUTAGE_REPORT_MD, OUTAGE_REPORT_JSON))
    except OSError:
        pass
