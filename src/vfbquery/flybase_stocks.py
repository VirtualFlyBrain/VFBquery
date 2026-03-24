"""Find FlyBase stocks for genes, alleles, insertions, or split system combinations."""
import re

import pandas as pd

from .flybase_db import get_connection


def _run_query(conn, sql, params):
    """Execute a query and return a DataFrame."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
        if not rows:
            return pd.DataFrame()
        columns = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=columns)


def resolve_entity(name_or_id):
    """Resolve a user-provided name or symbol to a canonical FlyBase feature.

    This Python helper still accepts FlyBase IDs for backwards compatibility.
    The HA API ``/resolve_entity`` endpoint prefers unresolved query text and,
    if an ID slips through, rewrites it to the feature name via VFB term_info
    before resolving.

    Resolution order for names (not IDs):
      1. Exact match on feature.name
      2. Synonym match via feature_synonym (case-insensitive ILIKE)
      3. Broad match via feature.name ILIKE '%query%'

    :param name_or_id: Gene name, allele symbol, or FlyBase ID (FBgn/FBal/FBti/FBst/FBco)
    :return: dict with 'match_type' and 'results' list
    """
    conn = get_connection(statement_timeout_ms=30000)
    try:
        return _resolve_entity_impl(conn, name_or_id)
    finally:
        conn.close()


def _resolve_entity_impl(conn, name_or_id):
    """Internal implementation of resolve_entity."""
    # Direct ID lookup
    if re.match(r"FB(gn|al|ti|st|co)\d+", name_or_id):
        df = _run_query(conn, """
            SELECT f.name, f.uniquename, c.name AS type
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE f.uniquename = %(id)s AND f.is_obsolete = false
        """, {"id": name_or_id})
        if len(df) > 0:
            return {
                "match_type": "EXACT",
                "results": [
                    {"name": r["name"], "uniquename": r["uniquename"],
                     "type": r["type"], "matched_synonym": None}
                    for _, r in df.iterrows()
                ],
            }
        return {"match_type": "NOT_FOUND", "results": []}

    feature_types = [
        "gene", "allele", "transposable_element_insertion_site",
        "chromosome_structure_variation", "split system combination",
    ]

    # 1. Exact match on feature.name
    df = _run_query(conn, """
        SELECT DISTINCT f.name, f.uniquename, c.name AS type
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        WHERE f.is_obsolete = false
          AND c.name = ANY(%(types)s)
          AND f.name = %(name)s
        ORDER BY c.name, f.name
        LIMIT 20
    """, {"name": name_or_id, "types": feature_types})

    if len(df) > 0:
        return {
            "match_type": "EXACT",
            "results": [
                {"name": r["name"], "uniquename": r["uniquename"],
                 "type": r["type"], "matched_synonym": None}
                for _, r in df.iterrows()
            ],
        }

    # 2. Synonym match (case-insensitive)
    df = _run_query(conn, """
        SELECT DISTINCT f.name, f.uniquename, c.name AS type,
               syn.name AS matched_synonym
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        JOIN feature_synonym fs ON f.feature_id = fs.feature_id
        JOIN synonym syn ON fs.synonym_id = syn.synonym_id
        WHERE f.is_obsolete = false
          AND c.name = ANY(%(types)s)
          AND syn.name ILIKE %(name)s
        ORDER BY c.name, f.name
        LIMIT 20
    """, {"name": name_or_id, "types": feature_types})

    if len(df) > 0:
        return {
            "match_type": "SYNONYM",
            "results": [
                {"name": r["name"], "uniquename": r["uniquename"],
                 "type": r["type"], "matched_synonym": r["matched_synonym"]}
                for _, r in df.iterrows()
            ],
        }

    # 3. Broad ILIKE search
    df = _run_query(conn, """
        SELECT DISTINCT f.name, f.uniquename, c.name AS type
        FROM feature f
        JOIN cvterm c ON f.type_id = c.cvterm_id
        WHERE f.is_obsolete = false
          AND c.name = ANY(%(types)s)
          AND (f.name ILIKE %(pattern)s)
        ORDER BY c.name, f.name
        LIMIT 20
    """, {"pattern": "%" + name_or_id + "%", "types": feature_types})

    if len(df) > 0:
        return {
            "match_type": "BROAD",
            "results": [
                {"name": r["name"], "uniquename": r["uniquename"],
                 "type": r["type"], "matched_synonym": None}
                for _, r in df.iterrows()
            ],
        }

    return {"match_type": "NOT_FOUND", "results": []}


# ---------------------------------------------------------------------------
# Stock query SQL
# ---------------------------------------------------------------------------

_GENE_STOCKS_SQL = """
WITH all_stocks AS (
  -- Path 1: gene -> allele -> genotype -> stock (direct)
  SELECT DISTINCT s.uniquename AS stock_id, s.name AS stock_number,
         g.uniquename AS genotype, sc.uniquename AS collection
  FROM feature gene
  JOIN feature_relationship fr ON gene.feature_id = fr.object_id
  JOIN cvterm frt ON fr.type_id = frt.cvterm_id AND frt.name = 'alleleof'
  JOIN feature a ON fr.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_genotype fg ON a.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 2: gene -> allele -> FBtp (construct) -> FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'alleleof'
  JOIN feature a ON fr1.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr2 ON a.feature_id = fr2.subject_id
  JOIN feature tp ON fr2.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr3 ON tp.feature_id = fr3.object_id
  JOIN cvterm c3 ON fr3.type_id = c3.cvterm_id AND c3.name = 'producedby'
  JOIN feature ti ON fr3.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 3: gene -> allele -> associated_with FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'alleleof'
  JOIN feature a ON fr1.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr2 ON a.feature_id = fr2.subject_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'associated_with'
  JOIN feature ti ON fr2.object_id = ti.feature_id AND ti.is_obsolete = false
  JOIN cvterm cti ON ti.type_id = cti.cvterm_id
    AND cti.name IN ('transposable_element_insertion_site', 'insertion_site', 'insertion')
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s

  UNION

  -- Path 4: gene -> regulatory_region -> allele -> FBtp -> FBti -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature gene
  JOIN feature_relationship fr1 ON gene.feature_id = fr1.object_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'associated_with'
  JOIN feature rr ON fr1.subject_id = rr.feature_id
  JOIN cvterm ctr ON rr.type_id = ctr.cvterm_id AND ctr.name = 'regulatory_region'
  JOIN feature_relationship fr2 ON rr.feature_id = fr2.object_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'has_reg_region'
  JOIN feature a ON fr2.subject_id = a.feature_id AND a.is_obsolete = false
  JOIN feature_relationship fr3 ON a.feature_id = fr3.subject_id
  JOIN feature tp ON fr3.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr4 ON tp.feature_id = fr4.object_id
  JOIN cvterm c4 ON fr4.type_id = c4.cvterm_id AND c4.name = 'producedby'
  JOIN feature ti ON fr4.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE gene.uniquename = %(feature_id)s
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
"""

_ALLELE_STOCKS_SQL = """
WITH all_stocks AS (
  -- Path 1: allele -> genotype -> stock (direct)
  SELECT DISTINCT s.uniquename AS stock_id, s.name AS stock_number,
         g.uniquename AS genotype, sc.uniquename AS collection
  FROM feature f
  JOIN feature_genotype fg ON f.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false

  UNION

  -- Path 2: allele -> FBtp (construct) -> FBti (insertion) -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature f
  JOIN feature_relationship fr1 ON f.feature_id = fr1.subject_id
  JOIN feature tp ON fr1.object_id = tp.feature_id
  JOIN cvterm ctp ON tp.type_id = ctp.cvterm_id
    AND ctp.name = 'transgenic_transposable_element'
  JOIN feature_relationship fr2 ON tp.feature_id = fr2.object_id
  JOIN cvterm c2 ON fr2.type_id = c2.cvterm_id AND c2.name = 'producedby'
  JOIN feature ti ON fr2.subject_id = ti.feature_id AND ti.is_obsolete = false
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false

  UNION

  -- Path 3: allele -> associated_with insertion -> genotype -> stock
  SELECT DISTINCT s.uniquename, s.name, g.uniquename, sc.uniquename
  FROM feature f
  JOIN feature_relationship fr1 ON f.feature_id = fr1.subject_id
  JOIN cvterm c1 ON fr1.type_id = c1.cvterm_id AND c1.name = 'associated_with'
  JOIN feature ti ON fr1.object_id = ti.feature_id AND ti.is_obsolete = false
  JOIN cvterm cti ON ti.type_id = cti.cvterm_id
    AND cti.name IN ('transposable_element_insertion_site', 'insertion_site', 'insertion')
  JOIN feature_genotype fg ON ti.feature_id = fg.feature_id
  JOIN genotype g ON fg.genotype_id = g.genotype_id
  JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
  JOIN stock s ON sg.stock_id = s.stock_id AND s.is_obsolete = false
  LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
  LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
  WHERE f.uniquename = %(feature_id)s AND f.is_obsolete = false
)
SELECT stock_id, stock_number, genotype, collection
FROM all_stocks
"""

_INSERTION_STOCKS_SQL = """
SELECT DISTINCT
    s.uniquename AS stock_id,
    s.name AS stock_number,
    g.uniquename AS genotype,
    sc.uniquename AS collection
FROM feature f
JOIN feature_genotype fg ON f.feature_id = fg.feature_id
JOIN genotype g ON fg.genotype_id = g.genotype_id
JOIN stock_genotype sg ON g.genotype_id = sg.genotype_id
JOIN stock s ON sg.stock_id = s.stock_id
LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
WHERE f.uniquename = %(feature_id)s
  AND f.is_obsolete = false
  AND s.is_obsolete = false
"""

_STOCK_DETAILS_SQL = """
SELECT
    s.uniquename AS stock_id,
    s.name AS stock_number,
    s.description,
    g.uniquename AS genotype,
    sc.uniquename AS collection
FROM stock s
LEFT JOIN stockcollection_stock scs ON s.stock_id = scs.stock_id
LEFT JOIN stockcollection sc ON scs.stockcollection_id = sc.stockcollection_id
LEFT JOIN stock_genotype sg ON s.stock_id = sg.stock_id
LEFT JOIN genotype g ON sg.genotype_id = g.genotype_id
WHERE s.uniquename = %(stock_id)s
  AND s.is_obsolete = false
"""

_COMBO_COMPONENTS_SQL = """
SELECT a.name AS allele_name, a.uniquename AS allele_id
FROM feature combo
JOIN feature_relationship fr ON combo.feature_id = fr.subject_id
JOIN cvterm c ON fr.type_id = c.cvterm_id AND c.name = 'partially_produced_by'
JOIN feature a ON fr.object_id = a.feature_id AND a.is_obsolete = false
WHERE combo.uniquename = %(combo_id)s
  AND combo.is_obsolete = false
ORDER BY a.uniquename
"""


def _add_collection_filter(sql, params, collection_filter, use_where=False):
    """Add optional collection filter to a stock query."""
    if collection_filter:
        clause = "WHERE" if use_where else "  AND"
        sql += f"{clause} collection ILIKE %(coll)s\n"
        params["coll"] = f"%{collection_filter}%"
    return sql


def _find_stocks_gene(conn, gene_id, collection_filter=None):
    """Find stocks for a gene via four UNION paths."""
    sql = _GENE_STOCKS_SQL
    params = {"feature_id": gene_id}
    sql = _add_collection_filter(sql, params, collection_filter, use_where=True)
    sql += "ORDER BY collection, stock_number;"
    return _run_query(conn, sql, params)


def _find_stocks_allele(conn, allele_id, collection_filter=None):
    """Find stocks for an allele via three UNION paths."""
    sql = _ALLELE_STOCKS_SQL
    params = {"feature_id": allele_id}
    sql = _add_collection_filter(sql, params, collection_filter, use_where=True)
    sql += "ORDER BY collection, stock_number;"
    return _run_query(conn, sql, params)


def _find_stocks_insertion(conn, feature_id, collection_filter=None):
    """Find stocks for an insertion or chromosome aberration."""
    sql = _INSERTION_STOCKS_SQL
    params = {"feature_id": feature_id}
    if collection_filter:
        sql += "  AND sc.uniquename ILIKE %(coll)s\n"
        params["coll"] = f"%{collection_filter}%"
    sql += "ORDER BY sc.uniquename, s.name;"
    return _run_query(conn, sql, params)


def _find_stocks_combination(conn, combo_id, collection_filter=None):
    """Find stocks for a split system combination via its component alleles."""
    components = _run_query(conn, _COMBO_COMPONENTS_SQL, {"combo_id": combo_id})
    if components.empty:
        return pd.DataFrame()

    frames = []
    for _, row in components.iterrows():
        df = _find_stocks_allele(conn, row["allele_id"], collection_filter)
        if not df.empty:
            df["component"] = row["allele_name"]
            df["component_id"] = row["allele_id"]
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["stock_id"])
        .sort_values(["collection", "stock_number"])
        .reset_index(drop=True)
    )


def _find_stock_details(conn, stock_id):
    """Look up details for a specific stock ID."""
    return _run_query(conn, _STOCK_DETAILS_SQL, {"stock_id": stock_id})


def find_stocks(feature_id, collection_filter=None):
    """Find stocks for a resolved FlyBase feature ID.

    Routes to the appropriate query based on ID prefix:
      - FBgn: gene (4-path UNION, 120s timeout)
      - FBal: allele (3-path UNION, 60s timeout)
      - FBti: insertion (direct, 60s timeout)
      - FBco: combination (component alleles, 60s timeout)
      - FBst: stock details (direct lookup, 60s timeout)

    :param feature_id: FlyBase ID (FBgn/FBal/FBti/FBco/FBst)
    :param collection_filter: Optional stock collection name filter (e.g. "Bloomington")
    :return: list of stock dicts
    """
    timeout = 120000 if feature_id.startswith("FBgn") else 60000
    conn = get_connection(statement_timeout_ms=timeout)

    try:
        if feature_id.startswith("FBgn"):
            df = _find_stocks_gene(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBal"):
            df = _find_stocks_allele(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBti"):
            df = _find_stocks_insertion(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBco"):
            df = _find_stocks_combination(conn, feature_id, collection_filter)
        elif feature_id.startswith("FBst"):
            df = _find_stock_details(conn, feature_id)
        else:
            raise ValueError(
                f"Unrecognised ID prefix: {feature_id}. "
                "Expected FBgn, FBal, FBti, FBst, or FBco."
            )

        if df.empty:
            return []
        return df.to_dict(orient="records")
    finally:
        conn.close()
