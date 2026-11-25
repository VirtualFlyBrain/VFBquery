"""Circuit path search and circuit mode (#114). Offline.

A tiny dataset is written with the real build code
(:func:`vfbquery.vfb_circuit_classes.write_site`), loaded with the real loader
and searched. Hand-checkable numbers:

    classes A (a1, a2), B (b1), C (c1), D (d1), X (x1); AB is a superclass of A and B

    edge     synapses  target total input  class inprop_in
    a1->c1   10        c1: 40              A->C  (10+10)/40           = 0.5
    a2->c1   10
    c1->d1   20        d1: 100             C->D  20/100               = 0.2
    a1->d1   2                             A->D  2/100                = 0.02
    b1->a1   10        a1: 20              B->A  (10/20 + 0/a2) / 2   = 0.25
    a1->x1   6         x1: 10              A->X  6/10                 = 0.6
    x1->d1   6                             X->D  6/100                = 0.06

So from A to D: A-C-D scores 0.1, A-X-D 0.036 and A-D 0.02 (2 synapses, below
the default threshold of 5).
"""
import asyncio
import json
import math
import os

import pytest

igraph = pytest.importorskip("igraph")

from vfbquery import vfb_circuit as vc                       # noqa: E402
from vfbquery import vfb_circuit_classes as vcc              # noqa: E402

TYPES = {"a1": ["A"], "a2": ["A"], "b1": ["B"], "c1": ["C"], "d1": ["D"], "x1": ["X"]}
ANC = {"A": {"AB"}, "B": {"AB"}, "C": set(), "D": set(), "X": set()}
LABELS = {"A": "class A", "B": "class B", "C": "class C", "D": "class D", "X": "class X"}
EDGES = [("a1", "c1", 10), ("a2", "c1", 10), ("c1", "d1", 20), ("a1", "d1", 2),
         ("b1", "a1", 10), ("a1", "x1", 6), ("x1", "d1", 6)]
UP = {"c1": 40, "d1": 100, "a1": 20, "x1": 10}
DOWN = {"a1": 20, "a2": 20, "b1": 10, "c1": 20, "x1": 10}


def write_run(folder, run="run-1", datasets=None):
    """Write a run folder; ``datasets`` maps key -> (symbol, down totals)."""
    datasets = datasets or {"tiny": ("tn", DOWN)}
    meta = {"built": "2026-11-18T00:00:00Z"}
    entries = {}
    for key, (symbol, down) in datasets.items():
        _, entry = vcc.write_site(os.path.join(folder, key), dict(meta, run=run, connectome=key),
                                  TYPES, UP, down, LABELS, {}, ANC, iter(EDGES),
                                  log=lambda *_: None)
        entries[key] = dict(entry, label=f"{key} label", symbol=symbol)
    vcc.write_manifest(str(folder), run, meta, entries)
    return str(folder)


@pytest.fixture(scope="module")
def store(tmp_path_factory):
    folder = write_run(tmp_path_factory.mktemp("run"))
    return vc.load_run(folder, log=lambda *_: None)


def paths(result, dataset="tiny"):
    block = next(b for b in result["datasets"] if b["dataset"] == dataset)
    return [[n["id"] for n in p["nodes"]] for p in block["paths"]], block


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def test_class_paths_are_ranked_by_product_of_inprops(store):
    r = vc.find_paths(store, ["A"], ["D"])
    got, block = paths(r)
    assert block["level"] == "class"
    assert got == [["A", "C", "D"], ["A", "X", "D"]]
    assert [p["score"] for p in block["paths"]] == pytest.approx([0.1, 0.036])
    assert block["paths"][0]["edges"][0] == {
        "source": "A", "target": "C", "synapses": 20, "pairs": 2,
        "inprop_in": 0.5, "inprop_out": 0.5}


def test_min_synapses_and_min_inprop_filter_edges(store):
    got, _ = paths(vc.find_paths(store, ["A"], ["D"], min_synapses=0))
    assert ["A", "D"] in got
    # X->D (0.06) falls below min_inprop; A->C (0.5) and C->D (0.2) do not.
    got, _ = paths(vc.find_paths(store, ["A"], ["D"], min_inprop=0.1))
    assert got == [["A", "C", "D"]]


def test_broad_term_expands_to_its_leaf_classes(store):
    r = vc.find_paths(store, ["AB"], ["D"])
    got, block = paths(r)
    assert [n["id"] for n in block["sources"]["AB"]] == ["A", "B"]
    # B -> A -> C -> D would pass through source A partway, so it is not offered.
    assert got == [["A", "C", "D"], ["A", "X", "D"]]


def test_neuron_end_searches_the_neuron_graph(store):
    got, block = paths(vc.find_paths(store, ["a1"], ["D"]))
    assert block["level"] == "neuron"
    assert got == [["a1", "c1", "d1"], ["a1", "x1", "d1"]]
    assert block["paths"][0]["score"] == pytest.approx(10 / 40 * 20 / 100)
    assert block["paths"][0]["nodes"][1]["class"] == "C"


def _write_left_out_run(folder):
    """x1 has two leaf types (X, Y); z1 is typed only to AB, which A and B subtype."""
    types = dict(TYPES, x1=["X", "Y"], z1=["AB"])
    labels = dict(LABELS, Y="class Y", AB="class AB")
    anc = dict(ANC, Y=set())
    edges = EDGES + [("a1", "z1", 6), ("z1", "d1", 6)]
    up = dict(UP, z1=10)
    down = dict(DOWN, z1=10)
    meta = {"built": "2026-11-18T00:00:00Z"}
    _, entry = vcc.write_site(os.path.join(folder, "tiny"), dict(meta, run="run-1", connectome="tiny"),
                              types, up, down, labels, {}, anc, iter(edges), log=lambda *_: None)
    vcc.write_manifest(str(folder), "run-1", meta, {"tiny": dict(entry, label="tiny label", symbol="tn")})
    return str(folder)


def test_neurons_without_a_class_say_why(tmp_path):
    store = vc.load_run(_write_left_out_run(tmp_path), log=lambda *_: None)
    _, block = paths(vc.find_paths(store, ["a1"], ["D"]))
    nodes = {n["id"]: n for p in block["paths"] for n in p["nodes"]}
    assert nodes["x1"]["class"] is None
    assert nodes["x1"]["status"] == "multi_leaf"
    assert sorted(t["id"] for t in nodes["x1"]["types"]) == ["X", "Y"]
    assert {t["id"]: t["label"] for t in nodes["x1"]["types"]}["Y"] == "class Y"
    assert nodes["z1"]["status"] == "no_leaf"
    assert nodes["z1"]["types"] == [{"id": "AB", "label": "class AB"}]
    # Neurons with a class carry neither
    assert nodes["d1"]["class"] == "D" and "status" not in nodes["d1"]


def test_a_run_without_a_report_still_loads(tmp_path):
    folder = _write_left_out_run(tmp_path)
    os.remove(os.path.join(folder, "tiny", "report.tsv"))
    store = vc.load_run(folder, verify=False, log=lambda *_: None)
    _, block = paths(vc.find_paths(store, ["a1"], ["D"]))
    x1 = next(n for p in block["paths"] for n in p["nodes"] if n["id"] == "x1")
    assert x1["class"] is None and "status" not in x1


class _Clock:
    """Stands in for the time module: each neuron chain search takes 10 s."""
    def __init__(self):
        self.now = 1000.0

    def time(self):
        return self.now


def test_neuron_chains_stop_at_the_time_limit_best_paths_first(tmp_path, monkeypatch):
    store = vc.load_run(write_run(tmp_path, datasets={"one": ("o1", DOWN), "two": ("t2", DOWN)}),
                        log=lambda *_: None)
    clock = _Clock()
    chains = vc._instance_chains

    def slow_chains(*args):
        clock.now += 10
        return chains(*args)
    monkeypatch.setattr(vc, "time", clock)
    monkeypatch.setattr(vc, "_instance_chains", slow_chains)

    result = vc.find_paths(store, ["A"], ["D"], instance_graph=True, time_limit=25)
    one, two = (next(b for b in result["datasets"] if b["dataset"] == d) for d in ("one", "two"))
    # Each dataset's best path first, then each one's second: started at 0, 10
    # and 20 s, so the fourth (two's second path) is left out.
    assert [("instances" in p) for p in one["paths"]] == [True, True]
    assert [("instances" in p) for p in two["paths"]] == [True, False]
    assert result["time_limit_reached"] is True
    assert any("1 of the class paths have no example neuron chains" in w for w in result["warnings"])

    full = vc.find_paths(store, ["A"], ["D"], instance_graph=True, time_limit=None)
    assert all("instances" in p for b in full["datasets"] for p in b["paths"])
    assert "time_limit_reached" not in full
    with pytest.raises(ValueError, match="time_limit"):
        vc.find_paths(store, ["A"], ["D"], time_limit=0)


def test_instance_graph_gives_neuron_chains_along_each_class_path(store):
    _, block = paths(vc.find_paths(store, ["A"], ["D"], instance_graph=True))
    chains = block["paths"][0]["instances"]
    assert sorted(c["neurons"] for c in chains) == [["a1", "c1", "d1"], ["a2", "c1", "d1"]]
    assert chains[0]["score"] == pytest.approx(0.05)


def test_normalise_output_uses_output_proportions(store):
    _, block = paths(vc.find_paths(store, ["A"], ["D"], normalise="output"))
    # A->C: (10/20 + 10/20) / 2 = 0.5; C->D: 20/20 = 1.0
    assert block["paths"][0]["score"] == pytest.approx(0.5)


def test_unknown_terms_are_reported(store):
    r = vc.find_paths(store, ["A"], ["nothing"])
    assert r["datasets"] == []
    assert r["warnings"] == ["nothing was not found in any searched dataset"]


def test_parameters_are_validated(store):
    with pytest.raises(ValueError):
        vc.find_paths(store, ["A"], ["D"], k=0)
    with pytest.raises(ValueError):
        vc.find_paths(store, ["A"], ["D"], normalise="both")


def test_datasets_are_searched_separately_and_shared_paths_flagged(tmp_path):
    folder = write_run(tmp_path, datasets={"one": ("o1", DOWN), "two": ("t2", {})})
    s = vc.load_run(folder, log=lambda *_: None)
    r = vc.find_paths(s, ["A"], ["D"])
    assert [b["dataset"] for b in r["datasets"]] == ["one", "two"]
    assert {"classes": ["A", "C", "D"], "datasets": ["one", "two"]} in r["shared_class_paths"]
    r = vc.find_paths(s, ["A"], ["D"], exclude={"one"})
    assert [b["dataset"] for b in r["datasets"]] == ["two"]
    # "two" has no output totals.
    _, block = paths(vc.find_paths(s, ["A"], ["D"], normalise="output"), "two")
    assert block["paths"] == [] and "normalise=output" in block["note"]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def test_folder_without_manifest_is_refused(tmp_path):
    folder = write_run(tmp_path)
    os.remove(os.path.join(folder, vcc.MANIFEST))
    with pytest.raises(vc.CircuitDataError, match="incomplete"):
        vc.load_run(folder)


def test_corrupt_file_is_refused(tmp_path):
    folder = write_run(tmp_path)
    with open(os.path.join(folder, "tiny", "report.tsv"), "a") as f:
        f.write("extra\n")
    with pytest.raises(vc.CircuitDataError, match="checksum"):
        vc.load_run(folder)


def test_current_names_a_run_folder(tmp_path):
    (tmp_path / "CURRENT").write_text("run-7\n")
    assert vc.resolve_current(str(tmp_path)) == str(tmp_path / "run-7")


# ---------------------------------------------------------------------------
# Circuit mode (HTTP)
# ---------------------------------------------------------------------------

def _serve(app, calls):
    """Run ``calls(client)`` against ``app`` and return its result."""
    from aiohttp.test_utils import TestClient, TestServer

    async def main():
        async with TestClient(TestServer(app)) as client:
            return await calls(client)
    return asyncio.run(main())


async def _wait_loaded(client):
    for _ in range(200):
        r = await client.get("/health")
        if r.status == 200:
            return
        await asyncio.sleep(0.05)
    raise AssertionError("graphs never loaded")


def test_circuit_mode_serves_paths_and_names_the_run(tmp_path):
    from vfbquery.circuit_api import create_circuit_app
    write_run(tmp_path / "run-1", datasets={"tiny": ("tn", DOWN), "hemi": ("hb", DOWN)})
    (tmp_path / "CURRENT").write_text("run-1")

    async def calls(client):
        await _wait_loaded(client)
        r = await client.get("/circuit_paths", params={"source": "A", "target": "D",
                                                       "colour": "red"})
        body = await r.json()
        bad = await client.get("/circuit_paths", params={"source": "A", "target": "D",
                                                         "exclude_dbs": "nope"})
        all_dbs = await client.get("/circuit_paths", params={"source": "A", "target": "D",
                                                             "exclude_dbs": ""})
        status = await (await client.get("/status")).json()
        return r.status, body, bad.status, await all_dbs.json(), status

    app = create_circuit_app(root=str(tmp_path), workers=0, poll=3600, time_limit=12)
    status, body, bad, all_dbs, st = _serve(app, calls)
    assert st["time_limit"] == 12
    assert status == 200
    assert body["run"] == "run-1"
    # hb is excluded by default, as on /query_connectivity.
    assert [b["dataset"] for b in body["datasets"]] == ["tiny"]
    assert body["excluded_dbs"] == ["hemi"]
    assert any("colour" in w for w in body["warnings"])
    assert bad == 400
    assert [b["dataset"] for b in all_dbs["datasets"]] == ["hemi", "tiny"]
    assert st["serving"]["run"] == "run-1"


def test_circuit_mode_is_unavailable_until_a_run_loads(tmp_path):
    from vfbquery.circuit_api import create_circuit_app
    (tmp_path / "CURRENT").write_text("missing-run")

    async def calls(client):
        await asyncio.sleep(0.2)
        r = await client.get("/circuit_paths", params={"source": "A", "target": "D"})
        return r.status, await (await client.get("/status")).json()

    status, st = _serve(create_circuit_app(root=str(tmp_path), workers=0, poll=3600), calls)
    assert status == 503
    assert "no manifest.json" in st["last_error"]


def test_a_new_current_run_is_swapped_in(tmp_path):
    from vfbquery.circuit_api import create_circuit_app
    write_run(tmp_path / "run-1", run="run-1")
    write_run(tmp_path / "run-2", run="run-2")
    (tmp_path / "CURRENT").write_text("run-1")
    app = create_circuit_app(root=str(tmp_path), workers=0, poll=3600)

    async def calls(client):
        await _wait_loaded(client)
        first = (await (await client.get("/health")).json())["run"]
        (tmp_path / "CURRENT").write_text("run-2")
        await app["circuit"].refresh()
        second = await (await client.get("/circuit_paths",
                                         params={"source": "A", "target": "D"})).json()
        return first, second["run"]

    assert _serve(app, calls) == ("run-1", "run-2")


def test_circuit_routes_are_publicly_reachable(tmp_path):
    """Every circuit-mode route must be on ALLOWED_PATHS, or security_middleware
    404s it for every request that comes through the ingress (as /circuit_paths
    did in v1.22.70)."""
    from vfbquery import ha_api
    from vfbquery.circuit_api import create_circuit_app
    app = create_circuit_app(fixed_dir=str(tmp_path), workers=0, poll=60)
    assert ha_api.unreachable_routes(app) == []


def _worker_store_names():
    from vfbquery import circuit_api
    return sorted(circuit_api._STORES)


def test_new_workers_hold_only_the_run_they_serve(tmp_path):
    """Workers forked at a swap must not keep the replaced run in memory."""
    from vfbquery.circuit_api import create_circuit_app
    write_run(tmp_path / "run-1", run="run-1")
    write_run(tmp_path / "run-2", run="run-2")
    (tmp_path / "CURRENT").write_text("run-1")
    app = create_circuit_app(root=str(tmp_path), workers=1, poll=3600)

    async def calls(client):
        await _wait_loaded(client)
        (tmp_path / "CURRENT").write_text("run-2")
        await app["circuit"].refresh()
        loop = asyncio.get_running_loop()
        names = await loop.run_in_executor(app["circuit"].pool, _worker_store_names)
        paths = await (await client.get("/circuit_paths",
                                        params={"source": "A", "target": "D"})).json()
        return names, paths["run"]

    assert _serve(app, calls) == (["run-2"], "run-2")
