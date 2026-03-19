"""Query synaptic connectivity between Drosophila neuron types via VFB.

Uses VFBquery's Neo4jConnect client to run Cypher queries directly against
the VFB Neo4j database, without depending on vfb_connect.
"""
from .neo4j_client import Neo4jConnect, dict_cursor


def _get_nc():
    """Get a Neo4jConnect instance for VFB."""
    return Neo4jConnect()


def _resolve_neuron_type_label(nc, label):
    """Resolve a neuron type label or FBbt ID to a VFB short_form ID.

    Accepts FBbt IDs (e.g. "FBbt_00003789"), exact labels, synonym matches,
    or case-insensitive labels.

    :param nc: Neo4jConnect instance
    :param label: Neuron type label (e.g. "Kenyon cell") or FBbt ID
    :return: short_form ID (e.g. "FBbt_00003686")
    :raises ValueError: if label not found
    """
    import re

    # Direct FBbt ID lookup
    if re.match(r'^FBbt_\d+$', label):
        results = nc.commit_list([
            f"MATCH (n:Class:Neuron {{short_form: '{label}'}}) "
            f"RETURN n.short_form LIMIT 1"
        ])
        dc = dict_cursor(results)
        if dc:
            return dc[0]["n.short_form"]
        raise ValueError(
            f"Neuron class not found for ID '{label}'. "
            "Check the ID is a valid neuron class (not an anatomy region)."
        )

    # Exact label match
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE n.label = '{label}' "
        f"RETURN n.short_form LIMIT 1"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    # Case-insensitive label fallback
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE toLower(n.label) = toLower('{label}') "
        f"RETURN n.short_form, n.label LIMIT 5"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    # Synonym match (catches short names like "Tm1")
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE '{label}' IN n.synonym "
        f"RETURN n.short_form LIMIT 1"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    raise ValueError(
        f"Neuron type not found in VFB: '{label}'. "
        "Use list_connectome_datasets() or check spelling."
    )


def list_connectome_datasets():
    """List available connectome datasets from VFB.

    :return: list of dicts with 'label' and 'symbol' keys
    """
    nc = _get_nc()
    results = nc.commit_list([
        "MATCH (c:Connectome:Individual) RETURN c.label, c.symbol[0] ORDER BY c.label"
    ])
    dc = dict_cursor(results)
    return [{"label": r["c.label"], "symbol": r["c.symbol[0]"]} for r in dc]


def query_connectivity(upstream_type=None, downstream_type=None, weight=5,
                       group_by_class=False, exclude_dbs=None):
    """Query synaptic connections between neuron types.

    At least one of upstream_type or downstream_type must be provided.
    Parameters are neuron type labels (e.g. "Kenyon cell") which are
    resolved to VFB IDs internally.

    :param upstream_type: Presynaptic neuron type label (optional)
    :param downstream_type: Postsynaptic neuron type label (optional)
    :param weight: Minimum synapse count threshold (default 5)
    :param group_by_class: Aggregate by neuron class (default False)
    :param exclude_dbs: Dataset symbols to exclude (default ["hb", "fafb"])
    :return: dict with 'connections' (list of dicts), 'warnings' (list), 'count' (int)
    """
    if exclude_dbs is None:
        exclude_dbs = ["hb", "fafb"]

    if upstream_type is None and downstream_type is None:
        raise ValueError("At least one of upstream_type or downstream_type must be specified")

    nc = _get_nc()
    warnings = []

    # Resolve labels to IDs
    upstream_id = None
    downstream_id = None

    if upstream_type is not None:
        try:
            upstream_id = _resolve_neuron_type_label(nc, upstream_type)
        except ValueError as e:
            warnings.append(str(e))
            return {"connections": [], "warnings": warnings, "count": 0}

    if downstream_type is not None:
        try:
            downstream_id = _resolve_neuron_type_label(nc, downstream_type)
        except ValueError as e:
            warnings.append(str(e))
            return {"connections": [], "warnings": warnings, "count": 0}

    # Build Cypher query
    cypher = _build_connectivity_cypher(
        upstream_id=upstream_id,
        downstream_id=downstream_id,
        weight=weight,
        group_by_class=group_by_class,
        exclude_dbs=exclude_dbs,
    )

    results = nc.commit_list([cypher])
    if not results:
        return {"connections": [], "warnings": warnings, "count": 0}

    dc = dict_cursor(results)
    return {"connections": dc, "warnings": warnings, "count": len(dc)}


def _build_connectivity_cypher(upstream_id, downstream_id, weight,
                               group_by_class, exclude_dbs):
    """Build the Cypher query for connectivity.

    Ported from VFB_connect cross_server_tools.py get_connected_neurons_by_type().
    """
    clauses = []

    # Match upstream class and subclasses
    if upstream_id is not None:
        clauses.append(
            f"MATCH (:Class:Neuron {{short_form:'{upstream_id}'}})"
            f"<-[:SUBCLASSOF*0..]-(c1:Class:Neuron)"
        )

    # Match downstream class and subclasses
    if downstream_id is not None:
        clauses.append(
            f"MATCH (:Class:Neuron {{short_form:'{downstream_id}'}})"
            f"<-[:SUBCLASSOF*0..]-(c2:Class:Neuron)"
        )

    # Core synapse matching
    clauses.append(
        "MATCH (c1)<-[:INSTANCEOF]-(n1:Individual:Neuron:has_neuron_connectivity)"
        "-[r:synapsed_to]->"
        "(n2:Individual:Neuron:has_neuron_connectivity)-[:INSTANCEOF]->(c2)"
        f"\nWHERE r.weight[0] >= {weight}"
    )

    # Database filtering
    if exclude_dbs:
        db_list = str(exclude_dbs)
        clauses.append(
            "MATCH (n1)-[:database_cross_reference]->"
            "(s:Individual:Site {is_data_source:[True]})"
            f"\nWHERE NOT (s.short_form IN {db_list})"
            f"\nAND NOT (s.symbol[0] IN {db_list})"
        )

    if not group_by_class:
        # Per-neuron results
        clauses.append(
            "OPTIONAL MATCH (n1)-[r1:database_cross_reference]->"
            "(s1:Individual:Site {is_data_source:[True]})"
        )
        clauses.append(
            "OPTIONAL MATCH (n2)-[r2:database_cross_reference]->"
            "(s2:Individual:Site {is_data_source:[True]})"
        )
        clauses.append(
            "RETURN "
            "apoc.text.join(collect(distinct c1.label),'|') AS upstream_class, "
            "apoc.text.join(collect(distinct c1.short_form),'|') AS upstream_class_id, "
            "n1.short_form as upstream_neuron_id, "
            "n1.label as upstream_neuron_name, "
            "r.weight[0] as weight, "
            "n2.short_form as downstream_neuron_id, "
            "n2.label as downstream_neuron_name, "
            "apoc.text.join(collect(distinct c2.label),'|') as downstream_class, "
            "apoc.text.join(collect(distinct c2.short_form),'|') as downstream_class_id, "
            "s1.short_form AS up_data_source, "
            "r1.accession[0] as up_accession, "
            "s2.short_form AS down_data_source, "
            "r2.accession[0] AS down_accession"
        )
    else:
        # Class-aggregated results
        clauses.append(
            "WITH c1, c2, count(*) as pairwise_connections, "
            "sum(r.weight[0]) as total_weight, "
            "count(distinct n1) as connected_upstream_count"
        )

        # Count total upstream neurons (with optional db filtering)
        total_match = (
            "MATCH (c1)<-[:INSTANCEOF]-(all_n1:Individual:has_neuron_connectivity)"
        )
        if exclude_dbs:
            db_list = str(exclude_dbs)
            total_match += (
                "\nMATCH (all_n1)-[:database_cross_reference]->"
                "(s_all:Individual:Site {is_data_source:[True]})"
                f"\nWHERE NOT (s_all.short_form IN {db_list})"
                f"\nAND NOT (s_all.symbol[0] IN {db_list})"
            )
        clauses.append(total_match)

        clauses.append(
            "WITH c1, c2, pairwise_connections, total_weight, "
            "connected_upstream_count, "
            "count(distinct all_n1) as total_upstream_count"
        )

        clauses.append(
            "RETURN "
            "c1.label AS upstream_class, "
            "c1.short_form AS upstream_class_id, "
            "c2.label AS downstream_class, "
            "c2.short_form AS downstream_class_id, "
            "total_upstream_count, "
            "connected_upstream_count, "
            "round((toFloat(connected_upstream_count)/toFloat(total_upstream_count))*100) "
            "as percent_connected, "
            "pairwise_connections, "
            "total_weight, "
            "total_weight/pairwise_connections as average_weight "
            "ORDER BY pairwise_connections DESC, average_weight DESC"
        )

    return " \n\n".join(clauses)
