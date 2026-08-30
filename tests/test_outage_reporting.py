"""The outage report the root conftest builds when the circuit breaker trips.

The report exists so a person reading "N tests skipped" can decide between
debugging and ignoring: it must name the tests, carry the URL of the call
that failed or timed out (as a clickable link), and say how it failed.
These tests pin that contract without needing an outage.
"""

import importlib.util
import json
import os

import pytest
import requests


def _load_root_conftest():
    path = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "conftest.py")
    spec = importlib.util.spec_from_file_location("vfb_root_conftest", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def guard(tmp_path, monkeypatch):
    module = _load_root_conftest()
    monkeypatch.setattr(module, "_OUTAGE_EVENTS",
                        str(tmp_path / "events.jsonl"))
    monkeypatch.setattr(module, "_OUTAGE_LATCH", str(tmp_path / "latch"))
    module._probe_cache.update(at=0.0, down=False, detail=None)
    return module


# ---------------------------------------------------------------------------
# Finding the URL behind a failure
# ---------------------------------------------------------------------------

def test_failure_url_from_requests_exception(guard):
    request = requests.Request(
        "GET", "https://pdb.virtualflybrain.org/db/neo4j/tx/commit").prepare()
    exc = requests.ConnectionError("boom", request=request)
    assert guard._failure_url(exc) == (
        "https://pdb.virtualflybrain.org/db/neo4j/tx/commit")


def test_failure_url_from_message_text(guard):
    exc = RuntimeError(
        "Solr responded with an error (HTTP 503): "
        "http://solr.virtualflybrain.org/solr/vfb_json/select?q=x timed out.")
    assert guard._failure_url(exc) == (
        "http://solr.virtualflybrain.org/solr/vfb_json/select?q=x")


def test_failure_url_walks_the_exception_chain(guard):
    inner = RuntimeError("connect to http://owl.virtualflybrain.org/kbs/vfb/ failed")
    outer = ConnectionError("wrapped")
    outer.__cause__ = inner
    assert guard._failure_url(outer) == "http://owl.virtualflybrain.org/kbs/vfb/"


def test_failure_url_none_when_nothing_url_shaped(guard):
    assert guard._failure_url(ConnectionError("no address here")) is None


# ---------------------------------------------------------------------------
# Probe detail
# ---------------------------------------------------------------------------

def test_probe_records_how_each_backend_answered(guard, monkeypatch):
    def fake_get(url, timeout):
        if "pdb" in url:
            raise requests.ReadTimeout("Read timed out. (read timeout=5)")

        class Resp:
            status_code = 200
        return Resp()

    monkeypatch.setattr(guard.requests, "get", fake_get)
    assert guard._backend_down() is True
    detail = guard._probe_cache["detail"]
    assert detail[0]["ok"] and detail[0]["status"] == 200      # solr answered
    assert not detail[1]["ok"] and "ReadTimeout" in detail[1]["error"]
    # the failing probe reaches the skip message…
    assert "pdb.virtualflybrain.org" in guard._probe_failure_suffix()
    assert "ReadTimeout" in guard._probe_failure_suffix()
    # …and the event log, for the report.
    events = [json.loads(line) for line in open(guard._OUTAGE_EVENTS)]
    assert events and events[0]["event"] == "probe"


def test_probe_suffix_empty_when_healthy(guard):
    guard._probe_cache.update(detail=[{"url": "x", "ok": True, "status": 200}])
    assert guard._probe_failure_suffix() == ""


# ---------------------------------------------------------------------------
# The report itself
# ---------------------------------------------------------------------------

def _sample_events():
    return [
        {"event": "trigger", "test": "src/test/test_a.py::test_one",
         "kind": "connection-failure",
         "error": "ConnectionError: Failed to establish a new connection",
         "url": "https://pdb.virtualflybrain.org/db/neo4j/tx/commit",
         "time": 1.0},
        {"event": "trigger", "test": "src/test/test_a.py::test_one",   # dupe
         "kind": "connection-failure", "error": "again", "url": None,
         "time": 2.0},
        {"event": "trigger", "test": "src/test/test_b.py::test_two",
         "kind": "timeout", "error": "Failed: Timeout >300.0s", "url": None,
         "time": 3.0},
        {"event": "probe", "probes": [
            {"url": "http://solr.virtualflybrain.org/solr/vfb_json/admin/ping",
             "ok": True, "status": 200, "elapsed_s": 0.1},
            {"url": "http://pdb.virtualflybrain.org/", "ok": False,
             "status": None, "error": "ReadTimeout: Read timed out.",
             "elapsed_s": 5.0}], "time": 4.0},
        {"event": "skip", "test": "src/test/test_c.py::test_three", "time": 5.0},
        {"event": "skip", "test": "src/test/test_c.py::test_three", "time": 5.5},
        {"event": "skip", "test": "src/test/test_d.py::test_four", "time": 6.0},
    ]


def test_report_names_tests_urls_and_failure_modes(guard):
    markdown, summary = guard.build_outage_report(_sample_events())
    assert "2 test(s) hit the backend directly" in summary
    assert "2 more were fast-skipped" in summary
    # the triggering tests, deduplicated, with kind and error
    assert markdown.count("test_a.py::test_one") == 1
    assert "connection-failure" in markdown and "timeout" in markdown
    # the failing call is a clickable markdown link
    assert ("[https://pdb.virtualflybrain.org/db/neo4j/tx/commit]"
            "(https://pdb.virtualflybrain.org/db/neo4j/tx/commit)") in markdown
    # probe verdicts, both ways, with the URL linked
    assert "**FAILED** — [http://pdb.virtualflybrain.org/]" in markdown
    assert "OK — [http://solr.virtualflybrain.org" in markdown
    assert "ReadTimeout" in markdown
    # every fast-skipped test is listed, once, inside a details fold
    assert markdown.count("test_c.py::test_three") == 1
    assert "test_d.py::test_four" in markdown
    assert "<details>" in markdown


def test_sessionfinish_writes_the_report_files(guard, tmp_path, monkeypatch):
    with open(guard._OUTAGE_EVENTS, "w") as fh:
        for event in _sample_events():
            fh.write(json.dumps(event) + "\n")

    class Config:
        class invocation_params:
            dir = str(tmp_path)

    class Session:
        config = Config()

    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    guard.pytest_sessionfinish(Session(), 0)
    markdown = (tmp_path / guard.OUTAGE_REPORT_MD).read_text()
    assert "VFB backend outage report" in markdown
    events = json.loads((tmp_path / guard.OUTAGE_REPORT_JSON).read_text())
    assert len(events) == len(_sample_events())


def test_sessionfinish_silent_when_no_outage(guard, tmp_path, monkeypatch):
    class Config:
        class invocation_params:
            dir = str(tmp_path)

    class Session:
        config = Config()

    monkeypatch.delenv("PYTEST_XDIST_WORKER", raising=False)
    guard.pytest_sessionfinish(Session(), 0)
    assert not (tmp_path / guard.OUTAGE_REPORT_MD).exists()
