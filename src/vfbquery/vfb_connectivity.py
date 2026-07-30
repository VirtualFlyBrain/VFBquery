"""Query synaptic connectivity between Drosophila neuron types via VFB.

Uses VFBquery's Neo4jConnect client to run Cypher queries directly against
the VFB Neo4j database, without depending on vfb_connect.

Two behaviours here are worth knowing before reading the code, because both
are the difference between an empty answer and a correct one.

**Queries are expanded over the subclass hierarchy.** Asking for "Kenyon cell"
means "Kenyon cell *or any of its subclasses*". This is not a nicety: in FBbt
the broad classes people actually name are almost never the classes instances
are typed to. ``Kenyon cell`` (``FBbt_00003686``) has **zero** directly-typed
instances — all ~16,000 of them hang off its 37 subclasses — so matching the
named class alone returns nothing at all for the single most obvious query in
the mushroom body. See :func:`_subclass_closure`.

**Some connectome datasets are excluded by default.** See
:data:`DEFAULT_EXCLUDE_DBS` for which, and why.
"""
from .neo4j_client import Neo4jConnect, dict_cursor


#: Connectome datasets excluded unless the caller says otherwise.
#:
#: These are *symbols* as returned by :func:`list_connectome_datasets`, matched
#: against both ``Site.short_form`` and ``Site.symbol[0]``.
#:
#: The reason is double-counting, not data quality — both datasets are good, and
#: both remain queryable by passing ``exclude_dbs=[]``:
#:
#: * ``fafb`` (*VFB CATMAID Adult Brain*) and ``fw`` (*FlyWire v783*) are two
#:   reconstructions of **the same EM volume**. A neuron traced in both appears
#:   twice, so a connection found in both is counted twice, and any "how many
#:   partners" number silently doubles for the cells that happen to have been
#:   traced in both. FlyWire is the proofread whole-brain segmentation of that
#:   volume, so it is the one kept.
#: * ``hb`` (*hemibrain v1.2.1*) is a partial volume — one hemisphere of one
#:   female brain — largely superseded for whole-brain questions by ``fw`` and
#:   ``mc`` (*male CNS v0.9*). Its cells overlap heavily in type with those two
#:   without being the same cells, which inflates per-type counts in a way that
#:   is easy to misread as biological variation.
#:
#: Excluding them by default makes the *shape* of a connectivity answer right
#: for a naive query. It also means a default query does not reproduce a
#: published hemibrain figure — pass ``exclude_dbs=[]`` for that, or
#: ``exclude_dbs`` naming everything except the dataset you want.
DEFAULT_EXCLUDE_DBS = ["hb", "fafb"]

#: Above this many classes in a subclass closure, expansion is abandoned for
#: that side and a warning is emitted. Nothing in FBbt between a nameable
#: neuron type and this bound is a problem — "cholinergic neuron" is the
#: broadest realistic query at ~5,700 subclasses and runs in a couple of
#: seconds — so hitting the cap means the query is rooted at something like
#: ``neuron`` itself (~18,000 subclasses, ~490,000 instances), where the answer
#: would not be usable regardless.
MAX_SUBCLASS_IDS = 10000


_NC = None


def _get_nc():
    """Get a Neo4jConnect instance for VFB, reusing one per process.

    Constructing ``Neo4jConnect`` runs a connection test to work out whether
    the server speaks the v4 or v3 transaction API. Returning a fresh instance
    per call meant that test ran again on every single query — a whole extra
    round-trip against a shared, and at times very slow, production server,
    paid before any useful work started. The answer does not change during a
    process's life, so it is worked out once.
    """
    global _NC
    if _NC is None:
        _NC = Neo4jConnect()
    return _NC


def _cypher_str(value):
    """Quote a Python string as a Cypher single-quoted literal.

    Labels reach this module straight from an HTTP query string, so the
    backslash and quote have to be neutralised before interpolation. The REST
    client has no parameter binding, which is why this is done by hand.
    """
    escaped = str(value).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _resolve_neuron_type_label(nc, label, notes=None):
    """Resolve a neuron type label or FBbt ID to a VFB short_form ID.

    Accepts FBbt IDs (e.g. "FBbt_00003789"), exact labels, case-insensitive
    labels, and exact synonyms (which is what catches short names like "Tm1").

    When none of those match, a containment search over labels and synonyms
    runs as a last resort. A **single** candidate is accepted and reported
    through ``notes`` — this is what makes the short names people actually type
    work, e.g. ``"DA1 lPN"`` for *adult antennal lobe projection neuron DA1
    lPN*. Two or more candidates are never guessed between; they are listed in
    the error so the caller can pick.

    :param nc: Neo4jConnect instance
    :param label: Neuron type label (e.g. "Kenyon cell") or FBbt ID
    :param notes: optional list; a message is appended when the resolution was
        not exact, so the caller can surface how the input was interpreted
    :return: short_form ID (e.g. "FBbt_00003686")
    :raises ValueError: if the label matches nothing, or is ambiguous
    """
    import re

    quoted = _cypher_str(label)

    # Direct FBbt ID lookup
    if re.match(r'^FBbt_\d+$', label):
        results = nc.commit_list([
            f"MATCH (n:Class:Neuron {{short_form: {quoted}}}) "
            f"RETURN n.short_form LIMIT 1"
        ])
        dc = dict_cursor(results)
        if dc:
            return dc[0]["n.short_form"]
        raise ValueError(
            f"Neuron class not found for ID '{label}'. "
            "Check the ID is a valid neuron class (not an anatomy region)."
        )

    # Exact label match. Kept on its own because it is the only step that is an
    # index seek, and it is what almost every caller hits.
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE n.label = {quoted} "
        f"RETURN n.short_form LIMIT 1"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    # The tiers below stay as separate statements on purpose. Merging them into
    # one `OR` was tried, on the reasoning that three sequential round-trips
    # against an intermittently slow server is three chances to block; measured
    # against production it was far worse. The single-predicate containment scan
    # returns in well under a second, while the same scan with the equality and
    # synonym disjuncts bolted on did not return inside forty seconds on any of
    # six attempts — the disjunction costs the planner the filter it can push
    # down. Split, each tier is also short-circuiting: a caller passing a real
    # label never reaches the scan at all.

    # Case-insensitive label fallback
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE toLower(n.label) = toLower({quoted}) "
        f"RETURN n.short_form, n.label LIMIT 5"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    # Synonym match (catches short names like "Tm1")
    results = nc.commit_list([
        f"MATCH (n:Class:Neuron) WHERE {quoted} IN n.synonym "
        f"RETURN n.short_form LIMIT 1"
    ])
    dc = dict_cursor(results)
    if dc:
        return dc[0]["n.short_form"]

    # Last resort: containment over label and synonyms. Ordering by label
    # length puts the tersest — and so most likely intended — term first, which
    # only matters for the error message, since a single hit is the only case
    # that resolves.
    results = nc.commit_list([
        "MATCH (n:Class:Neuron) WHERE NOT n:Deprecated AND ("
        f"toLower(n.label) CONTAINS toLower({quoted}) OR "
        f"any(syn IN n.synonym WHERE toLower(syn) CONTAINS toLower({quoted}))"
        ") RETURN n.short_form AS id, n.label AS label "
        "ORDER BY size(n.label), n.label LIMIT 6"
    ])
    candidates = dict_cursor(results)
    if len(candidates) == 1:
        hit = candidates[0]
        if notes is not None:
            notes.append(
                f"'{label}' is not a VFB term; matched the only term containing "
                f"it: '{hit['label']}' ({hit['id']})."
            )
        return hit["id"]
    if len(candidates) > 1:
        shown = "; ".join(f"'{c['label']}' ({c['id']})" for c in candidates[:5])
        more = " and others" if len(candidates) > 5 else ""
        raise ValueError(
            f"Neuron type '{label}' is ambiguous in VFB — it matches {shown}"
            f"{more}. Pass one of those labels or its FBbt ID."
        )

    raise ValueError(
        f"Neuron type not found in VFB: '{label}'. "
        "Use list_connectome_datasets() or check spelling."
    )


def _subclass_closure(nc, class_id):
    """Return ``(label, subclass_ids, instance_count)`` for a neuron class.

    ``subclass_ids`` is the class itself plus every class beneath it under
    ``SUBCLASSOF``, and ``instance_count`` is how many non-deprecated
    connectivity individuals are typed to any of them. Both come from one
    round-trip because the caller needs both: the ids to query with, and the
    count to decide which side of a two-sided query to drive from.

    Why the count matters is worth stating plainly, since getting it wrong is a
    two-minute query instead of a half-second one: expanding *both* sides of a
    connectivity match into variable-length ``SUBCLASSOF`` walks does not
    complete in reasonable time. Driving from the smaller side and filtering
    the partner by an id list does. See :func:`_build_connectivity_cypher`.
    """
    quoted = _cypher_str(class_id)
    results = nc.commit_list([
        f"MATCH (c:Class:Neuron) WHERE c.short_form = {quoted}\n"
        "WITH c LIMIT 1\n"
        "OPTIONAL MATCH (c)<-[:SUBCLASSOF*0..]-(sub:Class)\n"
        "WITH c, collect(DISTINCT sub.short_form) AS ids\n"
        "OPTIONAL MATCH (s:Class)<-[:INSTANCEOF]-"
        "(n:Individual:Neuron:has_neuron_connectivity)\n"
        "WHERE s.short_form IN ids AND NOT n:Deprecated\n"
        "RETURN c.label AS label, ids AS ids, count(DISTINCT n) AS instances"
    ])
    dc = dict_cursor(results)
    if not dc:
        return class_id, [class_id], 0
    row = dc[0]
    ids = sorted(set(row.get("ids") or []) | {class_id})
    return row.get("label") or class_id, ids, row.get("instances") or 0


def _id_list(ids):
    """Render a list of ids as a Cypher list literal."""
    return "[" + ", ".join(_cypher_str(i) for i in ids) + "]"


def _db_filter_predicate(var, exclude_dbs):
    """Return a Cypher ``EXISTS { … }`` predicate for the dataset exclusion.

    True when ``var`` has at least one data-source cross-reference that is *not*
    in ``exclude_dbs``. This is deliberately a predicate rather than the
    ``MATCH … WHERE NOT …`` it replaced: as a MATCH it both multiplied rows (a
    neuron with two cross-references matched twice) and, placed after the
    synapse expansion, cost 70 s on a query that takes 0.4 s with the predicate
    form. Placement matters as much as form — it belongs immediately after the
    ``WITH DISTINCT`` that reduces to the anchor neurons.
    """
    db_list = _id_list(exclude_dbs)
    return (
        f"EXISTS {{ MATCH ({var})-[:database_cross_reference]->"
        "(s:Individual:Site {is_data_source:[True]}) "
        f"WHERE NOT s.short_form IN {db_list} "
        f"AND NOT s.symbol[0] IN {db_list} }}"
    )


def list_connectome_datasets():
    """List available connectome datasets from VFB.

    ``short_form`` is returned alongside ``symbol`` because both are legitimate
    things to exclude with: :func:`_db_filter_predicate` compares against
    ``Site.short_form`` *and* ``Site.symbol[0]``, so a caller who reads
    ``flywire783`` off a term's cross-references and passes that to
    ``exclude_dbs`` is not making a mistake. Returning the symbol alone left
    them guessing which of the two spellings the filter wanted, and guessing
    wrong used to be silent — see ``ha_api._resolve_exclude_dbs``.

    :return: list of dicts with 'label', 'symbol' and 'short_form' keys
    """
    nc = _get_nc()
    results = nc.commit_list([
        "MATCH (c:Connectome:Individual) "
        "RETURN c.label, c.symbol[0], c.short_form ORDER BY c.label"
    ])
    dc = dict_cursor(results)
    return [{"label": r["c.label"], "symbol": r["c.symbol[0]"],
             "short_form": r["c.short_form"]} for r in dc]


def _connectivity_cache_key(upstream_type, downstream_type, weight,
                            group_by_class, exclude_dbs):
    """Build a stable, Solr-safe cache key for a query_connectivity call.

    The default ``@with_solr_cache`` decorator keys on a single id, which does
    not fit this five-parameter signature, so the key is built here from all
    of the inputs (mirroring the in-memory key in ``ha_api`` —
    ``query_connectivity:{upstream}:{downstream}:{weight}:{group_by_class}:{exclude_dbs}``)
    and hashed so it is safe to embed in a Solr document id.
    """
    import hashlib
    raw = (
        f"query_connectivity:{upstream_type}:{downstream_type}:"
        f"{weight}:{group_by_class}:{exclude_dbs}"
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def query_connectivity(upstream_type=None, downstream_type=None, weight=5,
                       group_by_class=False, exclude_dbs=None, force_refresh=False):
    """Query synaptic connections between neuron types.

    At least one of upstream_type or downstream_type must be provided.
    Parameters are neuron type labels (e.g. "Kenyon cell") which are
    resolved to VFB IDs internally.

    A type means itself *or any of its subclasses*: "Kenyon cell" finds the
    ~16,000 individuals typed to its subclasses, none of which are typed to
    "Kenyon cell" itself. See the module docstring.

    Results are persisted in the SOLR result cache under a composite key
    (see :func:`_connectivity_cache_key`) so a cold miss survives restarts
    and reaches the other API containers. The in-memory ResultCache and
    request coalescer in ``ha_api`` sit in front of this layer; the graph
    post-processing (``post_fn``) stays in the handler, so it is never part
    of the cached payload.

    :param upstream_type: Presynaptic neuron type label (optional)
    :param downstream_type: Postsynaptic neuron type label (optional)
    :param weight: Minimum synapse count threshold (default 5)
    :param group_by_class: Aggregate by neuron class (default False)
    :param exclude_dbs: Dataset symbols to exclude; defaults to
        :data:`DEFAULT_EXCLUDE_DBS`, which documents why. Pass ``[]`` for every
        dataset.
    :param force_refresh: Bypass the SOLR cache and recompute (default False)
    :return: dict with 'connections' (list of dicts), 'warnings' (list),
        'count' (int) and 'resolved' (what each type label was taken to mean,
        including how far the subclass expansion reached)
    """
    if exclude_dbs is None:
        exclude_dbs = list(DEFAULT_EXCLUDE_DBS)

    if upstream_type is None and downstream_type is None:
        raise ValueError("At least one of upstream_type or downstream_type must be specified")

    # Fully bypass the cache when disabled (VFBQUERY_CACHE_ENABLED=false): run
    # the live query directly without reading stale data or writing to the
    # shared production cache. Mirrors the @with_solr_cache decorator's bypass.
    from .solr_result_cache import get_solr_cache, solr_caching_disabled
    if solr_caching_disabled():
        return _query_connectivity_uncached(
            upstream_type, downstream_type, weight, group_by_class, exclude_dbs
        )

    # Persistent SOLR cache (composite key) sitting behind the in-memory cache.
    cache = get_solr_cache()
    cache_key = _connectivity_cache_key(
        upstream_type, downstream_type, weight, group_by_class, exclude_dbs
    )
    if force_refresh:
        cache.clear_cache_entry('query_connectivity', cache_key)
    else:
        cached = cache.get_cached_result('query_connectivity', cache_key)
        if cached is not None:
            return cached

    result = _query_connectivity_uncached(
        upstream_type, downstream_type, weight, group_by_class, exclude_dbs
    )

    # Cache deterministic, non-error results (count >= 0). Best-effort: a Solr
    # write failure must never break the query path.
    try:
        if isinstance(result, dict) and result.get('count', -1) >= 0:
            cache.cache_result('query_connectivity', cache_key, result)
    except Exception:
        pass
    return result


def _query_connectivity_uncached(upstream_type=None, downstream_type=None, weight=5,
                                 group_by_class=False, exclude_dbs=None):
    """Compute connectivity directly from Neo4j (no caching).

    Split out from :func:`query_connectivity` so the SOLR cache wraps a single
    pure function. Callers should go through ``query_connectivity``.
    """
    if exclude_dbs is None:
        exclude_dbs = list(DEFAULT_EXCLUDE_DBS)

    nc = _get_nc()
    warnings = []
    resolved = {}
    sides = {}

    for side, label in (("upstream", upstream_type),
                        ("downstream", downstream_type)):
        if label is None:
            continue
        try:
            class_id = _resolve_neuron_type_label(nc, label, notes=warnings)
        except ValueError as e:
            warnings.append(str(e))
            return {"connections": [], "warnings": warnings, "count": 0,
                    "resolved": resolved}

        class_label, ids, instances = _subclass_closure(nc, class_id)

        if len(ids) > MAX_SUBCLASS_IDS:
            warnings.append(
                f"'{class_label}' ({class_id}) has {len(ids)} subclasses, over "
                f"the {MAX_SUBCLASS_IDS} limit; only neurons typed directly to "
                "it were searched. Ask about a more specific type."
            )
            ids = [class_id]

        resolved[side] = {
            "query": label,
            "id": class_id,
            "label": class_label,
            "classes_searched": len(ids),
            "instances": instances,
        }

        if instances == 0:
            warnings.append(
                f"No connectivity data for '{class_label}' ({class_id}) or any "
                "of its subclasses — no neurons from a connectome dataset are "
                "typed to it."
            )
            return {"connections": [], "warnings": warnings, "count": 0,
                    "resolved": resolved}

        sides[side] = (ids, instances)

    # Drive the query from the side with fewer individuals. Expanding both
    # sides into variable-length walks does not complete; expanding the smaller
    # side and filtering the partner against an id list takes under a second.
    # For a one-sided query the supplied side is the only candidate.
    anchor = min(sides, key=lambda s: sides[s][1])

    cypher = _build_connectivity_cypher(
        upstream_ids=sides["upstream"][0] if "upstream" in sides else None,
        downstream_ids=sides["downstream"][0] if "downstream" in sides else None,
        weight=weight,
        group_by_class=group_by_class,
        exclude_dbs=exclude_dbs,
        anchor=anchor,
    )

    results = nc.commit_list([cypher])
    if not results:
        return {"connections": [], "warnings": warnings, "count": 0,
                "resolved": resolved}

    dc = dict_cursor(results)
    return {"connections": dc, "warnings": warnings, "count": len(dc),
            "resolved": resolved}


def _build_connectivity_cypher(upstream_ids, downstream_ids, weight,
                               group_by_class, exclude_dbs, anchor="upstream"):
    """Build the Cypher query for connectivity.

    Originally ported from VFB_connect ``cross_server_tools.py``
    ``get_connected_neurons_by_type()``, which matched one class directly. This
    takes id *lists* — a class and its subclass closure, from
    :func:`_subclass_closure` — because the class a user names is usually not
    the class instances are typed to.

    ``anchor`` names the side the query is driven from, and should be the side
    with fewer individuals. The anchored side is expanded to its neurons and
    reduced with ``WITH DISTINCT`` before the synapse expansion; the other side
    is filtered afterwards against its id list. The two arrangements are written
    out separately below rather than generated, because the difference between
    them — which ``WITH`` the dataset filter follows, and whether it needs
    ``WHERE`` or ``AND`` — is exactly where this query gets slow or invalid.

    Both arrangements leave ``c1``, ``c2``, ``n1``, ``n2`` and ``r`` bound, so
    the RETURN blocks are shared.
    """
    clauses = []
    dbf = _db_filter_predicate("n1", exclude_dbs) if exclude_dbs else None

    if anchor == "upstream":
        clauses.append(
            "MATCH (c1_a:Class:Neuron)"
            f"\nWHERE c1_a.short_form IN {_id_list(upstream_ids)}"
        )
        clauses.append(
            "MATCH (c1_a)<-[:INSTANCEOF]-"
            "(n1:Individual:Neuron:has_neuron_connectivity)"
            # deprecated neurons are obsolete and must not appear in connectivity
            "\nWHERE NOT n1:Deprecated"
        )
        # Reduce to the distinct anchor neurons before doing anything else: one
        # neuron typed to several subclasses is one neuron.
        clauses.append("WITH DISTINCT n1" + (f"\nWHERE {dbf}" if dbf else ""))
        clauses.append(
            "MATCH (n1)-[r:synapsed_to]->"
            "(n2:Individual:Neuron:has_neuron_connectivity)"
            f"\nWHERE r.weight[0] >= {weight}"
            "\nAND NOT n2:Deprecated"
        )
        if downstream_ids:
            clauses.append(
                "MATCH (n2)-[:INSTANCEOF]->(c2:Class:Neuron)"
                f"\nWHERE c2.short_form IN {_id_list(downstream_ids)}"
            )
        else:
            clauses.append("MATCH (n2)-[:INSTANCEOF]->(c2:Class)")
        clauses.append(
            "MATCH (n1)-[:INSTANCEOF]->(c1:Class:Neuron)"
            f"\nWHERE c1.short_form IN {_id_list(upstream_ids)}"
        )
    else:
        clauses.append(
            "MATCH (c2_a:Class:Neuron)"
            f"\nWHERE c2_a.short_form IN {_id_list(downstream_ids)}"
        )
        clauses.append(
            "MATCH (c2_a)<-[:INSTANCEOF]-"
            "(n2:Individual:Neuron:has_neuron_connectivity)"
            "\nWHERE NOT n2:Deprecated"
        )
        clauses.append("WITH DISTINCT n2")
        # The dataset filter is on n1, which only exists from here, so it joins
        # this WHERE with AND rather than opening one of its own.
        clauses.append(
            "MATCH (n1:Individual:Neuron:has_neuron_connectivity)"
            "-[r:synapsed_to]->(n2)"
            f"\nWHERE r.weight[0] >= {weight}"
            "\nAND NOT n1:Deprecated"
            + (f"\nAND {dbf}" if dbf else "")
        )
        if upstream_ids:
            clauses.append(
                "MATCH (n1)-[:INSTANCEOF]->(c1:Class:Neuron)"
                f"\nWHERE c1.short_form IN {_id_list(upstream_ids)}"
            )
        else:
            clauses.append("MATCH (n1)-[:INSTANCEOF]->(c1:Class)")
        clauses.append(
            "MATCH (n2)-[:INSTANCEOF]->(c2:Class:Neuron)"
            f"\nWHERE c2.short_form IN {_id_list(downstream_ids)}"
        )

    if not group_by_class:
        # Per-neuron results
        # Show the source site + accession as plain text even when the site is
        # deprecated (these columns are passed through to the results table and
        # are not rendered as links downstream); deprecated *neurons* are still
        # excluded above.
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

        # Denominator for percent_connected: every neuron of this upstream
        # class, connected or not. It has to carry the same deprecation and
        # dataset filters as the numerator or the percentage is nonsense — a
        # neuron excluded from the numerator by the dataset filter but counted
        # here would depress the figure for its whole class.
        total_match = (
            "MATCH (c1)<-[:INSTANCEOF]-(all_n1:Individual:has_neuron_connectivity)"
            "\nWHERE NOT all_n1:Deprecated"
        )
        if exclude_dbs:
            total_match += "\nAND " + _db_filter_predicate("all_n1", exclude_dbs)
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
