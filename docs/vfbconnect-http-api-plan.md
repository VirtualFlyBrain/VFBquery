# Plan — expose VFB Connect basic queries as an HTTP API (via VFBquery / v3-cached)

**Goal.** Let users (and the workshop notebooks) run the common `vfb_connect` queries over HTTP with
**zero client install** — no `navis`, no `setuptools<58` pin, no 2–3-min term-cache launch — by
**extending the existing VFBquery `ha_api`** (served at `v3-cached`) rather than building a new service.

**Principle (agreed).** Most graph queries already exist in `ha_api`. What's missing is a *front door*
(search / id-resolution) and *output shaping* (query schemas → DataFrames), plus a couple of small new
endpoints. We add those and a thin pure-`requests` client; we do **not** reimplement `vfb_connect`.

---

## 1. Current state (verified in code)

`ha_api.py` (aiohttp) already provides, at `v3-cached`:

- **Endpoints:** `/get_term_info`, `/run_query?id=&query_type=`, `/query_connectivity`,
  `/resolve_entity`, `/resolve_combination`, `/find_stocks`, `/find_combo_publications`,
  `/list_connectome_datasets`, `/get_hierarchy`, `/get_hierarchy_html`, `/health`, `/status`.
- **~40 `run_query` query_types**, incl. `ListAllAvailableImages` (=instances), `SubclassesOf`,
  `PartsOf`, `NeuronsPartHere/Synaptic/Pre|PostsynapticHere/CapableOf`,
  `Up|DownstreamClassConnectivity`, `NeuronNeuronConnectivityQuery`, `NeuronInputsTo`,
  `SimilarMorphologyTo` (+variants), `anatScRNAseqQuery`, `clusterExpression`, `scRNAdatasetData`,
  `AnatomyExpressedIn`, `TransgeneExpressionHere`, `AllDatasets`, `TermsForPub`, `FindStocks`.
- **Serving infra already built:** `ProcessPoolExecutor` (default 10 workers, `--workers` /
  `VFBQUERY_WORKERS`), request **coalescing** (identical in-flight queries share a worker), in-memory
  **result cache** (TTL 300 s), **queue-depth backpressure** (503), security middleware, version in
  `/health` & `/status`. Helper clients present: `owlery_client.py`, `solr_fetcher.py`,
  `solr_result_cache.py`.

So the connectivity / NBLAST / transcriptomics / instances / term-info surface is **already cached and
HTTP-served**.

## 2. `vfb_connect` method → backend mapping

| `vfb_connect` method (workshop use) | Backing on v3-cached | Status |
|---|---|---|
| `term` / `terms` / `get_TermInfo` | `/get_term_info` | ✅ covered |
| `get_instances(named type)` | resolve → `run_query ListAllAvailableImages` | ✅ covered (needs shaping) |
| `get_subclasses` / `get_superclasses` | `run_query SubclassesOf` / hierarchy | ✅ covered |
| `get_connected_neurons_by_type` | `/query_connectivity`, `Up/DownstreamClassConnectivity` | ✅ covered |
| `get_neurons_downstream_of/upstream_of` (individual) | `run_query NeuronNeuronConnectivityQuery` / `NeuronInputsTo` | ✅ covered |
| `get_similar_neurons` (NBLAST) | `run_query SimilarMorphologyTo` | ✅ covered |
| `get_transcriptomic_profile` / scRNAseq | `anatScRNAseqQuery` / `clusterExpression` / `scRNAdatasetData` | ✅ covered |
| `get_datasets` / connectomes | `run_query AllDatasets` / `/list_connectome_datasets` | ✅ covered |
| NT predictions | inside `/get_term_info` | ✅ covered (no work) |
| `search` (free-text) | Solr `edismax` — logic in MCP `search_terms`, **not yet an `ha_api` route** | ➕ add `/search` |
| `xref_2_vfb_id` / `get_terms_by_xref` | only FlyBase resolution today | ➕ add `/xref` |
| `get_terms_by_region` (arbitrary `overlaps some X`) | approximated by `NeuronsPartHere`/`PartsOf`; exact = Owlery | ⚠️ interim OK, full = Owlery phase |
| arbitrary OWL class expressions | `owlery_client.py` exists, not exposed | ⏳ later (Manchester phase) |
| `get_vfb_link` | pure client-side URL builder | 🔵 client-side |
| navis skeleton load / NBLAST *compute* / 3D plot | heavy client ops | 🔵 stays client-side / static files |

## 3. Changes to make

### C1 — `/search` endpoint  *(effort: S — expose existing, don't build)*
This is **not new search logic.** The free-text search already exists as the MCP `search_terms`
tool: an `edismax` query against the Solr **`ontology`** core (VFBquery already has `_ont_solr`
pointed there). C1 just exposes that same query as a cached REST route so the client uses one
canonical implementation.
- **NOT `resolve_entity`:** that is FlyBase-Chado exact resolution (tiered exact→synonym→broad for
  FlyBase features) and is documented as the *wrong* tool for ontology term lookup — it returns
  `NOT_FOUND` on partial/fuzzy anatomy names (verified). Discovery needs `search_terms`.
- **File:** `ha_api.py` — add `handle_search` + `app.router.add_get("/search", …)` calling the
  **`ontology`** core (`_ont_solr`), reusing the exact `search_terms` params:
  `q = "<q> OR <q>* OR *<q>*"`, `mm=45%`, `qf=label^110 synonym^100 …autosuggest`, `bq` boosts,
  `fq` VFB/FB filter, plus `filter_types` / `exclude_types` / `boost_types`.
  See `docs/draft_search_xref_endpoints.py` for the drafted handler.
- **Single source of truth:** factor the query config so it isn't a 3rd/4th copy (website
  `searchConfiguration.js`, MCP `search_terms`, here). Ideally share one config module.
- **Accept:** `search=DA1 lPN` returns `FBbt_00067363` as the top hit (verified live).

### C2 — typed-column → DataFrame adapter  *(effort: S, client-side)*
Query schemas return typed columns; a few cells are pipe-joined multi-values or HTML links/thumbnails.
Build a fixed coercion map (scalar / list / link / image) driven by the schema's declared column types.
- **Where:** the client wrapper (C6), not the server.
- **Accept:** `run_query … ListAllAvailableImages` for DA1 lPN → a 68-row DataFrame matching today's
  `vfb.get_instances(...)` columns (label/id/data_source/dataset/templates).

### C3 — `/xref` bidirectional id converter  *(effort: S–M)*
VFB id ↔ external accession (neuPrint bodyId, FlyWire root id, CATMAID skeleton id, FlyBase). Data is
already indexed (instance rows carry `accession`+`data_source`; `get_term_info` carries xrefs).
- **File:** `ha_api.py` + a small Solr lookup helper.
- **Shape:** `GET /xref?id=VFB_jrchjtdb` → list of `{db, accession}`; `GET /xref?accession=1734350908&db=neuprint` → `{VFB id, label}`.
- **Accept:** round-trips a known hemibrain bodyId ↔ `VFB_jrchjtdb`.

### C4 — VFB link + 3D scene  *(effort: link S, render L)*
- **Link (S):** client-side builder from returned `VFB_id`/template; optionally `/scene_link?ids=…&template=…`
  returning a geppetto-vfb viewer URL that opens with those IDs loaded (viewer already accepts ID lists).
- **Render (optional, L):** `/scene?ids=…&template=…` → server-rendered PNG/GLB of N neurons. Bigger job
  (headless render); keep off the shared request path or gate/queue it hard. Nice shareable workshop output.

### C5 — Owlery / Manchester passthrough + `/combine`  *(effort: M, later)*
For arbitrary compositions ("cholinergic neurons with presynaptic terminals in the fan-shaped body").
- **Interim:** `/combine` doing ∪ / ∩ / − over id-sets from the existing named query_types (covers ~80%).
- **Full:** Manchester-syntax → `owlery_client` passthrough (already in the repo) → id set → hydrate.
- **Accept:** a 2-term intersection matches the equivalent `vfb_connect` Owlery query.

### C6 — thin client wrapper  *(effort: S–M)* — **this is what makes access "simpler"**
A pure `requests` + `pandas` package (installs instantly, Colab-friendly, no navis/setuptools issues)
exposing the familiar names — `get_instances`, `get_connected_neurons_by_type`, `get_similar_neurons`,
`get_transcriptomic_profile`, `term(s)`, `search`, `xref`, `get_vfb_link` — each mapping to a v3-cached
call + the C2 adapter. Two viable homes (decide in §6):
- **(a)** new tiny package `vfbquery-client` / `vfb-remote` (zero heavy deps), **or**
- **(b)** a `remote=True` mode inside `vfb_connect` that routes basic queries to HTTP and falls back to
  the local library for heavy ops (one package, one API).
- **Accept:** the workshop's route-A cells run unchanged against HTTP with no `navis`/`setuptools` install.

## 4. Deployment & scaling — 80 concurrent at peak

The workshop shape is the win: 80 people run the **same** cells on the **same** example (DA1 lPN), so
coalescing + the 5-min result cache collapse them to ~1 backend hit each. Therefore:

- **Warm on startup**, gate traffic behind a readiness probe (pay the term-cache cost once, before
  attendees arrive).
- **Worker pool ~10–16** (protects Neo4j); it must stay a **process** pool — `VfbConnect`/query workers
  aren't thread-safe and each holds a large cache.
- **2+ replicas** behind the LB on the existing k8s/Rancher for HA; deploy alongside `vfb3-mcp`.
- **Per-IP rate limit**; keep the 503 backpressure.
- **Keep off the shared box:** navis skeleton loading, NBLAST *computation*, 3D rendering. Skeletons come
  from existing static SWC/mesh URLs; only C4-render (if built) is server-side and must be queued.

## 5. Phasing

- **Phase 1 — workshop-ready (minimal):** C1 `/search`, C2 adapter, C6 client wrapper → point notebooks
  at HTTP as the zero-install route A. Everything else already exists.
- **Phase 2:** C3 `/xref`, C4 scene-link.
- **Phase 3 — post-workshop / power users:** C5 Owlery+`/combine`, C4 scene render, full
  `get_terms_by_region` via Owlery.

## 6. Decisions & open questions

**Decided (this round):**
- **Endpoint namespace** → **extend the existing `v3-cached` / `ha_api` paths** (add `/search`, `/xref`
  alongside the current routes). One service, one deploy.
- **Client wrapper home** → **new lightweight package** `vfbquery-client` (requests + pandas only, no
  navis / no `setuptools<58`), scaffolded in this branch under `clients/vfbquery-client/`.

**Still open:**
3. **Deploy target** — extend the `ha_api` image/replica, or a sibling service sharing the Solr cache?
4. **Auth / rate-limit policy** for a public endpoint (per-IP is probably enough for a workshop).
5. **Scene feature scope** — link-only for now, or commit to server-side render?
6. **Package publish** — confirm PyPI name `vfbquery-client`, and whether it ships from this repo's CI.

## 7. Test plan

Reuse the existing `test_ha_api_validation.py` pattern: unit tests per new endpoint (`/search`, `/xref`),
adapter round-trip tests (schema → DataFrame parity with `vfb_connect` outputs on DA1 lPN), and a load
test at **80 concurrent** hitting a shared query to confirm coalescing + cache hold the backend to ~1
hit and the 503 backpressure behaves.
