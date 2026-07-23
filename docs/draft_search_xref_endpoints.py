"""DRAFT endpoint handlers to add to vfbquery/ha_api.py  (plan C1 + C3).

Not wired in yet — this is a review starting point. To adopt:
  1. paste these handlers into ha_api.py (or import them),
  2. register the routes in create_app():
         app.router.add_get("/search", handle_search)
         app.router.add_get("/xref",   handle_xref)
  3. run both through the SAME cache + coalescer + queue wrapper that
     handle_run_query uses (keys suggested below), so /search and /xref inherit
     the pool, request-coalescing, 5-min result cache and 503 backpressure.

Both are read-only Solr lookups (search -> ontology core, xref -> vfb_json core), so
they are cheap and highly cacheable (a workshop's identical searches collapse to one
Solr hit). NB /search is the SAME query as the MCP `search_terms`, not a new engine.
"""
import requests
from aiohttp import web

# Free-text search runs against the *ontology* core (has the autosuggest fields);
# xref lookups run against vfb_json (carries accession + xrefs). VFBquery already
# has `_ont_solr` (ontology) and `vfb_solr` (vfb_json) — reuse those rather than new
# requests sessions when wiring this in.
ONTOLOGY_SOLR = "https://solr.virtualflybrain.org/solr/ontology/select"
VFBJSON_SOLR = "https://solr.virtualflybrain.org/solr/vfb_json/select"


# --------------------------------------------------------------------------- #
# C1 — /search : this is NOT new search logic. It is the *existing* MCP
#      `search_terms` edismax query (VFB3-MCP/dist/index.js ~L468-500) exposed as a
#      cached REST route. resolve_entity is NOT this — that's FlyBase-Chado exact
#      resolution and won't resolve ontology term names.
#      TODO on wiring: factor the query config into ONE shared place with the MCP /
#      website (searchConfiguration.js) so it can't drift into a 3rd/4th copy.
# --------------------------------------------------------------------------- #
def _solr_search(query: str, rows: int = 50,
                 filter_types=None, exclude_types=None, boost_types=None) -> list:
    fq = ["(short_form:VFB* OR short_form:FB* OR facets_annotation:DataSet "
          "OR facets_annotation:pub) AND NOT short_form:VFBc_*"]
    for ft in filter_types or []:
        fq.append(f"facets_annotation:{ft}")
    if exclude_types:
        fq.append("NOT (" + " OR ".join(f"facets_annotation:{et}" for et in exclude_types) + ")")
    bq = ("short_form:VFBexp*^10.0 short_form:VFB*^100.0 short_form:FBbt*^100.0 "
          "short_form:FBbt_00003982^2 facets_annotation:Deprecated^0.001")
    for bt in boost_types or []:
        bq += f" facets_annotation:{bt}^1000.0"
    params = {
        "q": f"{query} OR {query}* OR *{query}*",
        "q.op": "OR", "defType": "edismax", "mm": "45%",
        "qf": "label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest",
        "pf": "true", "bq": bq,
        "fl": "short_form,label,synonym,id,facets_annotation,unique_facets",
        "rows": str(min(rows, 1000)), "wt": "json", "fq": fq,
    }
    r = requests.get(ONTOLOGY_SOLR, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("docs", [])


async def handle_search(request: web.Request) -> web.Response:
    query = request.query.get("query") or request.query.get("q")
    if not query:
        return web.json_response({"error": "Missing required parameter: query"}, status=400)
    rows = int(request.query.get("rows", 50))
    ft = request.query.getall("filter_types", None)
    et = request.query.getall("exclude_types", None)
    # cache key suggestion:  f"search:{query}:{rows}:{ft}:{et}"
    docs = _solr_search(query, rows=rows, filter_types=ft, exclude_types=et)
    return web.json_response({"rows": docs})


# --------------------------------------------------------------------------- #
# C2 — /xref : VFB id <-> external accession, both directions.
#      The accession + data_source live on the Solr doc, and get_term_info
#      carries the full xref list, so this is a direct index lookup.
# --------------------------------------------------------------------------- #
def _solr_by_id(short_form: str) -> list:
    params = {"q": f"short_form:{short_form}", "fl": "short_form,label,xrefs",
              "rows": "1", "wt": "json"}
    r = requests.get(VFBJSON_SOLR, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("docs", [])


def _solr_by_accession(accession: str, db: str | None) -> list:
    # xrefs are indexed as db:accession; match the accession and optionally the db.
    q = f'xrefs:*{accession}*'
    if db:
        q = f'xrefs:*{db}*{accession}* OR xrefs:*{accession}*{db}*'
    params = {"q": q, "fl": "short_form,label,xrefs", "rows": "50", "wt": "json"}
    r = requests.get(VFBJSON_SOLR, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("docs", [])


async def handle_xref(request: web.Request) -> web.Response:
    vfb_id = request.query.get("id")
    accession = request.query.get("accession")
    db = request.query.get("db")
    if not vfb_id and not accession:
        return web.json_response(
            {"error": "Provide either id= or accession=(&db=)"}, status=400)
    # cache key suggestion:  f"xref:{vfb_id or ''}:{accession or ''}:{db or ''}"
    docs = _solr_by_id(vfb_id) if vfb_id else _solr_by_accession(accession, db)
    return web.json_response({"rows": docs})
