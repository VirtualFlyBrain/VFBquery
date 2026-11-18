"""Class-level connectivity graphs for circuit paths (VirtualFlyBrain/VFBquery#114).

Builds, for one connectome dataset, a graph whose nodes are neuron classes and
whose edges carry input proportions, ready for a k-shortest-paths search on
cost ``-log(inprop)``. The search itself lives elsewhere; this module is the
build step, run once per PDB release.

**One class per neuron.** A neuron's class is its single *leaf* type in that
dataset: a direct type that has no subclass also typed to a neuron of the same
dataset. Axis classes (transmitter, lineage, birth order — see
:mod:`vfbquery.circuit_axis_classes`) are ignored first, or nearly every
neuron with a lineage annotation would have two leaf types. A neuron with no
leaf type (it is typed only to a class that is subtyped elsewhere in the
dataset, e.g. FlyWire's 1,643 KCab neurons beside its KCab-p neurons) or with
more than one (e.g. a motor neuron typed to all three thoracic segments) is
left out of the class graph and listed in the report. Leaving it out is
deliberate: a node labelled KCab that held only the unsubtyped remainder would
claim all KCab neurons while holding a fraction of them. Curation follow-up is
tracked in VirtualFlyBrain/connectome-curation#1 and #2.

**Edge weights.** For classes A and B, with n_A and n_B assigned neurons:

* ``synapses`` — sum of ``synapsed_to`` weights from A neurons to B neurons;
* ``inprop_in`` — the mean, over **all** n_B neurons (including those that get
  nothing from A), of the share of that neuron's total input coming from A:
  ``sum_b (sum_a w_ab / total_upstream_b) / n_B``;
* ``inprop_out`` — the mirror image over A's total output:
  ``sum_a (sum_b w_ab / total_downstream_a) / n_A``, or ``None`` when any A
  neuron lacks an output total (the CATMAID datasets have none).

With one neuron per class these reduce exactly to neuron-level inprop. The
totals are whole-neuron synapse counts (``total_upstream`` /
``total_downstream``, from vfb-region-connectivity), so they count every
synapse, while the PDB only holds ``synapsed_to`` edges of at least two
synapses: class edges miss single-synapse contacts, so inprop is slightly low
where a connection is made of many single synapses (KC→MBON is the classic
case).

Edges with an unassigned neuron at either end are left out of the class graph,
but their synapses still count in the totals — leaving neurons out never
inflates anyone's inprop.

**Output.** ``python -m vfbquery.vfb_circuit_classes --run RUN --out DIR``
writes one folder per connectome (neuron edges, class edges, neuron classes,
classes, and a report of the neurons left out) and then ``manifest.json``; see
the layout note above :data:`TABLES`. In the data pipeline it runs against
the run's own database; by hand, run it against pdb-analytics, not the
serving pdb.
"""
import argparse
import collections
import csv
import gzip
import hashlib
import io
import json
import os
import re
import time

from ._version import __version__
from .circuit_axis_classes import AXIS_CLASSES
from .neo4j_client import Neo4jConnect, dict_cursor

#: Read-only replica for heavy queries (see vfb-k8s docs/09-pdb.md).
ANALYTICS_ENDPOINT = "https://pdb-analytics.k8s.virtualflybrain.org"

#: Source neurons per edge query. 5,000 FlyWire neurons return ~440k edges in
#: about 8 s on pdb-analytics.
EDGE_BATCH = 5000

#: Labels that look like axis classes. Only used to flag classes typed since
#: :data:`AXIS_CLASSES` was last reviewed; the list, not this pattern, decides.
AXIS_LABEL_PATTERN = re.compile(
    r"^(adult |larval )?(cholinergic|GABAergic|glutamatergic|dopaminergic|"
    r"histaminergic|octopaminergic|peptidergic|serotonergic|tyraminergic) neuron$"
    r"|^(adult )?\w+ergic and \w+ergic neuron$"
    r"|^GABA-\w+ neuron$"
    r"|(hemi)?lineage( primary| secondary)? neuron$"
    r"|^(hemi)?lineage \S+ (primary |secondary )?(inter|motor )?neuron$"
    r"|^(primary|secondary) (inter|motor )?neuron$"
    r"|expressing neuron$"
)

# Assignment status of a neuron.
ASSIGNED = "assigned"
NO_LEAF = "no_leaf"          # typed only to classes subtyped elsewhere in the dataset
MULTI_LEAF = "multi_leaf"    # more than one leaf type
ONLY_AXIS = "only_axis"      # no type other than axis classes
UNTYPED = "untyped"          # no type at all


# ---------------------------------------------------------------------------
# Pure logic (no network)
# ---------------------------------------------------------------------------

def assign_classes(neuron_types, ancestors, axis=AXIS_CLASSES):
    """Give each neuron its single leaf type in this dataset.

    :param neuron_types: ``{neuron_id: iterable of direct class ids}`` for one
        dataset.
    :param ancestors: ``{class_id: set of all superclass ids}``; classes absent
        from it are treated as having no superclasses.
    :param axis: class ids to ignore (see :mod:`vfbquery.circuit_axis_classes`).
    :return: ``(assignment, status, leaves)`` — ``{neuron: class}`` for
        assigned neurons, ``{neuron: (status, sorted candidate classes)}`` for
        every neuron, and the dataset's set of leaf classes.
    """
    typed = {n: set(cs) - set(axis) for n, cs in neuron_types.items()}
    used = set().union(*typed.values()) if typed else set()
    parents = {a for c in used for a in ancestors.get(c, ())} & used
    leaves = used - parents

    assignment, status = {}, {}
    for n, cs in neuron_types.items():
        cs = set(cs)
        kept = typed[n]
        own = sorted(kept & leaves)
        if len(own) == 1:
            assignment[n] = own[0]
            status[n] = (ASSIGNED, own)
        elif own:
            status[n] = (MULTI_LEAF, own)
        elif kept:
            # Report the most specific of the neuron's (non-leaf) types.
            spec = sorted(c for c in kept
                          if not any(d != c and c in ancestors.get(d, ()) for d in kept))
            status[n] = (NO_LEAF, spec)
        elif cs:
            status[n] = (ONLY_AXIS, sorted(cs))
        else:
            status[n] = (UNTYPED, [])
    return assignment, status, leaves


def aggregate_class_edges(edges, assignment, total_up, total_down):
    """Sum neuron edges into class edges with input and output proportions.

    :param edges: iterable of ``(source neuron, target neuron, synapses)``.
    :param assignment: ``{neuron: class}``; edges touching an unassigned neuron
        are skipped.
    :param total_up: ``{neuron: total input synapses}``.
    :param total_down: ``{neuron: total output synapses}``; may be partial.
    :return: ``{(class A, class B): {"synapses", "pairs", "inprop_in",
        "inprop_out"}}`` — see the module docstring for the definitions.
    """
    size = collections.Counter(assignment.values())
    # Which classes have an output total for every member: only those get
    # inprop_out, or the mean would silently be over a subset.
    has_down = collections.defaultdict(lambda: True)
    for n, c in assignment.items():
        if not total_down.get(n):
            has_down[c] = False

    acc = {}
    skipped_no_total = 0
    for a, b, w in edges:
        ca, cb = assignment.get(a), assignment.get(b)
        if ca is None or cb is None:
            continue
        up = total_up.get(b)
        if not up:
            skipped_no_total += 1
            continue
        e = acc.get((ca, cb))
        if e is None:
            e = acc[(ca, cb)] = [0, 0, 0.0, 0.0]
        e[0] += w
        e[1] += 1
        e[2] += w / up
        down = total_down.get(a)
        if down:
            e[3] += w / down

    out = {}
    for (ca, cb), (syn, pairs, sum_in, sum_out) in acc.items():
        out[(ca, cb)] = {
            "synapses": syn,
            "pairs": pairs,
            "inprop_in": sum_in / size[cb],
            "inprop_out": sum_out / size[ca] if has_down[ca] else None,
        }
    if skipped_no_total:
        print(f"Warning: {skipped_no_total} edges skipped: target has no total_upstream")
    return out


def unlisted_axis_candidates(labels, axis=AXIS_CLASSES):
    """Classes whose labels look like axis classes but are not in the list."""
    return sorted(c for c, l in labels.items()
                  if c not in axis and l and AXIS_LABEL_PATTERN.search(l))


# ---------------------------------------------------------------------------
# PDB access
# ---------------------------------------------------------------------------

def _query(nc, cypher):
    results = nc.commit_list([cypher])
    if results is False:
        raise RuntimeError("Neo4j query failed:\n" + cypher[:500])
    return dict_cursor(results)


def fetch_neurons(nc, site):
    """Direct types and synapse totals of every connectome neuron in a dataset."""
    rows = _query(nc, f"""
        MATCH (:Connectome {{short_form: {json.dumps(site)}}})
              <-[:database_cross_reference]-(n:Neuron:has_neuron_connectivity)
        OPTIONAL MATCH (n)-[:INSTANCEOF]->(c:Class)
        RETURN n.short_form AS n, n.total_upstream[0] AS up,
               n.total_downstream[0] AS down, collect(c.short_form) AS types""")
    types = {r["n"]: r["types"] for r in rows}
    up = {r["n"]: r["up"] for r in rows if r["up"]}
    down = {r["n"]: r["down"] for r in rows if r["down"]}
    return types, up, down


def fetch_classes(nc, class_ids):
    """Label, symbol and all superclasses of each class."""
    rows = _query(nc, f"""
        UNWIND {json.dumps(sorted(class_ids))} AS id
        MATCH (c:Class {{short_form: id}})
        OPTIONAL MATCH (c)-[:SUBCLASSOF*1..]->(a:Class)
        RETURN c.short_form AS id, c.label AS label,
               coalesce(c.symbol[0], '') AS symbol,
               collect(DISTINCT a.short_form) AS ancestors""")
    return ({r["id"]: r["label"] for r in rows},
            {r["id"]: r["symbol"] for r in rows},
            {r["id"]: set(r["ancestors"]) for r in rows})


def fetch_edges(nc, neuron_ids, batch=EDGE_BATCH):
    """Yield ``(source, target, synapses)`` for edges out of ``neuron_ids``."""
    ids = sorted(neuron_ids)
    for i in range(0, len(ids), batch):
        chunk = json.dumps(ids[i:i + batch])
        for r in _query(nc, f"""
                MATCH (a:Neuron) WHERE a.short_form IN {chunk}
                MATCH (a)-[e:synapsed_to]->(b:Neuron)
                RETURN a.short_form AS a, b.short_form AS b, e.weight[0] AS w"""):
            yield r["a"], r["b"], r["w"]




def fetch_connectomes(nc):
    """Every connectome dataset in the PDB: ``{short_form: {label, symbol}}``."""
    return {r["c"]: {"label": r["label"] or "", "symbol": r["symbol"] or ""}
            for r in _query(nc, """
                MATCH (c:Connectome)
                RETURN c.short_form AS c, c.label AS label, c.symbol[0] AS symbol
                ORDER BY c""")}


# ---------------------------------------------------------------------------
# Output files
#
# Layout (agreed in #114), one folder per run:
#
#   <out>/manifest.json                  written last; no manifest = incomplete
#   <out>/<connectome>/neuron_edges.tsv.gz
#   <out>/<connectome>/class_edges.tsv.gz
#   <out>/<connectome>/neuron_classes.tsv.gz
#   <out>/<connectome>/classes.tsv.gz
#   <out>/<connectome>/report.tsv
#   <out>/<connectome>/summary.md
#
# <connectome> is the Connectome short_form, the same key as the cb_<key> GDS
# graphs. Each TSV starts with '#' lines (title, connectome, run, build
# details, column descriptions), then a header row.
# ---------------------------------------------------------------------------

MANIFEST = "manifest.json"
FORMAT_VERSION = 1

#: name -> (title, [(column, description)])
TABLES = {
    "neuron_edges.tsv.gz": (
        "Neuron-to-neuron connections (synapsed_to edges between neurons of this dataset)",
        [("source", "presynaptic neuron (VFB id)"),
         ("target", "postsynaptic neuron (VFB id)"),
         ("synapses", "synapse count"),
         ("inprop_in", "synapses / target's total input synapses; blank if the target has no total"),
         ("inprop_out", "synapses / source's total output synapses; blank if the source has no total")]),
    "class_edges.tsv.gz": (
        "Class-to-class connections between the leaf classes in classes.tsv.gz",
        [("source", "presynaptic class (FBbt id)"),
         ("target", "postsynaptic class (FBbt id)"),
         ("synapses", "total synapses from source-class neurons to target-class neurons"),
         ("pairs", "connected neuron pairs"),
         ("inprop_in", "mean over all target-class neurons of the share of their input that comes from the source class"),
         ("inprop_out", "mean over all source-class neurons of the share of their output that goes to the target class; "
                        "blank if any source-class neuron has no output total")]),
    "neuron_classes.tsv.gz": (
        "The single leaf class assigned to each neuron (neurons left out are in report.tsv)",
        [("neuron", "neuron (VFB id)"),
         ("class", "assigned leaf class (FBbt id)")]),
    "classes.tsv.gz": (
        "Class nodes: the leaf classes with at least one assigned neuron",
        [("class", "class (FBbt id)"),
         ("label", "class label"),
         ("symbol", "class symbol, if any"),
         ("neurons", "number of assigned neurons"),
         ("ancestors", "all superclasses (FBbt ids, '|'-separated), for expanding broad query terms")]),
    "report.tsv": (
        "Neurons left out of the class graph, and why",
        [("neuron", "neuron (VFB id)"),
         ("status", f"{NO_LEAF}: typed only to classes subtyped elsewhere in the dataset; "
                    f"{MULTI_LEAF}: more than one leaf type; {ONLY_AXIS}: only axis classes; "
                    f"{UNTYPED}: no type"),
         ("types", "the neuron's most specific types (FBbt ids, '|'-separated)"),
         ("labels", "their labels ('|'-separated)")]),
}


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class _Table:
    """A TSV with '#' metadata lines and a header row; gzipped if named .gz.

    Gzip files are written with a fixed timestamp, so the same content always
    has the same sha256.
    """

    def __init__(self, folder, name, meta):
        title, columns = TABLES[name]
        self.path = os.path.join(folder, name)
        self.name, self.rows = name, 0
        if name.endswith(".gz"):
            raw = gzip.GzipFile(self.path, "wb", mtime=0)
            self._f = io.TextIOWrapper(raw, encoding="utf-8", newline="")
        else:
            self._f = open(self.path, "w", encoding="utf-8", newline="")
        lines = [title] + [f"{k}: {v}" for k, v in meta.items()] + ["columns:"]
        lines += [f"  {c}: {d}" for c, d in columns]
        self._f.writelines(f"# {line}\n" for line in lines)
        self._w = csv.writer(self._f, delimiter="\t", lineterminator="\n")
        self._w.writerow([c for c, _ in columns])

    def row(self, *values):
        self._w.writerow(values)
        self.rows += 1

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._f.close()

    def entry(self):
        return {"rows": self.rows, "sha256": _sha256(self.path)}


def read_table(path):
    """Read a table written here: returns (metadata lines, header, rows)."""
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", newline="") as f:
        meta, rows = [], []
        for line in f:
            if not line.startswith("#"):
                header = line.rstrip("\n").split("\t")
                break
            meta.append(line[2:].rstrip("\n"))
        rows = [r for r in csv.reader(f, delimiter="\t")]
    return meta, header, rows


def _num(x):
    return "" if x is None else f"{x:.6g}"


# ---------------------------------------------------------------------------
# Build and write
# ---------------------------------------------------------------------------

def write_site(folder, meta, types, up, down, labels, symbols, ancestors, edges, log=print):
    """Assign classes and write one connectome's files into ``folder``.

    ``edges`` is an iterable of ``(source, target, synapses)``; it is streamed
    into neuron_edges.tsv.gz while the class edges are aggregated, so the
    neuron edges are never all held in memory. Edges to or from neurons not
    in ``types`` (i.e. outside this dataset) are skipped.

    Returns ``(graph, manifest entry)``; ``graph`` is what :func:`report` takes.
    """
    os.makedirs(folder, exist_ok=True)
    assignment, status, leaves = assign_classes(types, ancestors)
    files, skipped = {}, [0]

    with _Table(folder, "neuron_edges.tsv.gz", meta) as t:
        def kept():
            for a, b, w in edges:
                if a not in types or b not in types:
                    skipped[0] += 1
                    continue
                t.row(a, b, w, _num(w / up[b] if up.get(b) else None),
                      _num(w / down[a] if down.get(a) else None))
                yield a, b, w
        class_edges = aggregate_class_edges(kept(), assignment, up, down)
    files[t.name] = t.entry()
    if skipped[0]:
        log(f"{meta['connectome']}: skipped {skipped[0]:,} edges to neurons outside the dataset")

    with _Table(folder, "class_edges.tsv.gz", meta) as t:
        for (a, b), e in sorted(class_edges.items()):
            t.row(a, b, e["synapses"], e["pairs"], _num(e["inprop_in"]), _num(e["inprop_out"]))
    files[t.name] = t.entry()

    with _Table(folder, "neuron_classes.tsv.gz", meta) as t:
        for n, c in sorted(assignment.items()):
            t.row(n, c)
    files[t.name] = t.entry()

    size = collections.Counter(assignment.values())
    with _Table(folder, "classes.tsv.gz", meta) as t:
        for c in sorted(size):
            t.row(c, labels.get(c, ""), symbols.get(c, ""), size[c],
                  "|".join(sorted(ancestors.get(c, ()))))
    files[t.name] = t.entry()

    with _Table(folder, "report.tsv", meta) as t:
        for n, (st, cands) in sorted(status.items()):
            if st != ASSIGNED:
                t.row(n, st, "|".join(cands), "|".join(labels.get(c, c) for c in cands))
    files[t.name] = t.entry()

    g = {"site": meta["connectome"], "endpoint": meta.get("endpoint", ""),
         "built": meta.get("built", ""), "types": types, "up": up, "down": down,
         "labels": labels, "symbols": symbols, "ancestors": ancestors,
         "assignment": assignment, "status": status, "leaves": leaves,
         "edges": class_edges}
    with open(os.path.join(folder, "summary.md"), "w", encoding="utf-8") as f:
        f.write(report(g))

    entry = {
        "neurons": len(types),
        "assigned": len(assignment),
        "classes": len(size),
        "neuron_edges": files["neuron_edges.tsv.gz"]["rows"],
        "class_edges": len(class_edges),
        "files": {f"{meta['connectome']}/{k}": v for k, v in files.items()},
    }
    return g, entry


def build_site(nc, site, out_dir, meta, log=print):
    """Fetch one connectome from the PDB and write its files."""
    t0 = time.time()
    types, up, down = fetch_neurons(nc, site)
    log(f"{site}: {len(types):,} neurons ({time.time() - t0:.0f}s)")
    class_ids = {c for cs in types.values() for c in cs}
    labels, symbols, ancestors = fetch_classes(nc, class_ids)
    log(f"{site}: {len(class_ids):,} classes ({time.time() - t0:.0f}s)")
    meta = dict(meta, connectome=site)
    g, entry = write_site(os.path.join(out_dir, site), meta, types, up, down,
                          labels, symbols, ancestors, fetch_edges(nc, types), log)
    log(f"{site}: {entry['neuron_edges']:,} neuron edges, {entry['class_edges']:,} class edges "
        f"({time.time() - t0:.0f}s)")
    return entry


def write_manifest(out_dir, run, meta, datasets):
    """Write manifest.json last, atomically (temporary file, then rename)."""
    manifest = {"format": FORMAT_VERSION, "run": run, **meta, "datasets": datasets}
    tmp = os.path.join(out_dir, MANIFEST + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, os.path.join(out_dir, MANIFEST))
    return manifest


def build(run, out_dir, sites=None, endpoint=ANALYTICS_ENDPOINT, log=print,
          usr="neo4j", pwd="vfb"):
    """Build every connectome (or ``sites``) into ``out_dir`` and write the manifest.

    Any existing manifest is removed first, so the folder reads as incomplete
    until the whole build has finished. ``usr``/``pwd`` default to the public
    read-only login; a pipeline database needs its own.
    """
    os.makedirs(out_dir, exist_ok=True)
    for stale in (MANIFEST, MANIFEST + ".tmp"):
        if os.path.exists(os.path.join(out_dir, stale)):
            os.remove(os.path.join(out_dir, stale))
    nc = Neo4jConnect(endpoint, usr=usr, pwd=pwd, read_timeout=600)
    known = fetch_connectomes(nc)
    unknown = [s for s in sites or () if s not in known]
    if unknown:
        raise ValueError(f"not a Connectome short_form: {', '.join(unknown)}")
    sites = sites or sorted(known)
    meta = {"built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "endpoint": endpoint, "builder": f"vfbquery {__version__}"}
    datasets = {}
    for site in sites:
        datasets[site] = dict(known[site], **build_site(nc, site, out_dir, dict(meta, run=run), log))
    return write_manifest(out_dir, run, meta, datasets)


def _name(g, c):
    s = g["symbols"].get(c)
    return f"{g['labels'].get(c, c)}" + (f" [{s}]" if s else "")


def report(g, top=25):
    """Markdown summary: counts, left-out neurons by reason, conflicts."""
    site, status = g["site"], g["status"]
    n = len(status)
    by_status = collections.Counter(st for st, _ in status.values())
    size = collections.Counter(g["assignment"].values())
    inprops = sorted(e["inprop_in"] for e in g["edges"].values())
    L = [f"# Class graph: {site}", "",
         f"Built {g['built']} from {g['endpoint']}.", "",
         "| | |", "|---|---|",
         f"| Neurons | {n:,} |"]
    for st in (ASSIGNED, NO_LEAF, MULTI_LEAF, ONLY_AXIS, UNTYPED):
        L.append(f"| {st} | {by_status[st]:,} ({100 * by_status[st] / max(n, 1):.1f}%) |")
    L += [f"| Classes (nodes) | {len(size):,} |",
          f"| Class edges | {len(g['edges']):,} |"]
    if inprops:
        L.append(f"| Median edge inprop_in | {inprops[len(inprops) // 2]:.4f} |")
    no_up = sum(1 for x in g["assignment"] if x not in g["up"])
    no_down = sum(1 for x in g["assignment"] if x not in g["down"])
    L += [f"| Assigned neurons without total_upstream | {no_up:,} |",
          f"| Assigned neurons without total_downstream | {no_down:,} |", ""]

    noleaf = collections.Counter()
    for st, cands in status.values():
        if st == NO_LEAF:
            for c in cands:
                noleaf[c] += 1
    subtyped = {c: sorted((d for d in size if c in g["ancestors"].get(d, ())),
                          key=lambda d: -size[d]) for c in noleaf}
    L += ["## Neurons with no leaf type", "",
          "Counted under each of their most specific types; a neuron with two such types is counted twice.", "",
          "| Neurons | Class | Typed subclasses in dataset | e.g. |", "|---|---|---|---|"]
    for c, k in noleaf.most_common(top):
        sub = subtyped[c]
        L.append(f"| {k:,} | {_name(g, c)} ({c}) | {len(sub)} | "
                 + ", ".join(_name(g, d) for d in sub[:3]) + " |")
    if len(noleaf) > top:
        L.append(f"| … | {len(noleaf) - top} more classes | | |")

    multi = collections.Counter(tuple(c) for st, c in status.values() if st == MULTI_LEAF)
    L += ["", "## Neurons with more than one leaf type", "",
          "| Neurons | Leaf types |", "|---|---|"]
    for combo, k in multi.most_common(top):
        L.append(f"| {k:,} | " + " + ".join(f"{_name(g, c)} ({c})" for c in combo) + " |")
    if len(multi) > top:
        L.append(f"| … | {len(multi) - top} more combinations |")

    axis_only = collections.Counter(c for st, cs in status.values() if st == ONLY_AXIS for c in cs)
    L += ["", "## Neurons typed only to axis classes", "",
          "| Neurons | Axis class |", "|---|---|"]
    for c, k in axis_only.most_common(10):
        L.append(f"| {k:,} | {_name(g, c)} ({c}) |")

    cands = unlisted_axis_candidates(g["labels"])
    L += ["", "## Possible axis classes not in circuit_axis_classes.py", ""]
    L += [f"- {_name(g, c)} ({c})" for c in cands] or ["None."]
    return "\n".join(L) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--run", required=True,
                   help="Pipeline run (or release) the PDB was loaded from; recorded in every file")
    p.add_argument("--out", required=True,
                   help="Output folder, e.g. pipeline-out/<run>/circuit")
    p.add_argument("--endpoint", default=ANALYTICS_ENDPOINT, help="Neo4j endpoint to read from")
    p.add_argument("--user", default=os.getenv("NEO4J_USER", "neo4j"),
                   help="Neo4j user (default: $NEO4J_USER, else neo4j). The password is read "
                        "from $NEO4J_PASSWORD (default: the public vfb), never from the command line")
    p.add_argument("sites", nargs="*",
                   help="Connectome short_forms (default: every Connectome in the PDB)")
    a = p.parse_args(argv)
    m = build(a.run, a.out, a.sites, a.endpoint, usr=a.user,
              pwd=os.getenv("NEO4J_PASSWORD", "vfb"))
    print(f"{len(m['datasets'])} connectomes written to {a.out}")


if __name__ == "__main__":
    main()
