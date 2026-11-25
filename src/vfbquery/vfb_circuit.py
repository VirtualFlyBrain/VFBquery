"""Circuit paths over class- and neuron-level connectivity graphs (#114).

Loads a run folder written by :mod:`vfbquery.vfb_circuit_classes` and finds
the k strongest paths between two sets of query terms, separately in each
connectome dataset.

**Scoring.** Every edge has an input proportion (inprop: synapses from A to B
as a share of B's total input) or, with ``normalise="output"``, an output
proportion. A path's cost is the sum of ``-log(inprop)`` over its edges, so
the k cheapest paths (Yen's algorithm) are the chains with the highest product
of inprops, and ``score = exp(-cost)`` is that product.

**Levels.** If both ends are classes, the search runs on the dataset's class
graph, whose nodes are leaf classes (see :mod:`vfbquery.vfb_circuit_classes`).
A broad query term such as Kenyon cell expands to every leaf class beneath it
in that dataset. If either end includes a neuron, the search runs on the
neuron graph, and class terms expand to the neurons assigned to their leaf
classes. With ``instance_graph=True``, each class path also gets its best
neuron chains: paths in the neuron graph that step from a neuron of each class
to a neuron of the next.

**Neurons without a class.** Neuron-level paths can pass through neurons left
out of the class graph. Their nodes have ``class: None``, plus ``status`` (why:
``no_leaf``, ``multi_leaf``, ``only_axis`` or ``untyped``) and ``types``
(``[{id, label}]``, the most specific types they do have) from the run's
``report.tsv``.

**Many sources and targets in one search.** Each graph has two extra vertices,
a start joined to every vertex and an end joined from every vertex. A request
passes its own weight vector, which is infinite (edge ignored) everywhere
except: the real edges that pass the thresholds, the start edges to the
request's sources and the end edges from its targets (both cost 0). The same
vector also blocks edges into a source and out of a target, so a path never
passes through either partway. Nothing in the graph changes, so concurrent
searches on one graph are safe, and a FlyWire neuron-level search takes about
0.5 s.
"""
import collections
import gzip
import hashlib
import json
import math
import os
import time
import warnings

import numpy as np
import pandas as pd

from .vfb_circuit_classes import FORMAT_VERSION, MANIFEST

try:                                       # optional: only circuit mode needs it
    import igraph
except ImportError:                        # pragma: no cover - checked at load
    igraph = None

#: Search limits. Yen's cost grows with k; the browser shows a handful of paths.
MAX_K = 20
MAX_INSTANCE_K = 10
DEFAULT_K = 5
DEFAULT_INSTANCE_K = 3
#: Seconds a search may spend on example neuron chains (instance_graph). Each
#: chain search is one uninterruptible igraph call, 0.3-3 s on the large
#: connectomes, so a search can run over by about that much.
DEFAULT_TIME_LIMIT = 30.0
#: Same default threshold as /query_connectivity's ``weight``.
DEFAULT_MIN_SYNAPSES = 5
NORMALISE = ("input", "output")

#: Real edges are added to igraph in chunks, which keeps the transient memory
#: of building a large graph (male CNS: 15M edges) well below one big call.
_EDGE_CHUNK = 2_000_000


class CircuitDataError(RuntimeError):
    """A run folder that cannot be loaded: missing, incomplete or corrupt."""


# ---------------------------------------------------------------------------
# Reading files
# ---------------------------------------------------------------------------

def _header_lines(path):
    """Number of leading '#' lines (read separately: data may contain '#')."""
    opener = gzip.open if path.endswith(".gz") else open
    n = 0
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def _read_tsv(path, dtype):
    return pd.read_csv(path, sep="\t", skiprows=_header_lines(path), dtype=dtype,
                       keep_default_na=False, na_values={k: [""] for k, v in dtype.items()
                                                         if v == "float64"},
                       quoting=3)


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve_current(root):
    """The run folder that ``<root>/CURRENT`` points at.

    CURRENT holds a run name (a folder under ``root``) or a path.
    """
    with open(os.path.join(root, "CURRENT"), encoding="utf-8") as f:
        value = f.read().strip()
    if not value:
        raise CircuitDataError(f"{root}/CURRENT is empty")
    return value if os.path.isabs(value) else os.path.join(root, value)


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------

class LevelGraph:
    """One graph (class or neuron level) with permanent start and end vertices."""

    def __init__(self, names, src, dst, synapses, inprop_in, inprop_out, pairs=None):
        if igraph is None:
            raise CircuitDataError("python-igraph is not installed (pip install igraph)")
        self.names = np.asarray(names, dtype=object)
        self.index = {x: i for i, x in enumerate(self.names)}
        self.n, self.m = len(self.names), len(src)
        self.src = np.asarray(src, dtype=np.int32)
        self.dst = np.asarray(dst, dtype=np.int32)
        self.synapses = np.asarray(synapses, dtype=np.int32)
        self.pairs = None if pairs is None else np.asarray(pairs, dtype=np.int32)
        self.inprop = {"input": np.asarray(inprop_in, dtype=np.float64),
                       "output": np.asarray(inprop_out, dtype=np.float64)}
        with np.errstate(divide="ignore", invalid="ignore"):
            self.cost = {k: np.where(v > 0, -np.log(v), np.inf)
                         for k, v in self.inprop.items()}
        self.has_output = bool(np.isfinite(self.cost["output"]).any()) if self.m else False

        n = self.n
        self.start, self.end = n, n + 1
        g = igraph.Graph(n=n + 2, directed=True)
        for i in range(0, self.m, _EDGE_CHUNK):
            g.add_edges(np.column_stack([self.src[i:i + _EDGE_CHUNK],
                                         self.dst[i:i + _EDGE_CHUNK]]))
        allv = np.arange(n, dtype=np.int64)
        g.add_edges(np.column_stack([np.full(n, self.start), allv]))   # m .. m+n-1
        g.add_edges(np.column_stack([allv, np.full(n, self.end)]))     # m+n .. m+2n-1
        self.graph = g

    def search(self, sources, targets, k, edge_ok, normalise):
        """k cheapest paths from any of ``sources`` to any of ``targets``.

        ``sources``/``targets`` are vertex indices; ``edge_ok`` is a boolean
        mask over the real edges. Returns ``[(vertices, edge ids, cost)]``.
        """
        n, m = self.n, self.m
        sources = np.unique(np.asarray(sources, dtype=np.int64))
        targets = np.unique(np.asarray(targets, dtype=np.int64))
        if not len(sources) or not len(targets):
            return []
        w = np.full(m + 2 * n, np.inf)
        real = w[:m]
        real[edge_ok] = self.cost[normalise][edge_ok]
        # No passing through a source or a target partway. A vertex that is
        # both may be stepped into (as a target) and out of (as a source).
        both = np.intersect1d(sources, targets)
        mark = np.zeros(n, dtype=bool)
        mark[np.setdiff1d(sources, both)] = True
        real[mark[self.dst]] = np.inf
        mark[:] = False
        mark[np.setdiff1d(targets, both)] = True
        real[mark[self.src]] = np.inf
        w[m + sources] = 0.0
        w[m + n + targets] = 0.0

        # A vertex in both sets gives a zero-hop path start -> v -> end; ask
        # for enough extra paths to drop those and still return k.
        want = k + len(both)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)   # unreachable vertices
            found = self.graph.get_k_shortest_paths(
                self.start, self.end, k=want, weights=w.tolist(), mode="out", output="epath")
        out = []
        for epath in found:
            edges = [e for e in epath[1:-1]]
            if not edges:
                continue
            vertices = [int(self.src[edges[0]])] + [int(self.dst[e]) for e in edges]
            out.append((vertices, edges, float(w[edges].sum())))
            if len(out) == k:
                break
        return out


class Connectome:
    """One dataset's class graph, neuron graph and class assignments."""

    def __init__(self, key, folder, info):
        self.key = key
        self.label = info.get("label", "")
        self.symbol = info.get("symbol", "")
        self.neurons = info.get("neurons", 0)
        self.assigned = info.get("assigned", 0)

        classes = _read_tsv(os.path.join(folder, "classes.tsv.gz"),
                            {"class": str, "label": str, "symbol": str,
                             "neurons": "int64", "ancestors": str})
        self.classes = {r["class"]: {"label": r["label"], "symbol": r["symbol"],
                                     "neurons": int(r["neurons"])}
                        for r in classes.to_dict("records")}
        # term -> the leaf classes it stands for (itself, if it is one)
        self.leaves_under = collections.defaultdict(list)
        for c, anc in zip(classes["class"], classes["ancestors"]):
            self.leaves_under[c].append(c)
            for a in filter(None, anc.split("|")):
                self.leaves_under[a].append(c)
        self.leaves_under = dict(self.leaves_under)

        ce = _read_tsv(os.path.join(folder, "class_edges.tsv.gz"),
                       {"source": str, "target": str, "synapses": "int64", "pairs": "int64",
                        "inprop_in": "float64", "inprop_out": "float64"})
        cnames = pd.Index(classes["class"])
        self.class_graph = LevelGraph(
            cnames.to_numpy(), cnames.get_indexer(ce["source"]), cnames.get_indexer(ce["target"]),
            ce["synapses"], ce["inprop_in"], ce["inprop_out"], pairs=ce["pairs"])
        del ce

        nc = _read_tsv(os.path.join(folder, "neuron_classes.tsv.gz"),
                       {"neuron": str, "class": str})
        ne = _read_tsv(os.path.join(folder, "neuron_edges.tsv.gz"),
                       {"source": str, "target": str, "synapses": "int64",
                        "inprop_in": "float64", "inprop_out": "float64"})
        nnames = pd.Index(pd.unique(pd.concat([ne["source"], ne["target"], nc["neuron"]],
                                              ignore_index=True)))
        self.neuron_graph = LevelGraph(
            nnames.to_numpy(), nnames.get_indexer(ne["source"]), nnames.get_indexer(ne["target"]),
            ne["synapses"], ne["inprop_in"], ne["inprop_out"])
        del ne
        # neuron vertex -> class vertex (-1: not assigned), and the reverse
        self.neuron_class = np.full(self.neuron_graph.n, -1, dtype=np.int32)
        self.neuron_class[nnames.get_indexer(nc["neuron"])] = cnames.get_indexer(nc["class"])
        # neuron -> (status, [(type id, label)]) for neurons left out of the class graph
        self.left_out = {}
        report = os.path.join(folder, "report.tsv")
        if os.path.exists(report):
            rep = _read_tsv(report, {"neuron": str, "status": str, "types": str, "labels": str})
            for n, st, ts, ls in zip(rep["neuron"], rep["status"], rep["types"], rep["labels"]):
                ids = ts.split("|") if ts else []
                labels = ls.split("|") if ls else []
                if len(labels) != len(ids):
                    labels = ids
                self.left_out[n] = (st, list(zip(ids, labels)))
        order = np.argsort(self.neuron_class, kind="stable")
        bounds = np.searchsorted(self.neuron_class[order], np.arange(len(cnames) + 1))
        self.class_members = [order[bounds[i]:bounds[i + 1]] for i in range(len(cnames))]

    def site(self):
        """This dataset as /list_connectome_datasets describes one."""
        return {"label": self.label, "symbol": self.symbol, "short_form": self.key}

    def expand(self, term):
        """``("neuron", [vertex])``, ``("class", [leaf ids])`` or ``None``."""
        if term in self.neuron_graph.index:
            return "neuron", [self.neuron_graph.index[term]]
        leaves = self.leaves_under.get(term)
        if leaves:
            return "class", sorted(set(leaves))
        return None

    # -- formatting --------------------------------------------------------

    def class_node(self, c):
        info = self.classes[c]
        return {"id": c, "label": info["label"], "symbol": info["symbol"],
                "neurons": info["neurons"]}

    def neuron_node(self, v):
        c = self.neuron_class[v]
        node = {"id": self.neuron_graph.names[v], "class": None}
        if c >= 0:
            cid = self.class_graph.names[c]
            node.update({"class": cid, "class_label": self.classes[cid]["label"],
                         "class_symbol": self.classes[cid]["symbol"]})
        elif node["id"] in self.left_out:
            # Why the neuron has no class, and the types it does have
            status, types = self.left_out[node["id"]]
            node.update({"status": status,
                         "types": [{"id": t, "label": label} for t, label in types]})
        return node


class Store:
    """Every connectome of one run, as loaded from its folder."""

    def __init__(self, folder, manifest, datasets, seconds):
        self.folder = folder
        self.manifest = manifest
        self.run = manifest.get("run", "")
        self.built = manifest.get("built", "")
        self.datasets = datasets
        self.load_seconds = seconds

    def sites(self):
        return [c.site() for c in self.datasets.values()]

    def terms(self):
        """Every FBbt term with neurons in some dataset: the leaf classes and
        all their superclasses, i.e. every class a search can start from."""
        if getattr(self, "_terms", None) is None:
            self._terms = sorted(set().union(*(c.leaves_under for c in self.datasets.values())))
        return self._terms

    def summary(self):
        return {"run": self.run, "built": self.built, "folder": self.folder,
                "load_seconds": round(self.load_seconds, 1),
                "datasets": {k: {"label": c.label, "symbol": c.symbol,
                                 "neurons": c.neurons, "assigned": c.assigned,
                                 "classes": c.class_graph.n,
                                 "class_edges": c.class_graph.m,
                                 "neuron_edges": c.neuron_graph.m}
                             for k, c in self.datasets.items()}}


def load_run(folder, verify=True, log=print):
    """Load a run folder. Raises :class:`CircuitDataError` if it is incomplete."""
    t0 = time.time()
    path = os.path.join(folder, MANIFEST)
    if not os.path.exists(path):
        raise CircuitDataError(f"no {MANIFEST} in {folder}: build incomplete or wrong folder")
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    if manifest.get("format") != FORMAT_VERSION:
        raise CircuitDataError(f"{path}: format {manifest.get('format')!r}, "
                               f"this VFBquery reads format {FORMAT_VERSION}")
    if verify:
        for key, info in manifest["datasets"].items():
            for rel, f in info["files"].items():
                p = os.path.join(folder, rel)
                if not os.path.exists(p):
                    raise CircuitDataError(f"missing {p}")
                if _sha256(p) != f["sha256"]:
                    raise CircuitDataError(f"checksum mismatch: {p}")
    datasets = {}
    for key, info in sorted(manifest["datasets"].items()):
        t = time.time()
        datasets[key] = Connectome(key, os.path.join(folder, key), info)
        log(f"circuit: loaded {key} ({time.time() - t:.0f}s)")
    return Store(folder, manifest, datasets, time.time() - t0)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def _num(x):
    x = float(x)
    return None if math.isnan(x) else x


def _edge(g, e, names):
    out = {"source": names[g.src[e]], "target": names[g.dst[e]],
           "synapses": int(g.synapses[e])}
    if g.pairs is not None:
        out["pairs"] = int(g.pairs[e])
    out["inprop_in"] = _num(g.inprop["input"][e])
    out["inprop_out"] = _num(g.inprop["output"][e])
    return out


def _thresholds(g, min_synapses, min_inprop, normalise):
    ok = g.synapses >= min_synapses
    if min_inprop > 0:
        ok &= g.inprop[normalise] >= min_inprop
    return ok


def _instance_chains(con, class_path, k, normalise):
    """The k best neuron chains that follow one class path, hop by hop."""
    ng = con.neuron_graph
    ncls = con.class_graph.n
    pairs = {class_path[i] * ncls + class_path[i + 1] for i in range(len(class_path) - 1)}
    cs, cd = con.neuron_class[ng.src].astype(np.int64), con.neuron_class[ng.dst].astype(np.int64)
    ok = (cs >= 0) & (cd >= 0) & np.isin(cs * ncls + cd, list(pairs))
    chains = ng.search(con.class_members[class_path[0]], con.class_members[class_path[-1]],
                       k, ok, normalise)
    return [{"score": math.exp(-cost),
             "neurons": [ng.names[v] for v in vertices],
             "edges": [_edge(ng, e, ng.names) for e in edges]}
            for vertices, edges, cost in chains]


def validate(k=DEFAULT_K, min_synapses=DEFAULT_MIN_SYNAPSES, min_inprop=0.0,
             normalise="input", instance_k=DEFAULT_INSTANCE_K):
    """Raise ValueError on a parameter outside its range."""
    if not 1 <= k <= MAX_K:
        raise ValueError(f"k must be between 1 and {MAX_K}")
    if not 1 <= instance_k <= MAX_INSTANCE_K:
        raise ValueError(f"instance_k must be between 1 and {MAX_INSTANCE_K}")
    if min_synapses < 0:
        raise ValueError("min_synapses must be at least 0")
    if not 0 <= min_inprop <= 1:
        raise ValueError("min_inprop must be between 0 and 1")
    if normalise not in NORMALISE:
        raise ValueError(f"normalise must be one of: {', '.join(NORMALISE)}")


def search_dataset(con, sources, targets, k=DEFAULT_K, min_synapses=DEFAULT_MIN_SYNAPSES,
                   min_inprop=0.0, normalise="input", instance_graph=False,
                   instance_k=DEFAULT_INSTANCE_K):
    """Search one dataset. Returns its result block, or None if an end is absent."""
    exp_s = {t: con.expand(t) for t in sources}
    exp_t = {t: con.expand(t) for t in targets}
    if not any(exp_s.values()) or not any(exp_t.values()):
        return None
    neuron_level = any(e and e[0] == "neuron" for e in list(exp_s.values()) + list(exp_t.values()))
    cg, ng = con.class_graph, con.neuron_graph

    def ends(expanded):
        listed, vertices = {}, []
        for term, e in expanded.items():
            if not e:
                listed[term] = []
                continue
            kind, items = e
            if kind == "neuron":
                listed[term] = [con.neuron_node(items[0])]
                vertices += items
            else:
                listed[term] = [con.class_node(c) for c in items]
                idx = [cg.index[c] for c in items]
                if neuron_level:
                    for i in idx:
                        vertices += con.class_members[i].tolist()
                else:
                    vertices += idx
        return listed, vertices

    src_listed, src_v = ends(exp_s)
    tgt_listed, tgt_v = ends(exp_t)
    block = {"dataset": con.key, "label": con.label, "symbol": con.symbol,
             "level": "neuron" if neuron_level else "class",
             "sources": src_listed, "targets": tgt_listed,
             "neurons_left_out": con.neurons - con.assigned, "paths": []}

    g = ng if neuron_level else cg
    if normalise == "output" and not g.has_output:
        block["note"] = "No output totals in this dataset, so normalise=output is unavailable."
        return block
    found = g.search(src_v, tgt_v, k, _thresholds(g, min_synapses, min_inprop, normalise),
                     normalise)
    for vertices, edges, cost in found:
        if neuron_level:
            nodes = [con.neuron_node(v) for v in vertices]
        else:
            nodes = [con.class_node(cg.names[v]) for v in vertices]
        path = {"score": math.exp(-cost), "hops": len(edges), "nodes": nodes,
                "edges": [_edge(g, e, g.names) for e in edges]}
        if instance_graph and not neuron_level:
            path["instances"] = _instance_chains(con, vertices, instance_k, normalise)
        block["paths"].append(path)
    return block


def find_paths(store, sources, targets, k=DEFAULT_K, min_synapses=DEFAULT_MIN_SYNAPSES,
               min_inprop=0.0, normalise="input", exclude=(), instance_graph=False,
               instance_k=DEFAULT_INSTANCE_K, time_limit=None):
    """Search every dataset in ``store`` except the ``exclude`` keys.

    ``time_limit`` (seconds, None for none) bounds the time spent on example
    neuron chains, the slow part of ``instance_graph``. The paths themselves
    are always returned; chains are found best path first, taking each
    dataset's first path, then each one's second, and so on, and stop when the
    time is up. Paths left without chains have no ``instances`` key, and the
    response says how many.
    """
    validate(k, min_synapses, min_inprop, normalise, instance_k)
    if time_limit is not None and not time_limit > 0:
        raise ValueError("time_limit must be a positive number of seconds")
    t0 = time.time()
    blocks, found_in = [], {t: [] for t in list(sources) + list(targets)}
    for key, con in store.datasets.items():
        if key in exclude:
            continue
        for t in found_in:
            if con.expand(t):
                found_in[t].append(key)
        block = search_dataset(con, sources, targets, k, min_synapses, min_inprop,
                               normalise, False, instance_k)
        if block is not None:
            blocks.append((con, block))
    timed_out = _add_instances(blocks, instance_k, normalise, time_limit, t0) if instance_graph else 0
    blocks = [b for _, b in blocks]

    shared = collections.defaultdict(list)
    for b in blocks:
        if b["level"] == "class":
            for p in b["paths"]:
                shared[tuple(n["id"] for n in p["nodes"])].append(b["dataset"])
    warnings_ = [f"{t} was not found in any searched dataset" for t, ds in found_in.items()
                 if not ds]
    result = {
        "run": store.run, "built": store.built,
        "query": {"sources": list(sources), "targets": list(targets), "k": k,
                  "min_synapses": min_synapses, "min_inprop": min_inprop,
                  "normalise": normalise, "instance_graph": instance_graph,
                  "instance_k": instance_k},
        "excluded_dbs": sorted(exclude),
        "found_in": found_in,
        "datasets": blocks,
        "shared_class_paths": [{"classes": list(c), "datasets": ds}
                               for c, ds in shared.items() if len(ds) > 1],
        "seconds": round(time.time() - t0, 3),
    }
    if timed_out:
        result["time_limit_reached"] = True
        warnings_.append(
            f"Time limit ({time_limit:g} s) reached: {timed_out} of the class paths have no "
            "example neuron chains (no 'instances'). Ask for fewer paths (k) or chains "
            "(instance_k), or fewer datasets, to get them all.")
    if warnings_:
        result["warnings"] = warnings_
    return result


def _add_instances(blocks, instance_k, normalise, time_limit, t0):
    """Add example neuron chains to class paths until ``time_limit`` is used.

    Best paths first across datasets, so that every dataset gets chains for
    its top path before any gets them for its second. Returns how many paths
    were left without chains.
    """
    pending = [(rank, i, con, path)
               for i, (con, block) in enumerate(blocks) if block["level"] == "class"
               for rank, path in enumerate(block["paths"])]
    pending.sort(key=lambda x: (x[0], x[1]))
    skipped = 0
    for _, _, con, path in pending:
        if time_limit is not None and time.time() - t0 >= time_limit:
            skipped += 1
            continue
        vertices = [con.class_graph.index[n["id"]] for n in path["nodes"]]
        path["instances"] = _instance_chains(con, vertices, instance_k, normalise)
    return skipped
