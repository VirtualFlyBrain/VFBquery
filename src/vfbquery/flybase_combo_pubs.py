"""Find publications linked to FlyBase split system combinations (FBco)."""
import re

import pandas as pd

from .flybase_db import get_connection


def resolve_combination(name_or_id):
    """Resolve a combination name, synonym, or FBco ID.

    Resolution order:
      1. If FBco ID: direct lookup by feature.uniquename
      2. Exact match on feature.name where type = 'split system combination'
      3. Synonym match via feature_synonym (exact =)
      4. Broad ILIKE on both feature.name and synonym.name (UNION), limit 20

    :param name_or_id: Combination name, synonym (e.g. "MB002B"), or FBco ID
    :return: dict with 'match_type' and 'results' list
    """
    conn = get_connection(statement_timeout_ms=30000)
    try:
        return _resolve_combination_impl(conn, name_or_id)
    finally:
        conn.close()


_FEATURE_TYPE = "split system combination"


def _resolve_combination_impl(conn, name_or_id):
    """Internal implementation of resolve_combination."""
    if re.match(r"FBco\d+", name_or_id):
        return _resolve_by_id(conn, name_or_id)
    return _resolve_by_name(conn, name_or_id)


def _run_query(cur, sql, params):
    """Execute a query and return rows + column names."""
    cur.execute(sql, params)
    rows = cur.fetchall()
    return rows


def _resolve_by_id(conn, fbco_id):
    """Resolve by FBco uniquename."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT f.name, f.uniquename
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE f.uniquename = %(uid)s
              AND c.name = %(ftype)s
              AND f.is_obsolete = false
        """, {"uid": fbco_id, "ftype": _FEATURE_TYPE})
        rows = cur.fetchall()

    if rows:
        return {
            "match_type": "EXACT",
            "results": [
                {"name": r[0], "uniquename": r[1], "matched_synonym": None}
                for r in rows
            ],
        }
    return {"match_type": "NOT_FOUND", "results": []}


def _resolve_by_name(conn, name):
    """Try exact name, then synonym, then broad ILIKE."""
    with conn.cursor() as cur:
        # 1. Exact match on feature.name
        cur.execute("""
            SELECT f.name, f.uniquename
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE f.name = %(name)s
              AND c.name = %(ftype)s
              AND f.is_obsolete = false
        """, {"name": name, "ftype": _FEATURE_TYPE})
        rows = cur.fetchall()
        if rows:
            return {
                "match_type": "EXACT",
                "results": [
                    {"name": r[0], "uniquename": r[1], "matched_synonym": None}
                    for r in rows
                ],
            }

        # 2. Synonym match (exact =, not ILIKE)
        cur.execute("""
            SELECT DISTINCT f.name, f.uniquename, s.name AS matched_synonym
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            JOIN feature_synonym fs ON f.feature_id = fs.feature_id
            JOIN synonym s ON fs.synonym_id = s.synonym_id
            WHERE s.name = %(name)s
              AND c.name = %(ftype)s
              AND f.is_obsolete = false
        """, {"name": name, "ftype": _FEATURE_TYPE})
        rows = cur.fetchall()
        if rows:
            return {
                "match_type": "SYNONYM",
                "results": [
                    {"name": r[0], "uniquename": r[1], "matched_synonym": r[2]}
                    for r in rows
                ],
            }

        # 3. Broad ILIKE on name and synonyms
        pattern = f"%{name}%"
        cur.execute("""
            SELECT DISTINCT f.name, f.uniquename
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            WHERE (f.name ILIKE %(pat)s)
              AND c.name = %(ftype)s
              AND f.is_obsolete = false

            UNION

            SELECT DISTINCT f.name, f.uniquename
            FROM feature f
            JOIN cvterm c ON f.type_id = c.cvterm_id
            JOIN feature_synonym fs ON f.feature_id = fs.feature_id
            JOIN synonym s ON fs.synonym_id = s.synonym_id
            WHERE s.name ILIKE %(pat)s
              AND c.name = %(ftype)s
              AND f.is_obsolete = false

            ORDER BY uniquename
            LIMIT 20
        """, {"pat": pattern, "ftype": _FEATURE_TYPE})
        rows = cur.fetchall()
        if rows:
            return {
                "match_type": "BROAD",
                "results": [
                    {"name": r[0], "uniquename": r[1], "matched_synonym": None}
                    for r in rows
                ],
            }

    return {"match_type": "NOT_FOUND", "results": []}


def find_combo_publications(fbco_id):
    """Get all publications linked to a combination via feature_pub.

    :param fbco_id: FlyBase combination ID (e.g. "FBco0000052")
    :return: list of publication dicts with keys:
             fbrf, title, year, miniref, pub_type, doi, pmid, pmcid
    """
    if not fbco_id.startswith("FBco"):
        raise ValueError(f"Expected FBco ID, got '{fbco_id}'")

    conn = get_connection(statement_timeout_ms=60000)
    try:
        return _find_publications_impl(conn, fbco_id)
    finally:
        conn.close()


def _find_publications_impl(conn, fbco_id):
    """Internal implementation of find_combo_publications."""
    with conn.cursor() as cur:
        # Main publications query
        cur.execute("""
            SELECT
                p.uniquename AS fbrf,
                p.title,
                p.pyear AS year,
                p.miniref,
                ct.name AS pub_type
            FROM feature f
            JOIN feature_pub fp ON f.feature_id = fp.feature_id
            JOIN pub p ON fp.pub_id = p.pub_id
            JOIN cvterm ct ON p.type_id = ct.cvterm_id
            WHERE f.uniquename = %(uid)s
              AND f.is_obsolete = false
            ORDER BY p.pyear DESC, p.uniquename
        """, {"uid": fbco_id})
        pub_rows = cur.fetchall()

        if not pub_rows:
            return []

        df = pd.DataFrame(
            pub_rows, columns=["fbrf", "title", "year", "miniref", "pub_type"]
        )

        # Get external IDs (DOI, PMID, PMCID)
        fbrfs = [r[0] for r in pub_rows]
        cur.execute("""
            SELECT p.uniquename AS fbrf, db.name AS db_name, dx.accession
            FROM pub p
            JOIN pub_dbxref pdx ON p.pub_id = pdx.pub_id
            JOIN dbxref dx ON pdx.dbxref_id = dx.dbxref_id
            JOIN db ON dx.db_id = db.db_id
            WHERE p.uniquename = ANY(%(fbrfs)s)
              AND db.name IN ('DOI', 'pubmed', 'PMCID')
        """, {"fbrfs": fbrfs})
        xref_rows = cur.fetchall()

    # Pivot external IDs into columns
    doi_map = {}
    pmid_map = {}
    pmcid_map = {}
    for fbrf, db_name, accession in xref_rows:
        if db_name == "DOI":
            doi_map[fbrf] = accession
        elif db_name == "pubmed":
            pmid_map[fbrf] = accession
        elif db_name == "PMCID":
            pmcid_map[fbrf] = accession

    df["doi"] = df["fbrf"].map(doi_map).fillna("")
    df["pmid"] = df["fbrf"].map(pmid_map).fillna("")
    df["pmcid"] = df["fbrf"].map(pmcid_map).fillna("")

    return df.to_dict(orient="records")
