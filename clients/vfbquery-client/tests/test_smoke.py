"""Smoke tests for vfbquery-client.

Offline tests (adapter shaping) run anywhere. The live tests hit a real service
and are skipped unless VFB_LIVE_TESTS=1 is set, so CI stays hermetic by default.

Which service is ``VFB_API_BASE``, defaulting to the public deploy. That matters
for ``/search`` and ``/xref``: they are new in this branch, so against the public
deploy they answer 404 until it ships. ``scripts/check_gates.sh`` therefore
starts a server from the checkout and points these tests at it, which is what
makes the round-trip below a gate rather than a note to run something after
deploying.
"""
import os
import warnings

import pandas as pd
import pytest
import requests

from vfbquery_client import VfbClient, VfbError, PUBLIC_BASE_URL


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


def _stub_transport(monkeypatch, payload, seen=None, status_code=200):
    """Replace the HTTP call itself, not ``VfbClient._get``.

    Warning surfacing lives *in* ``_get``, so a test that monkeypatches ``_get``
    replaces the code under test. Stubbing ``Session.get`` instead keeps every
    line of the client on the path being exercised and leaves out only requests.
    """
    def fake_get(self, url, params=None, timeout=None):
        if seen is not None:
            seen["url"], seen["params"] = url, params
        return _FakeResponse(payload, status_code)

    monkeypatch.setattr(requests.Session, "get", fake_get, raising=True)


def test_to_df_rows_and_list_columns():
    payload = {"rows": [
        {"id": "VFB_1", "label": "n1", "tags": "Neuron|Adult", "source": "hemibrain"},
        {"id": "VFB_2", "label": "n2", "tags": "Neuron", "source": "flywire"},
    ]}
    df = VfbClient._to_df(payload)
    assert list(df["id"]) == ["VFB_1", "VFB_2"]
    assert df.loc[0, "tags"] == ["Neuron", "Adult"]      # pipe-joined -> list


def test_to_df_handles_bare_list_and_dict():
    assert len(VfbClient._to_df([{"a": 1}, {"a": 2}])) == 2
    assert len(VfbClient._to_df({"a": 1})) == 1
    assert VfbClient._to_df(None).empty


def test_to_df_unpacks_the_connectivity_envelope():
    """/query_connectivity returns `connections`, not `rows`.

    It predates the `rows` convention the other endpoints share. When `_to_df`
    knew only `rows`, this envelope fell through to the "a dict is one row"
    branch and the caller got a 1x3 frame whose cells were the whole result —
    a DataFrame, so it looked like it had worked.
    """
    payload = {"connections": [
        {"upstream": "Tm1", "downstream": "T3", "weight": 72},
        {"upstream": "Tm1", "downstream": "T3", "weight": 68},
    ], "warnings": [], "count": 2}
    df = VfbClient._to_df(payload)
    assert len(df) == 2
    assert list(df.columns) == ["upstream", "downstream", "weight"]
    assert list(df["weight"]) == [72, 68]


def test_connectivity_sends_weight_to_the_server(monkeypatch):
    """`weight` is a server-side filter, so it has to be on the wire.

    Omitting it does not mean "unfiltered": the server applies its own default
    of 5. A client that dropped the parameter would silently return a threshold
    nobody asked for, which is why the default here mirrors the server's.
    """
    seen = {}

    def fake_get(self, path, **params):
        seen["path"] = path
        seen["params"] = params
        return {"connections": [], "warnings": [], "count": 0}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    VfbClient().get_connected_neurons_by_type("Tm1", "T3 neuron", weight=60)
    assert seen["path"] == "query_connectivity"
    assert seen["params"] == {"upstream_type": "Tm1",
                              "downstream_type": "T3 neuron", "weight": 60}

    VfbClient().get_connected_neurons_by_type("Tm1", "T3 neuron")
    assert seen["params"]["weight"] == 5      # the server's own default


def test_server_warnings_reach_the_caller_from_any_endpoint(monkeypatch):
    """A 200 that is *incomplete* says so in `warnings`, and the client repeats it.

    Both cases below are answers no inspection of the rows can distinguish from
    a good one. An unresolved type returns zero rows, exactly like a genuinely
    unconnected pair, so dropping the warning turns a typo into a confident
    negative. An instance list served from the SOLR fallback because Neo4j was
    down returns a well-formed subset — 10 rows where the graph holds 68, as
    seen during a real upstream outage — and looks complete.

    Asserted on two different endpoints because the handling is central: it is
    `_get` that repeats them, not one method that remembered to.
    """
    _stub_transport(monkeypatch, {
        "connections": [],
        "warnings": ["Neuron type not found in VFB: 'DA1 lPN'."],
        "count": 0})
    with pytest.warns(UserWarning, match="not found in VFB"):
        df = VfbClient().get_connected_neurons_by_type("DA1 lPN", "Kenyon cell")
    assert df.empty

    _stub_transport(monkeypatch, {
        "headers": {}, "rows": [{"id": "VFB_1", "label": "n1"}], "count": 1,
        "warnings": ["Neo4j unavailable (...); get_instances(FBbt_00067363) answered "
                     "from the SOLR anatomy_channel_image fallback ... may be partial."]})
    with pytest.warns(UserWarning, match="may be partial"):
        assert len(VfbClient().get_instances("FBbt_00067363")) == 1


def test_a_clean_result_stays_quiet(monkeypatch):
    """The other half of the pair above: no warnings key, no Python warning.

    Without this, "warn on everything" would pass the test above and make the
    warning meaningless.
    """
    _stub_transport(monkeypatch, {"connections": [{"weight": 9}],
                                  "warnings": [], "count": 1})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert len(VfbClient().get_connected_neurons_by_type("Tm1", "T3")) == 1


def test_503_becomes_a_vfberror_not_an_httperror(monkeypatch):
    """Backpressure is a *retry later*, and it has to survive the transport.

    The server sheds load with 503 + Retry-After rather than queueing without
    bound, so this status is a routine part of the contract at 80 concurrent
    users, not an exceptional one. Left to `raise_for_status` it would surface
    as a bare `requests.HTTPError` alongside every other 4xx/5xx, which is the
    one distinction a caller writing a retry loop needs to make. Nothing else
    tests the mapping, because every other offline test stubs `_get` — the
    method the mapping lives in.
    """
    _stub_transport(monkeypatch, {"error": "Server overloaded"}, status_code=503)
    with pytest.raises(VfbError, match="busy"):
        VfbClient().term("FBbt_00067363")

    # ...and an ordinary failure still raises the transport's own error, so the
    # mapping above cannot be "turn everything into VfbError".
    _stub_transport(monkeypatch, {"error": "nope"}, status_code=500)
    with pytest.raises(requests.HTTPError):
        VfbClient().term("FBbt_00067363")


def test_base_url_comes_from_the_environment_when_set(monkeypatch):
    """Resolved per construction, not at import.

    This is what lets the live tests run against a server started from this
    checkout, which is the only way /search and /xref can be exercised end to
    end before they are deployed. Resolving it at import would mean the value
    depended on whether the module had already been loaded.
    """
    monkeypatch.setenv("VFB_API_BASE", "http://127.0.0.1:8123/")
    assert VfbClient().base_url == "http://127.0.0.1:8123"
    # An explicit argument still wins, and an empty variable is not a setting.
    assert VfbClient("https://example.org").base_url == "https://example.org"
    monkeypatch.setenv("VFB_API_BASE", "")
    assert VfbClient().base_url == PUBLIC_BASE_URL


def test_get_vfb_link():
    url = VfbClient.get_vfb_link(["VFB_jrchjtdb", "VFB_fw035286"], template="VFB_00101567")
    assert url.startswith("https://virtualflybrain.org/?id=VFB_jrchjtdb,VFB_fw035286")
    assert "t=VFB_00101567" in url


def test_search_params_sent_to_endpoint(monkeypatch):
    """Search must send names /search understands and no Solr config of its own."""
    seen = {}

    def fake_get(self, path, **params):
        seen["path"] = path
        seen["params"] = params
        return {"rows": [{"short_form": "FBbt_00067363", "label": "DA1 lPN"}]}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    df = VfbClient().search("DA1 lPN", limit=3, filter_types=["Class", "Neuron"],
                            demote_types=["Individual"])
    assert seen["path"] == "search"
    assert seen["params"]["query"] == "DA1 lPN"
    assert seen["params"]["limit"] == 3
    # Candidate depth defaults to the website's 500, not to `limit` — asking Solr
    # for fewer candidates would drop good answers before ranking sees them.
    assert seen["params"]["rows"] == 500
    assert seen["params"]["filter_types"] == "Class,Neuron"
    assert seen["params"]["demote_types"] == "Individual"
    assert "exclude_types" not in seen["params"]   # empty filters are omitted
    assert list(df["short_form"]) == ["FBbt_00067363"]


def test_resolve_to_id_ranks_before_taking_top(monkeypatch):
    """_resolve_to_id must rank a full candidate set, then take row 0."""
    seen = {}

    def fake_get(self, path, **params):
        seen.update(params)
        return {"rows": [{"short_form": "FBbt_00067363", "label": "DA1 lPN"}]}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    assert VfbClient()._resolve_to_id("DA1 lPN") == "FBbt_00067363"
    assert seen["limit"] == 1 and seen["rows"] == 500


def test_resolve_to_id_passes_ids_through(monkeypatch):
    def explode(self, path, **params):    # must not be called for an id
        raise AssertionError("searched for something that is already an id")

    monkeypatch.setattr(VfbClient, "_get", explode, raising=True)
    assert VfbClient()._resolve_to_id("VFB_jrchjtdb") == "VFB_jrchjtdb"
    assert VfbClient()._resolve_to_id("FBbt_00067363") == "FBbt_00067363"


def test_xref_requires_exactly_one_direction(monkeypatch):
    """Both id= and accession= is a mistake, not a query — /xref rejects it too.

    Sending both would silently take one direction and ignore the other, which
    reads as a working call that answered a different question.
    """
    monkeypatch.setattr(VfbClient, "_get",
                        lambda self, path, **p: {"rows": []}, raising=True)
    for kwargs in ({}, {"id": "VFB_jrchjtdb", "accession": "1734350908"}):
        with pytest.raises(ValueError):
            VfbClient().xref(**kwargs)


def test_xref_sends_only_the_given_direction(monkeypatch):
    seen = {}

    def fake_get(self, path, **params):
        seen["path"] = path
        seen["params"] = params
        return {"rows": [{"id": "VFB_jrchjtdb", "db": "hb",
                          "accession": "1734350908"}]}

    monkeypatch.setattr(VfbClient, "_get", fake_get, raising=True)
    df = VfbClient().xref(accession="1734350908", db="hb")
    assert seen["path"] == "xref"
    # _get drops Nones, so the unused direction never reaches the server.
    assert seen["params"] == {"id": None, "accession": "1734350908", "db": "hb"}
    assert list(df["id"]) == ["VFB_jrchjtdb"]


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_xref_round_trips_a_hemibrain_bodyid():
    """VFB id -> accession -> back to the same VFB id (plan C3's acceptance test)."""
    vfb = VfbClient()
    out = vfb.xref(id="VFB_jrchjtdb", db="hb")
    assert list(out["accession"]) == ["1734350908"]
    back = vfb.xref(accession="1734350908", db="hb")
    assert list(back["id"]) == ["VFB_jrchjtdb"]
    # Confirmed, not guessed: an accession VFB does not hold returns nothing
    # rather than the best-ranked near miss.
    assert vfb.xref(accession="000000000000000").empty


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_get_instances_da1lpn():
    """A floor, not an exact count — instances move with the data releases.

    Caught in its own `catch_warnings` because the interesting failure is not
    "too few rows" but *why*: when Neo4j is transiently unavailable the service
    answers 200 from the SOLR fallback with a subset (10 rows, the first time
    this happened). Asserting the absence of that warning first means the outage
    fails as an outage rather than as a mystery `10 > 50`.
    """
    with warnings.catch_warnings(record=True) as raised:
        warnings.simplefilter("always")
        df = VfbClient().get_instances("FBbt_00067363")  # DA1 lPN by id, no search hop
    degraded = [str(w.message) for w in raised if "fallback" in str(w.message)]
    assert not degraded, f"service answered from a degraded path: {degraded}"
    assert isinstance(df, pd.DataFrame) and len(df) > 50
    assert "data_source" in df.columns        # renamed from 'source'


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_connectivity_filters_server_side():
    """The pair the README documents, against the real service.

    Asserted on the *threshold* rather than a row count: the underlying
    connectome data is versioned and rows come and go, but no row may ever be
    below the weight that was asked for. If `weight` stopped reaching the
    server this fails even though the frame still looks plausible.
    """
    df = VfbClient().get_connected_neurons_by_type(
        upstream_type="transmedullary neuron Tm1",
        downstream_type="T3 neuron", weight=60)
    assert not df.empty
    assert df["weight"].min() >= 60


@pytest.mark.skipif(os.environ.get("VFB_LIVE_TESTS") != "1",
                    reason="set VFB_LIVE_TESTS=1 to run live v3-cached tests")
def test_live_search_ranks_class_first_for_da1_lpn():
    """The website's ranking puts the class above the individuals for 'DA1 lPN'.

    A plain Solr query does not — that ordering is the whole point of /search,
    so it is the thing worth asserting against the live service.
    """
    vfb = VfbClient()
    df = vfb.search("DA1 lPN", limit=5)
    assert len(df) == 5
    assert df.loc[0, "short_form"] == "FBbt_00067363"
    # Bare hemibrain bodyIds resolve too (they only match via shortform/xref).
    assert vfb._resolve_to_id("1734350908") == "VFB_jrchjtdb"
