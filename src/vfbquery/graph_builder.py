"""Build basic_graph JSON representations from VFBquery connectivity results.

Produces a graph format compatible with VFBchat's BasicGraphView component.
Node labels use the defined ``symbol`` field; the full ``label`` is available
in ``full_label`` for tooltip/hover display.

Graph generation is a pure post-processing step — it never modifies query
results and is completely independent of caching layers.
"""

import re
from .neo4j_client import Neo4jConnect, dict_cursor

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_NODES = 80
MAX_EDGES = 200
GRAPH_VERSION = 1

# Neurotransmitter group colours (matching VFBchat conventions)
NT_COLORS = {
    "cholinergic":    "#4a9eff",
    "GABAergic":      "#f87171",
    "glutamatergic":  "#4ade80",
    "dopaminergic":   "#f59e0b",
    "serotonergic":   "#a78bfa",
    "octopaminergic": "#22d3ee",
    "tyraminergic":   "#f472b6",
    "histaminergic":  "#fb923c",
}

# Sensory-system group colours
SYSTEM_COLORS = {
    "visual":          "#34d399",
    "olfactory":       "#e879f9",
    "auditory":        "#67e8f9",
    "mechanosensory":  "#fde047",
    "gustatory":       "#f97316",
}

# Fallback palette for groups that don't match known keywords
_PALETTE = [
    "#4a9eff", "#4ade80", "#f59e0b", "#f472b6",
    "#22d3ee", "#a78bfa", "#f87171", "#34d399",
    "#e879f9", "#fb923c", "#67e8f9", "#fde047",
]

# Brain-region keywords for fallback grouping
_REGION_KEYWORDS = [
    "medulla", "lobula", "lamina", "mushroom body", "kenyon",
    "ellipsoid body", "fan-shaped body", "protocerebral bridge",
    "noduli", "central complex", "antennal lobe", "lateral horn",
    "subesophageal", "optic lobe", "central brain",
]

# ---------------------------------------------------------------------------
# Neo4j batch enrichment
# ---------------------------------------------------------------------------

def batch_lookup_ids(ids):
    """Fetch label, symbol, and uniqueFacets for a list of VFB IDs.

    Uses a single Neo4j Cypher query.  Falls back gracefully on error,
    returning an empty dict so callers can use the IDs directly.

    :param ids: list of short_form IDs (e.g. ``["FBbt_00003686", ...]``)
    :return: ``{id: {"label": str, "symbol": str, "tags": list[str]}}``
    """
    if not ids:
        return {}
    # Deduplicate
    unique_ids = list(set(ids))
    try:
        nc = Neo4jConnect()
        id_list = str(unique_ids)
        cypher = (
            f"MATCH (n) WHERE n.short_form IN {id_list} "
            "RETURN n.short_form AS id, n.label AS label, "
            "coalesce(n.symbol[0], '') AS symbol, "
            "coalesce(n.uniqueFacets, []) AS tags"
        )
        results = nc.commit_list([cypher])
        if not results:
            return {}
        rows = dict_cursor(results)
        return {
            r["id"]: {
                "label": r.get("label") or r["id"],
                "symbol": r.get("symbol") or "",
                "tags": r.get("tags") or [],
            }
            for r in rows
        }
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Group assignment
# ---------------------------------------------------------------------------

def assign_group(tags=None, label=""):
    """Determine a semantic group from *tags* (uniqueFacets) or *label*.

    Priority: neurotransmitter > sensory system > brain region > "other".
    """
    search_text = ""
    if tags:
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split("|") if t.strip()]
        search_text = " ".join(tags).lower()
    label_lower = label.lower() if label else ""

    # 1. Neurotransmitter
    for nt in NT_COLORS:
        if nt.lower() in search_text or nt.lower() in label_lower:
            return nt

    # 2. Sensory system
    for sys_name in SYSTEM_COLORS:
        if sys_name in search_text or sys_name in label_lower:
            return sys_name

    # 3. Brain region
    for region in _REGION_KEYWORDS:
        if region in search_text or region in label_lower:
            return region

    return "other"


def _node_display_label(info):
    """Pick the best short display label from a lookup result.

    Prefers ``symbol`` (the defined short name); falls back to ``label``.
    """
    if info.get("symbol"):
        return info["symbol"]
    return info.get("label") or ""


# ---------------------------------------------------------------------------
# Core graph builder
# ---------------------------------------------------------------------------

def build_graph(nodes, edges, title=None, directed=True, layout="force"):
    """Assemble a ``basic_graph`` dict, deduplicating and truncating.

    :param nodes: list of node dicts ``{id, label, full_label, group, ...}``
    :param edges: list of edge dicts ``{source, target, weight, ...}``
    :param title: optional graph title
    :param directed: whether edges are directed (default ``True``)
    :param layout: layout hint (default ``"force"``)
    :return: complete ``basic_graph`` dict
    """
    # Deduplicate nodes by id
    seen = set()
    deduped_nodes = []
    for n in nodes:
        if n["id"] not in seen:
            seen.add(n["id"])
            deduped_nodes.append(n)

    # Track original counts for clipping notification
    orig_node_count = len(deduped_nodes)
    orig_edge_count = len(edges)

    # Truncate edges — keep highest weight first
    if len(edges) > MAX_EDGES:
        edges = sorted(edges, key=lambda e: e.get("weight") or 0, reverse=True)[:MAX_EDGES]

    # Truncate nodes — keep those with highest degree
    if len(deduped_nodes) > MAX_NODES:
        degree = {}
        for e in edges:
            degree[e["source"]] = degree.get(e["source"], 0) + 1
            degree[e["target"]] = degree.get(e["target"], 0) + 1
        deduped_nodes.sort(key=lambda n: degree.get(n["id"], 0), reverse=True)
        deduped_nodes = deduped_nodes[:MAX_NODES]
        # Remove edges referencing dropped nodes
        kept_ids = {n["id"] for n in deduped_nodes}
        edges = [e for e in edges if e["source"] in kept_ids and e["target"] in kept_ids]

    # Auto-assign colours to groups
    groups = list(dict.fromkeys(n.get("group", "other") for n in deduped_nodes))
    group_color = {}
    for g in groups:
        if g in NT_COLORS:
            group_color[g] = NT_COLORS[g]
        elif g in SYSTEM_COLORS:
            group_color[g] = SYSTEM_COLORS[g]
        else:
            idx = len(group_color) % len(_PALETTE)
            group_color[g] = _PALETTE[idx]

    for n in deduped_nodes:
        if not n.get("color"):
            n["color"] = group_color.get(n.get("group", "other"), _PALETTE[0])

    graph = {
        "type": "basic_graph",
        "version": GRAPH_VERSION,
        "title": title,
        "directed": directed,
        "layout": layout,
        "nodes": deduped_nodes,
        "edges": edges,
    }

    # Clipping notification — only present when data was truncated
    if orig_node_count > len(deduped_nodes) or orig_edge_count > len(edges):
        graph["clipped"] = {
            "nodes_total": orig_node_count,
            "nodes_included": len(deduped_nodes),
            "edges_total": orig_edge_count,
            "edges_included": len(edges),
        }

    return graph


# ---------------------------------------------------------------------------
# Converter: query_connectivity()
# ---------------------------------------------------------------------------

def graph_from_query_connectivity(connections, group_by_class,
                                  upstream_type=None, downstream_type=None):
    """Build graph from ``query_connectivity()`` result connections.

    :param connections: list of connection dicts
    :param group_by_class: whether results are class-aggregated
    :param upstream_type: upstream type label (for title)
    :param downstream_type: downstream type label (for title)
    """
    if not connections:
        return None

    # Collect all IDs for batch enrichment
    all_ids = set()
    if group_by_class:
        for c in connections:
            all_ids.add(c.get("upstream_class_id", ""))
            all_ids.add(c.get("downstream_class_id", ""))
    else:
        for c in connections:
            # Per-neuron: class IDs may be pipe-separated
            for cid in (c.get("upstream_class_id") or "").split("|"):
                if cid:
                    all_ids.add(cid)
            for cid in (c.get("downstream_class_id") or "").split("|"):
                if cid:
                    all_ids.add(cid)
            if c.get("upstream_neuron_id"):
                all_ids.add(c["upstream_neuron_id"])
            if c.get("downstream_neuron_id"):
                all_ids.add(c["downstream_neuron_id"])

    all_ids.discard("")
    lookup = batch_lookup_ids(list(all_ids))

    nodes = {}
    edges = []

    if group_by_class:
        for c in connections:
            up_id = c.get("upstream_class_id", "")
            dn_id = c.get("downstream_class_id", "")
            up_info = lookup.get(up_id, {"label": c.get("upstream_class", up_id), "symbol": "", "tags": []})
            dn_info = lookup.get(dn_id, {"label": c.get("downstream_class", dn_id), "symbol": "", "tags": []})

            if up_id and up_id not in nodes:
                nodes[up_id] = {
                    "id": up_id,
                    "label": _node_display_label(up_info) or c.get("upstream_class", up_id),
                    "full_label": up_info.get("label") or c.get("upstream_class", up_id),
                    "group": assign_group(up_info.get("tags"), up_info.get("label", "")),
                }
            if dn_id and dn_id not in nodes:
                nodes[dn_id] = {
                    "id": dn_id,
                    "label": _node_display_label(dn_info) or c.get("downstream_class", dn_id),
                    "full_label": dn_info.get("label") or c.get("downstream_class", dn_id),
                    "group": assign_group(dn_info.get("tags"), dn_info.get("label", "")),
                }
            if up_id and dn_id:
                edges.append({
                    "source": up_id,
                    "target": dn_id,
                    "weight": c.get("total_weight", 0),
                })
    else:
        # Per-neuron results
        for c in connections:
            up_nid = c.get("upstream_neuron_id", "")
            dn_nid = c.get("downstream_neuron_id", "")
            # Use class info for grouping
            up_class_id = (c.get("upstream_class_id") or "").split("|")[0]
            dn_class_id = (c.get("downstream_class_id") or "").split("|")[0]
            up_class_info = lookup.get(up_class_id, {"label": c.get("upstream_class", ""), "symbol": "", "tags": []})
            dn_class_info = lookup.get(dn_class_id, {"label": c.get("downstream_class", ""), "symbol": "", "tags": []})

            if up_nid and up_nid not in nodes:
                up_info = lookup.get(up_nid, {"label": c.get("upstream_neuron_name", up_nid), "symbol": "", "tags": []})
                nodes[up_nid] = {
                    "id": up_nid,
                    "label": _node_display_label(up_info) or c.get("upstream_neuron_name", up_nid),
                    "full_label": up_info.get("label") or c.get("upstream_neuron_name", up_nid),
                    "group": assign_group(up_class_info.get("tags"), up_class_info.get("label", "")),
                }
            if dn_nid and dn_nid not in nodes:
                dn_info = lookup.get(dn_nid, {"label": c.get("downstream_neuron_name", dn_nid), "symbol": "", "tags": []})
                nodes[dn_nid] = {
                    "id": dn_nid,
                    "label": _node_display_label(dn_info) or c.get("downstream_neuron_name", dn_nid),
                    "full_label": dn_info.get("label") or c.get("downstream_neuron_name", dn_nid),
                    "group": assign_group(dn_class_info.get("tags"), dn_class_info.get("label", "")),
                }
            if up_nid and dn_nid:
                edges.append({
                    "source": up_nid,
                    "target": dn_nid,
                    "weight": c.get("weight", 0),
                })

    up_label = upstream_type or "*"
    dn_label = downstream_type or "*"
    title = f"Connectivity: {up_label} \u2192 {dn_label}"

    return build_graph(list(nodes.values()), edges, title=title, directed=True)


# ---------------------------------------------------------------------------
# Converter: get_neuron_neuron_connectivity()
# ---------------------------------------------------------------------------

def graph_from_neuron_neuron(rows, primary_id, primary_label=None):
    """Build graph from ``get_neuron_neuron_connectivity()`` result rows.

    :param rows: list of row dicts with id, label, outputs, inputs, tags
    :param primary_id: short_form of the query neuron
    :param primary_label: fallback label (enrichment will override)
    """
    if not rows:
        return None

    # Batch lookup all IDs
    all_ids = [primary_id] + [r["id"] for r in rows if r.get("id")]
    lookup = batch_lookup_ids(all_ids)

    primary_info = lookup.get(primary_id, {
        "label": primary_label or primary_id,
        "symbol": "",
        "tags": [],
    })

    nodes = [{
        "id": primary_id,
        "label": _node_display_label(primary_info) or primary_label or primary_id,
        "full_label": primary_info.get("label") or primary_label or primary_id,
        "group": assign_group(primary_info.get("tags")),
        "size": 2,
    }]
    edges = []

    for r in rows:
        rid = r.get("id", "")
        if not rid:
            continue
        info = lookup.get(rid, {"label": r.get("label", rid), "symbol": "", "tags": []})
        # Parse tags — may be pipe-separated string or list
        row_tags = r.get("tags")
        if isinstance(row_tags, str):
            row_tags = [t.strip() for t in row_tags.split("|") if t.strip()]
        # Prefer enriched tags, fall back to row tags
        tags_for_group = info.get("tags") or row_tags or []

        nodes.append({
            "id": rid,
            "label": _node_display_label(info) or r.get("label", rid),
            "full_label": info.get("label") or r.get("label", rid),
            "group": assign_group(tags_for_group),
        })

        outputs = r.get("outputs", 0) or 0
        inputs = r.get("inputs", 0) or 0
        if outputs > 0:
            edges.append({
                "source": primary_id,
                "target": rid,
                "weight": outputs,
                "label": "output",
            })
        if inputs > 0:
            edges.append({
                "source": rid,
                "target": primary_id,
                "weight": inputs,
                "label": "input",
            })

    disp = _node_display_label(primary_info) or primary_label or primary_id
    return build_graph(nodes, edges, title=f"Connections of {disp}", directed=True)


# ---------------------------------------------------------------------------
# Converter: get_neuron_region_connectivity()
# ---------------------------------------------------------------------------

def graph_from_neuron_region(rows, primary_id, primary_label=None):
    """Build graph from ``get_neuron_region_connectivity()`` result rows.

    :param rows: list of row dicts with id, region, presynaptic_terminals,
                 postsynaptic_terminals, tags
    :param primary_id: short_form of the query neuron
    :param primary_label: fallback label
    """
    if not rows:
        return None

    all_ids = [primary_id] + [r["id"] for r in rows if r.get("id")]
    lookup = batch_lookup_ids(all_ids)

    primary_info = lookup.get(primary_id, {
        "label": primary_label or primary_id,
        "symbol": "",
        "tags": [],
    })

    nodes = [{
        "id": primary_id,
        "label": _node_display_label(primary_info) or primary_label or primary_id,
        "full_label": primary_info.get("label") or primary_label or primary_id,
        "group": assign_group(primary_info.get("tags")),
        "size": 2,
    }]
    edges = []

    for r in rows:
        rid = r.get("id", "")
        if not rid:
            continue
        info = lookup.get(rid, {"label": r.get("region", rid), "symbol": "", "tags": []})
        row_tags = r.get("tags")
        if isinstance(row_tags, str):
            row_tags = [t.strip() for t in row_tags.split("|") if t.strip()]
        tags_for_group = info.get("tags") or row_tags or []

        nodes.append({
            "id": rid,
            "label": _node_display_label(info) or r.get("region", rid),
            "full_label": info.get("label") or r.get("region", rid),
            "group": assign_group(tags_for_group, info.get("label", "")),
        })

        pre = r.get("presynaptic_terminals", 0) or 0
        post = r.get("postsynaptic_terminals", 0) or 0
        weight = pre + post
        if weight > 0:
            edges.append({
                "source": primary_id,
                "target": rid,
                "weight": weight,
                "label": f"pre:{pre} post:{post}",
            })

    disp = _node_display_label(primary_info) or primary_label or primary_id
    return build_graph(
        nodes, edges,
        title=f"Region connectivity of {disp}",
        directed=False,
    )


# ---------------------------------------------------------------------------
# Converter: get_downstream_class_connectivity()
# ---------------------------------------------------------------------------

def _strip_markdown_link(text):
    """Extract label from ``[label](id)`` markdown link, or return as-is."""
    if not text:
        return text or ""
    m = re.match(r"^\[(.+)\]\(([^)]+)\)$", text)
    if m:
        return m.group(1)
    return text


def _extract_id_from_markdown(text):
    """Extract id from ``[label](id)`` markdown link, or return as-is."""
    if not text:
        return text or ""
    m = re.match(r"^\[(.+)\]\(([^)]+)\)$", text)
    if m:
        return m.group(2)
    return text


def graph_from_downstream_class(rows, primary_id, primary_label=None):
    """Build graph from ``get_downstream_class_connectivity()`` result rows.

    :param rows: list of row dicts with id, downstream_class, total_weight, etc.
    :param primary_id: short_form of the query neuron class
    :param primary_label: fallback label
    """
    if not rows:
        return None

    # Collect IDs — rows may have 'id' field, or extract from markdown
    all_ids = [primary_id]
    for r in rows:
        rid = r.get("id") or _extract_id_from_markdown(r.get("downstream_class", ""))
        if rid:
            all_ids.append(rid)
    lookup = batch_lookup_ids(all_ids)

    primary_info = lookup.get(primary_id, {
        "label": primary_label or primary_id,
        "symbol": "",
        "tags": [],
    })

    nodes = [{
        "id": primary_id,
        "label": _node_display_label(primary_info) or primary_label or primary_id,
        "full_label": primary_info.get("label") or primary_label or primary_id,
        "group": assign_group(primary_info.get("tags"), primary_info.get("label", "")),
        "size": 2,
    }]
    edges = []

    # Compute size scaling from pairwise_connections
    max_pw = max((r.get("pairwise_connections") or 0 for r in rows), default=1) or 1

    for r in rows:
        rid = r.get("id") or _extract_id_from_markdown(r.get("downstream_class", ""))
        if not rid:
            continue
        ds_label = _strip_markdown_link(r.get("downstream_class", rid))
        info = lookup.get(rid, {"label": ds_label, "symbol": "", "tags": []})

        pw = r.get("pairwise_connections") or 0
        size = 1 + (pw / max_pw) * 2  # scale 1–3

        nodes.append({
            "id": rid,
            "label": _node_display_label(info) or ds_label,
            "full_label": info.get("label") or ds_label,
            "group": assign_group(info.get("tags"), info.get("label", "")),
            "size": round(size, 1),
        })

        weight = r.get("total_weight") or 0
        if weight or pw:
            edges.append({
                "source": primary_id,
                "target": rid,
                "weight": weight,
            })

    disp = _node_display_label(primary_info) or primary_label or primary_id
    return build_graph(nodes, edges, title=f"Downstream of {disp}", directed=True)


# ---------------------------------------------------------------------------
# Converter: get_upstream_class_connectivity()
# ---------------------------------------------------------------------------

def graph_from_upstream_class(rows, primary_id, primary_label=None):
    """Build graph from ``get_upstream_class_connectivity()`` result rows.

    :param rows: list of row dicts with id, upstream_class, total_weight, etc.
    :param primary_id: short_form of the query neuron class
    :param primary_label: fallback label
    """
    if not rows:
        return None

    all_ids = [primary_id]
    for r in rows:
        rid = r.get("id") or _extract_id_from_markdown(r.get("upstream_class", ""))
        if rid:
            all_ids.append(rid)
    lookup = batch_lookup_ids(all_ids)

    primary_info = lookup.get(primary_id, {
        "label": primary_label or primary_id,
        "symbol": "",
        "tags": [],
    })

    nodes = [{
        "id": primary_id,
        "label": _node_display_label(primary_info) or primary_label or primary_id,
        "full_label": primary_info.get("label") or primary_label or primary_id,
        "group": assign_group(primary_info.get("tags"), primary_info.get("label", "")),
        "size": 2,
    }]
    edges = []

    max_pw = max((r.get("pairwise_connections") or 0 for r in rows), default=1) or 1

    for r in rows:
        rid = r.get("id") or _extract_id_from_markdown(r.get("upstream_class", ""))
        if not rid:
            continue
        us_label = _strip_markdown_link(r.get("upstream_class", rid))
        info = lookup.get(rid, {"label": us_label, "symbol": "", "tags": []})

        pw = r.get("pairwise_connections") or 0
        size = 1 + (pw / max_pw) * 2

        nodes.append({
            "id": rid,
            "label": _node_display_label(info) or us_label,
            "full_label": info.get("label") or us_label,
            "group": assign_group(info.get("tags"), info.get("label", "")),
            "size": round(size, 1),
        })

        weight = r.get("total_weight") or 0
        if weight or pw:
            edges.append({
                "source": rid,
                "target": primary_id,
                "weight": weight,
            })

    disp = _node_display_label(primary_info) or primary_label or primary_id
    return build_graph(nodes, edges, title=f"Upstream of {disp}", directed=True)
