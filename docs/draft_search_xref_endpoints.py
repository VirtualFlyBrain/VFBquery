"""DRAFT endpoint handlers to add to vfbquery/ha_api.py  (plan C1 + C3).

Not wired in yet — this is a review starting point. To adopt:
  1. paste these handlers into ha_api.py (or import them),
  2. register the routes in create_app():
         app.router.add_get("/search", handle_search)
         app.router.add_get("/xref",   handle_xref)
  3. run both through the SAME cache + coalescer + queue wrapper that
     handle_run_query uses (keys suggested below), so /search and /xref inherit
     the pool, request-coalescing, 5-min result cache and 503 backpressure.

Both are read-only Solr lookups against the vfb_json core, so they are cheap and
highly cacheable (a workshop's identical searches collapse to one Solr hit).
"""
import json
import requests
from aiohttp import web

SOLR = "https://solr.virtualflybrain.org/solr/vfb_json/select"


# --------------------------------------------------------------------------- #
# C1 — /search : free-text term search (mirrors the MCP search_terms / website
#      spotlight edismax config: qf on label/synonym/autosuggest, exact-match to
#      top, optional facet filters).
# --------------------------------------------------------------------------- #
def _solr_search(query: str, rows: int = 50, filters: str | None = None) -> list:
    params = {
        "defType": "edismax",
        "q": query,
        "q.op": "OR",
        "qf": "label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest",
        "pf": "true",  # phrase boost -> exact/leading matches rise to the top
        "fl": "short_form,label,synonym,types:facets_annotation,unique_facets",
        "rows": str(rows),
        "fq": "(short_form:VFB* OR short_form:FB*) AND NOT short_form:VFBc_*",
        "wt": "json",
    }
    if filters:
        # caller-supplied fq, e.g. "facets_annotation:Neuron" or a dataset filter
        params["fq"] = f'({params["fq"]}) AND ({filters})'
    r = requests.get(SOLR, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("docs", [])


async def handle_search(request: web.Request) -> web.Response:
    query = request.query.get("query") or request.query.get("q")
    if not query:
        return web.json_response({"error": "Missing required parameter: query"}, status=400)
    rows = int(request.query.get("rows", 50))
    filters = request.query.get("filters")
    # cache key suggestion:  f"search:{query}:{rows}:{filters}"
    docs = _solr_search(query, rows=rows, filters=filters)
    return web.json_response({"rows": docs})


# --------------------------------------------------------------------------- #
# C2 — /xref : VFB id <-> external accession, both directions.
#      The accession + data_source live on the Solr doc, and get_term_info
#      carries the full xref list, so this is a direct index lookup.
# --------------------------------------------------------------------------- #
def _solr_by_id(short_form: str) -> list:
    params = {"q": f"short_form:{short_form}", "fl": "short_form,label,xrefs",
              "rows": "1", "wt": "json"}
    r = requests.get(SOLR, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("response", {}).get("docs", [])


def _solr_by_accession(accession: str, db: str | None) -> list:
    # xrefs are indexed as db:accession; match the accession and optionally the db.
    q = f'xrefs:*{accession}*'
    if db:
        q = f'xrefs:*{db}*{accession}* OR xrefs:*{accession}*{db}*'
    params = {"q": q, "fl": "short_form,label,xrefs", "rows": "50", "wt": "json"}
    r = requests.get(SOLR, params=params, timeout=30)
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
