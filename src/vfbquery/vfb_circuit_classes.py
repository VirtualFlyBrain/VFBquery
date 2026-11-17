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

Heavy queries: run the build against pdb-analytics, not the serving pdb.
"""
import argparse
import collections
import csv
import gzip
import json
import os
import re
import time

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


# ---------------------------------------------------------------------------
# Build and write
# ---------------------------------------------------------------------------

def build(site, endpoint=ANALYTICS_ENDPOINT, log=print):
    """Build one dataset's class graph. Returns a dict of everything written."""
    t0 = time.time()
    nc = Neo4jConnect(endpoint, read_timeout=600)
    types, up, down = fetch_neurons(nc, site)
    log(f"{site}: {len(types):,} neurons ({time.time() - t0:.0f}s)")
    class_ids = {c for cs in types.values() for c in cs}
    labels, symbols, ancestors = fetch_classes(nc, class_ids)
    log(f"{site}: {len(class_ids):,} classes ({time.time() - t0:.0f}s)")

    assignment, status, leaves = assign_classes(types, ancestors)
    edges = aggregate_class_edges(fetch_edges(nc, assignment), assignment, up, down)
    log(f"{site}: {len(edges):,} class edges ({time.time() - t0:.0f}s)")
    return {
        "site": site, "endpoint": endpoint,
        "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "types": types, "up": up, "down": down,
        "labels": labels, "symbols": symbols, "ancestors": ancestors,
        "assignment": assignment, "status": status, "leaves": leaves,
        "edges": edges,
    }


def _name(g, c):
    s = g["symbols"].get(c)
    return f"{g['labels'].get(c, c)}" + (f" [{s}]" if s else "")


def write(g, out_dir):
    """Write classes, class edges, neuron assignments and a Markdown report."""
    os.makedirs(out_dir, exist_ok=True)
    site = g["site"]
    size = collections.Counter(g["assignment"].values())

    with gzip.open(os.path.join(out_dir, f"{site}_classes.tsv.gz"), "wt", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["class", "label", "symbol", "neurons"])
        for c in sorted(size):
            w.writerow([c, g["labels"].get(c, ""), g["symbols"].get(c, ""), size[c]])

    with gzip.open(os.path.join(out_dir, f"{site}_class_edges.tsv.gz"), "wt", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["source", "target", "synapses", "pairs", "inprop_in", "inprop_out"])
        for (a, b), e in sorted(g["edges"].items()):
            w.writerow([a, b, e["synapses"], e["pairs"], f"{e['inprop_in']:.6g}",
                        "" if e["inprop_out"] is None else f"{e['inprop_out']:.6g}"])

    with gzip.open(os.path.join(out_dir, f"{site}_neurons.tsv.gz"), "wt", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["neuron", "status", "class", "candidates"])
        for n, (st, cands) in sorted(g["status"].items()):
            w.writerow([n, st, g["assignment"].get(n, ""), "|".join(cands)])

    with open(os.path.join(out_dir, f"{site}_report.md"), "w") as f:
        f.write(report(g))


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
    p.add_argument("sites", nargs="+", help="Connectome short_form, e.g. catmaid_l1em flywire783")
    p.add_argument("--endpoint", default=ANALYTICS_ENDPOINT)
    p.add_argument("--out", default="class_graphs")
    a = p.parse_args(argv)
    for site in a.sites:
        g = build(site, a.endpoint)
        write(g, a.out)
        print(f"{site}: written to {a.out}")


if __name__ == "__main__":
    main()
