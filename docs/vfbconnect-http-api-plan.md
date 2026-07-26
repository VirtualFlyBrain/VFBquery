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

### C1 — `/search` endpoint  ✅ **shipped** — `ec2307f`
The original estimate here was *"S — expose existing, don't build"*, on the assumption that the MCP
`search_terms` query **was** the search. It is not: the search is three stages, and the query is only
the first. The other two — synonym explosion (`refineResults`) and a ~370-line comparator — are what
decide the order a user actually sees, and they lived only in the website's JS. `search_config.py`
ports all three; `/search` serves them.

Everything below the first bullet is the original analysis, kept because it is the evidence for the
decision, with corrections marked.
- **NOT `resolve_entity`:** that is FlyBase-Chado exact resolution (tiered exact→synonym→broad for
  FlyBase features) and is documented as the *wrong* tool for ontology term lookup — it returns
  `NOT_FOUND` on partial/fuzzy anatomy names (verified). Discovery needs `search_terms`.
- **As shipped:** `ha_api.py` `handle_search` + `app.router.add_get("/search", …)` against the
  **`ontology`** core, with all query construction, filtering, boosting, refining and ranking in
  `src/vfbquery/search_config.py`. Params: `query`, `rows` (candidate depth, default 500),
  `limit` (page size), `filter_types` / `exclude_types` (hard `fq`), `boost_types` / `demote_types`
  (soft `bq`, matching the website's filter chips). Runs on its own concurrency budget with bounded
  queueing rather than availability-only shedding — see §7 for the measured numbers.
  `docs/draft_search_xref_endpoints.py` is the superseded draft; it queries but does not rank.
- **Single source of truth:** factor the query config so it isn't a 3rd/4th copy. Checked
  `geppetto-vfb`: there are **six** live copies (the sixth, VFBCircuitBrowser, was found later and
  has its own web-worker sorter and no Class boost), and the website's is **not** the same query as
  `search_terms` — see [`docs/search-config-comparison.md`](search-config-comparison.md). Summary:
  - website ANDs a wildcard OR-group **per token**; `search_terms` wildcards the whole phrase and
    leans on `mm=45%`. Live: `DA1 lPN` → 51 hits vs 718; `MBON-a2` → 39 vs 1585.
  - website hard-excludes `facets_annotation:Deprecated` (`fq`); MCP only demotes it (`bq`).
  - website `bq` floats **types over individuals** (`Class^200`, `FBbt*^150` vs `VFB*^50`) and floats
    `DataSet^500` / `pub^100`; MCP flattens these — hence MCP leading with individuals for `MBON-a2`.
  - factor isolated: for a bare hemibrain bodyId (`1734350908`) MCP's top hit is the **wrong** neuron,
    and the fix is the website's hard `NOT Deprecated` **`fq`**, not the tokenisation.
  - website then explodes synonyms into separate rows and re-ranks with a ~370-line custom JS
    `sorter` — **the order a website user sees is not Solr's order**. This is the stage the original
    estimate missed, and it is also why any "top hit" comparison done at the Solr level — including
    earlier revisions of the comparison doc — described something no user experiences.
  - *(correction)* the website's client also appends an exact-phrase boost
    `label:"<input>"^3000 synonym:"<input>"^1500` to `bq` **at request time**, so it appears in no
    config file. `pf`, which looks like it should be doing that job, is inert everywhere: `pf=true`
    is a silent no-op and even a real field list never fires against the wildcard-expanded `q`.
    Both measured — `python3 docs/compare_search_configs.py --check-pf`.
  - two of the six copies (spotlight, geppetto-client default) still use the pre-migration schema
    (`type:class`, `ontology_name`, `is_defining_ontology`, `is_obsolete`) and one points at
    **solr-dev**; confirm whether they are dead code.
  **Decided:** serve the website's construction + boosts and port the sorter server-side. See §6.
  Then have website / MCP / client all call `/search` rather than Solr directly.
- **Accept:** `search=DA1 lPN` returns `FBbt_00067363` as the top hit (verified live — true of *both*
  configs, so it does not discriminate between them; use the `MBON-a2` and bodyId cases for that).

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

- **Canonical search config** *(was open question 0)* → **the website's**: its `q` construction, `fq`,
  `bq` boosts, runtime phrase boost, `refineResults` synonym explosion and comparator, all ported into
  `src/vfbquery/search_config.py` and served by `/search`. Rationale: it is the ranking every VFB user
  is already used to, it is measurably more precise, and it fixes the bodyId-resolves-to-a-deprecated-
  term bug. This collapses six configs to one and puts the cache in front of Solr.
  - The client no longer has any Solr configuration at all, so `q_mode` is gone rather than defaulted.
  - **Consequence, and the remaining work is outside this repo:** the website's
    `datasourceConfiguration` and the MCP's `search_terms` should now call `/search` too. Until they
    do, this is a *fourth* consumer agreeing with the website rather than a genuine single source.
  - **Known bug inherited deliberately:** the config cannot retrieve some exact labels. `neuron`
    (FBbt_00005106) is absent from all 1370 ranked rows, and `bq` pushes it *down* (99th by score with
    `bq=""`, 705th with the boosts). The port is faithful; the config has the bug. Fixing it —
    probably `label_autosuggest_e:"<input>"^<big>` rather than `label:"<phrase>"` — is a change to VFB
    search behaviour and wants sign-off, not a quiet fix inside a port. See comparison doc §5.

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

### Done for `/search`

**Ranking parity with the real website JS.** `docs/search-parity/` runs the actual
`refineResults` + `sorter` under Node against the Python port on the same Solr response:
`python3 docs/search-parity/check_parity.py`. All 22 hand-picked cases and 78 queries identical.
Re-run it after touching `search_config.py` §3 (refine) or §4 (sort) — the comparator is
non-transitive, so both TimSorts *tend* to agree but are not guaranteed to, which makes this a
measurement and not a proof.

**No drift from the HTTP layer.** 15 cases through `/search` match module-level `search()`
byte-for-byte on rows and counts.

**Load, measured against the 80-at-peak target.** Two things the reading did not tell me:

| case | result |
|---|---|
| 80 concurrent *distinct* queries (worst case: nothing cacheable, nothing coalescable) | all 200; p50 2445 ms, max 3522 ms |
| 160 concurrent distinct | all 200; max 3941 ms |
| realistic workshop shape (a room on the same handful of exercise queries) | p50 31 ms, >1000 req/s |
| same query cold → warm | 611 ms → 1 ms |
| 8 identical concurrent | 1 Solr fetch, 7 coalesced |
| genuine saturation (`--search-queue-wait 0.5`) | sheds with 503 + `Retry-After` |

The first row is why the queueing is bounded-wait rather than availability-only: the first
implementation refused the moment the semaphore was full and returned `{503: 40, 200: 40}` at 80
concurrent — half the room seeing an error to avoid a recoverable few seconds of queueing. That was
found by running it, not by reading it.
