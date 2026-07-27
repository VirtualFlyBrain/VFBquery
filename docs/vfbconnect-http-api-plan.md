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
  `/list_connectome_datasets`, `/get_hierarchy`, `/health`, `/status`. (`/get_hierarchy` was a
  registered route absent from `ALLOWED_PATHS` — in-cluster only, in effect — and is published in
  this branch; see the resolved item below. `/get_hierarchy_html` remains in-cluster.
  `_warn_unreachable_routes` logs any such divergence at startup rather than leaving it to be
  rediscovered as a mystery 404.)
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
| `search` (free-text) | three stages, not one: `edismax` + `refineResults` + the website comparator, all ported to `search_config.py` | ✅ `/search` (C1) |
| `xref_2_vfb_id` / `get_terms_by_xref` | `term_info.xrefs`; no accession is indexed, so reverse = search + exact confirm | ✅ `/xref` (C3) |
| `get_terms_by_region` (arbitrary `overlaps some X`) | approximated by `NeuronsPartHere`/`PartsOf`; exact = Owlery | ⚠️ interim OK, full = Owlery phase |
| boolean combinations of the above ("in the calyx **and** the lateral horn", "MB dopaminergic **but not** octopaminergic") | bracketed expression over query results, matched on the `selection_id` column | ✅ `/combine` (C5) |
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
- **Single source of truth:** factor the query config so it isn't a 3rd/4th copy. Counted across three
  repos: **six** copies — four in `geppetto-vfb` (main overlay, query builder, spotlight, and
  VFBCircuitBrowser, which was found later and has its own web-worker sorter and no Class boost), one
  in the pinned `geppetto-client` library, one in `VFB3-MCP` — and the website's is **not** the same query as
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

### C2 — typed-column → DataFrame adapter  ✅ **shipped**
Query schemas return typed columns; a few cells are pipe-joined multi-values or HTML links/thumbnails.
- **Where:** the client wrapper (C6), not the server — `VfbClient._to_df`.
- **As shipped:** narrower than the plan. Rather than a coercion map driven by the schema's declared
  column types, it unwraps whichever envelope the endpoint used (`rows`, `connections`, a bare list, or
  a lone object as a one-row frame) and splits the pipe-joined columns named in `_LIST_COLUMNS`. HTML
  link/thumbnail cells are passed through as the HTML the service returns. That is enough for every
  endpoint the client calls; a schema-driven map is worth building when a caller needs the link and
  image columns as structured values, and not before.
- **Accept:** ✅ `get_instances("FBbt_00067363")` returns a DataFrame of >50 rows carrying the
  `data_source` column — `tests/test_smoke.py::test_live_get_instances_da1lpn` (`VFB_LIVE_TESTS=1`).
  Asserted as a floor rather than the planned exact 68, because the instance count moves with the
  data releases. Envelope and list-column behaviour is covered offline by three `_to_df` tests.

### C3 — `/xref` bidirectional id converter  ✅ **shipped**
VFB id ↔ external accession (neuPrint bodyId, FlyWire root id, CATMAID skeleton id, FlyBase).

The estimate assumed accessions were "already indexed". They are not, and that is the whole shape of
the implementation. Both Solr schemas were enumerated: neither core has an accession field, and on
`vfb_json` the `term_info` blob that *does* carry the xrefs is `indexed=false` (nor is it reachable via
the `_text_` catch-all — checked). So there is no query that finds a term by accession.

- **As shipped:** `ha_api.py` `handle_xref` + `/xref` in both the route table and `ALLOWED_PATHS`,
  sharing `/search`'s result cache, coalescer and Solr concurrency budget.
  - **Forward** (`?id=`): one `vfb_json` fetch, flatten `term_info.xrefs`.
  - **Reverse** (`?accession=`, optional `&db=`): the canonical `/search` for the accession, then an
    **exact confirmation** of each candidate against its own xref list — a row is returned only if
    that term really carries that accession. This is the point of the endpoint, not a formality:
    free-text search on a bare numeric bodyId will happily rank a near-miss first, which is exactly
    how the MCP came to resolve one to the wrong neuron.
  - `db` is optional and matches a site's symbol (`hb`), short_form
    (`neuprint_JRC_Hemibrain_1point2point1`) or label, whole-string and case-insensitively.
  - Rows: `id`, `label`, `db`, `db_label`, `site_id`, `accession`, `is_data_source`, `link`.
- **Known limit** (documented on the handler, not worked around): reverse lookup only reaches terms
  the search reached, and the only reason an accession is searchable at all is that VFB writes it into
  the label — `DA1_lPN_R (FlyEM-HB:1734350908)`. Connectome bodyIds therefore resolve; an accession
  appearing in no indexed text returns **no rows**. Empty is the correct answer until an accession
  field exists; the alternative is returning a plausible wrong neuron.
- **Accept:** ✅ round-trips a known hemibrain bodyId ↔ `VFB_jrchjtdb`, both directions, live —
  `clients/vfbquery-client/tests/test_smoke.py::test_live_xref_round_trips_a_hemibrain_bodyid`
  (`VFB_LIVE_TESTS=1`). Shaping logic covered offline by `tests/test_xref.py`.

### C4 — VFB link + 3D scene  *(effort: link S, render L)*
- **Link (S):** client-side builder from returned `VFB_id`/template; optionally `/scene_link?ids=…&template=…`
  returning a geppetto-vfb viewer URL that opens with those IDs loaded (viewer already accepts ID lists).
- **Render (optional, L):** `/scene?ids=…&template=…` → server-rendered PNG/GLB of N neurons. Bigger job
  (headless render); keep off the shared request path or gate/queue it hard. Nice shareable workshop output.

### C5 — `/combine` set algebra  ✅ **shipped**  ·  Owlery / Manchester passthrough *(still later)*
For arbitrary compositions ("cholinergic neurons with presynaptic terminals in the fan-shaped body").
The interim half is built and is larger than the estimate: not ∪ / ∩ / − over id-sets but a full
bracketed boolean expression over an arbitrary number of queries, with the result *explained*.
Reference: [`docs/combine-endpoint.md`](combine-endpoint.md).

- **As shipped:** `src/vfbquery/combine.py` (840 lines, stdlib-only) + `handle_combine` in `ha_api.py`,
  `/combine` in both the route table and `ALLOWED_PATHS`.
  - **Expression, not a fixed pair.** `GET /combine?expr=a AND [b NOT c]&a=…&b=…&c=…`. Each name is
    bound to an operand by its own query parameter, so the arity is open — up to
    `MAX_COMBINE_OPERANDS` (12, `VFBQUERY_MAX_COMBINE_OPERANDS`) per request, and past that you stage a
    result back in as `ids:`. `expr` is capped at `MAX_COMBINE_EXPR_LEN` (2000 chars).
  - **Operators:** `AND OR NOT XOR NAND NOR XNOR`, each also reachable by the words people actually
    type (`both`, `either`, `but not`, `only one of`, …) and by `& | - ^ !`. Precedence is
    `OR/NOR` loosest → `XOR/XNOR` → `AND/NAND/NOT` tightest, left-associative, overridable with
    `[…]` (preferred in URLs) or `(…)`.
  - **Operands take three forms:** `<QueryType>:<id>` (any of the ~40 `QUERY_TYPE_MAP` entries),
    `search:<text>` (goes through C1), and `ids:<id>,<id>,…` (a set you already have — costs no query
    and is how you exceed the operand limit).
  - **Explained, not just answered.** Every response carries `as_read` (the expression with the
    brackets the parser actually applied), `plain_english`, and a `steps` list — one record per
    operation with `operation`, `description`, `input_counts`, `result_count`, and `why_empty` when a
    step returns nothing for a diagnosable reason. `explain_only=true` returns all of that having run
    **no** queries, which is the cheap way to check you meant what you wrote.
  - **Matching is on the identity column, not "the first column".** Rows are matched on the header
    whose declared `type` is `selection_id` — the same column the website uses for "add to search".
    Verified present on 11 of 12 query types; `NeuronInputsTo` is the exception (plain `id`) and is
    covered by an explicit fallback list. Duplicate ids fold to one term
    (`DownstreamClassConnectivity` on `FBbt_00049825` is 8,935 rows over 894 terms).
  - **Lossless column merge** *(explicitly requested)*. The output row for a term carries every column
    every contributing operand had for it. Same-named columns that agree collapse to one; where they
    disagree the operand-qualified `column__operand` is kept alongside, so no cell is discarded.
    `found_in` / `found_in_count` record which operands produced the term. Merged headers inherit
    their type from the source query and gain `from_query`, so the DataFrame adapter (C2) and the
    website's renderers still know what each column is.
  - **Refuses rather than guesses.** Undefined name, unparseable expression, unknown query type,
    unclosed bracket, missing operator → 400 with a sentence saying which. A namespace mismatch
    (`FBbt_` ∩ `VFB_` can only ever be empty) is diagnosed in words on the step instead of being
    returned as a bare zero. An operand truncated by `RESULT_ROW_CAP` warns, and `require_complete=1`
    turns that into a 409 — because a set operation over a silently truncated input is wrong, not
    partial.
  - **The universe is explicit.** `NOT`/`NAND`/`NOR`/`XNOR` need one; the default is the union of the
    operands used, which makes `NOR` always empty and collapses `NAND`≡`XOR`, `XNOR`≡`AND`. Rather
    than hide that, the four degeneracies are named in the warnings and `universe=` takes any operand
    form to fix it.
  - **Costs the same as calling `/run_query` yourself.** Operands execute on the existing pool,
    coalescer and result cache, with **byte-identical cache keys** to the direct `/run_query` call —
    so a workshop room where 80 people combine the same two queries pays for two backend hits, and an
    operand repeated inside one expression runs once.
- **Deliberately *not* in this half:** Manchester syntax → `owlery_client` passthrough (already
  vendored) → id set → hydrate. That is what covers compositions no named query_type expresses; the
  set algebra covers the ~80% that are combinations of ones that do.
- **Accept:** ✅ offline — `tests/test_combine.py` (65) for the language, matching, universe and merge;
  `tests/test_combine_endpoint.py` (30) for the handler, including a real-dispatch layer asserting the
  shared cache entry, that `a AND [b OR a]` runs two queries not three, and that a full queue sheds the
  whole combination as one 503. Client: `combine()` / `explain_combination()` plus 8 tests, and a
  live-gated calyx ∩ lateral-horn intersection. ~20 worked biological examples with counts verified
  live on 2026-07-27 are in `docs/combine-endpoint.md` §8.
- **Still open (Owlery half):** a 2-term Manchester intersection matching the equivalent
  `vfb_connect` Owlery query.

### C6 — thin client wrapper  ✅ **shipped** — **this is what makes access "simpler"**
A pure `requests` + `pandas` package (installs instantly, Colab-friendly, no navis/setuptools issues)
exposing the familiar names, each mapping to a v3-cached call + the C2 adapter. Home **(a)** was taken
(see §6): `clients/vfbquery-client/`, package `vfbquery_client`, class `VfbClient`.
- **As shipped:** `term`, `terms`, `search`, `xref`, `get_instances`, `get_subclasses`,
  `get_connected_neurons_by_type`, `get_neuron_connectivity`, `get_similar_neurons`,
  `get_transcriptomic_profile`, `list_connectome_datasets`, `get_vfb_link`. Name/symbol arguments are
  resolved through `/search`, so the client carries no Solr configuration of its own. Server-side
  `warnings` are re-raised as Python warnings rather than dropped, because an unresolved type is
  otherwise indistinguishable from an unconnected pair.
- Rejected option **(b)**, a `remote=True` mode inside `vfb_connect`: it would keep the heavy install
  on the path it was meant to remove.
- **Accept:** ⏳ partially. The client installs from its own pyproject with `requests` + `pandas` only,
  and the CI leg for it installs on 3.8 and 3.11 (`docs/ci/search-gates.yml`, one `git mv` from
  active — see §CI). Running the
  workshop's route-A cells against it is **not** demonstrated here — the notebooks live in the
  `neurofly2026-workshop` repo and repointing them is a separate change.

## 4. Deployment & scaling — 80 concurrent at peak

The workshop shape is the win: 80 people run the **same** cells on the **same** example (DA1 lPN), so
coalescing + the 5-min result cache collapse them to ~1 backend hit each. Therefore:

- **Warm on startup**, gate traffic behind a readiness probe (pay the term-cache cost once, before
  attendees arrive).
  - **Not only a latency measure — a correctness one, on evidence.** The first end-to-end run of
    `scripts/check_gates.sh` failed gate 5 with `10 > 50` on `get_instances(FBbt_00067363)`. The cause was
    upstream, not in this branch (a re-run against the warm server passed 4/4): Neo4j answered 503, so
    `vfb_queries.get_instances` fell back to the SOLR `anatomy_channel_image` extract and returned **10 of
    68 rows as an HTTP 200 with nothing marking it partial** — the same class of defect this branch has
    been removing elsewhere (confirm-don't-guess in `/xref`, `warnings` surfaced for
    `/query_connectivity`). Fixed on both sides of the wire: the fallback now attaches `warnings` to its
    dict payload (the repo's existing convention) and the client re-raises any endpoint's `warnings` as
    Python warnings from `_get`, so a degraded answer can no longer pass for a complete one. What that
    does **not** fix is that a replica whose Neo4j is unreachable still serves traffic; the readiness
    probe is what should keep it out of the LB until it can answer properly. With 80 attendees running
    the same cell, one such replica is a fifth of the room getting a quietly wrong answer.
- **Worker pool ~10–16** (protects Neo4j); it must stay a **process** pool — `VfbConnect`/query workers
  aren't thread-safe and each holds a large cache.
- **2+ replicas** behind the LB on the existing k8s/Rancher for HA; deploy alongside `vfb3-mcp`.
- **Per-IP rate limit**; keep the 503 backpressure.
- **Keep off the shared box:** navis skeleton loading, NBLAST *computation*, 3D rendering. Skeletons come
  from existing static SWC/mesh URLs; only C4-render (if built) is server-side and must be queued.

## 5. Phasing

- **Phase 1 — workshop-ready (minimal):** ~~C1 `/search`, C2 adapter, C6 client wrapper~~ — all three
  shipped in this branch. The one step left in the phase is outside this repo: point the workshop
  notebooks at the client as the zero-install route A.
- **Phase 2:** ~~C3 `/xref`~~ (shipped in this branch — see above), C4 scene-link.
- **Phase 3 — post-workshop / power users:** ~~C5 `/combine`~~ (shipped in this branch — it turned out
  to be workshop material rather than power-user material: "neurons in the calyx **and** the lateral
  horn" is the first question an attendee asks after two searches), C5 Owlery/Manchester passthrough,
  C4 scene render, full `get_terms_by_region` via Owlery.

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
  term bug. This is what *lets* six configs collapse to one and puts the cache in front of Solr.
  - The client no longer has any Solr configuration at all, so `q_mode` is gone rather than defaulted.
  - **Consequence, and the remaining work is outside this repo:** the website's
    `datasourceConfiguration` and the MCP's `search_terms` should now call `/search` too. Until they
    do the collapse has not happened yet: all six copies still exist, so `/search` is a *seventh*
    implementation with exactly **one** consumer (`clients/vfbquery-client`, which used to be a copy
    itself). Three consumers — website, MCP, client — is the target and the point at which "single
    source of truth" stops being an intention. See `docs/search-config-comparison.md` §4.
  - **Exact-label retrieval bug — found in the port, fixed with sign-off.** The website's config
    cannot retrieve some exact labels: `neuron` (FBbt_00005106) was absent from all 1370 ranked rows,
    and `bq` pushed it *down* (99th by score with `bq=""`, 705th with the boosts). The port was
    faithful; the config had the bug. The cause is that the phrase-boost halves
    (`label:"<term>"^3000` + `synonym:"<term>"^1500`) are **additive**, so a term whose label *is* the
    query but which has no redundant synonym scores 3000 against a competitor's 4500.
    The first guess in this doc — `label_autosuggest_e` — was wrong: that field does not exist in the
    `ontology` schema. The fix that shipped is `label_str:"<term>"^6000` appended to `bq`, where
    `label_str` is the existing `copyField` of `label` into the `*_str` dynamic field (`strings`,
    `docValues=true`) and so is a whole-field, case-sensitive exact match. Four capitalisations are
    emitted to cover VFB's mixed-case labels.
    Measured on 43 sampled live labels: recall 42 → 43, rank-0 41 → 42, `neuron` miss → rank 0,
    top-10 churn **0** across ten unrelated queries, and no extra Solr requests. Guarded by
    `check_recall.py --gate` (see comparison doc §5) because a *retrieval* regression is structurally
    invisible to the parity gate.

**Still open:**
2. ~~**`/get_hierarchy` and `/get_hierarchy_html`**~~ — **resolved.** `/get_hierarchy` is now in
   `ALLOWED_PATHS`: it is an ordinary query — the `part_of` or `subclass_of` tree around a term —
   and nothing about it needed to be private beyond nobody having asked. `/get_hierarchy_html` stays
   in-cluster: it is the pre-rendered markup the geppetto site's ROI browser consumes, produced by
   the same worker, so publishing it would make one consumer's HTML part of the API's compatibility
   surface for no gain. `_warn_unreachable_routes` still logs the remaining divergence at startup.
3. **Deploy target** — extend the `ha_api` image/replica, or a sibling service sharing the Solr cache?
4. **Auth / rate-limit policy** for a public endpoint (per-IP is probably enough for a workshop).
5. **Scene feature scope** — link-only for now, or commit to server-side render?
6. **Package publish** — confirm PyPI name `vfbquery-client`, and whether it ships from this repo's CI.

## 7. Test plan

Unit tests per new endpoint (`/search`, `/xref`, `/combine`), adapter round-trip tests (schema → DataFrame parity
with `vfb_connect` outputs on DA1 lPN), and a load test at **80 concurrent** hitting a shared query to
confirm coalescing + cache hold the backend to ~1 hit and the 503 backpressure behaves.

### One command

```bash
scripts/check_gates.sh          # unit + client + parity + recall + live
```

Five gates, five different reasons, one exit code: everything under `tests/` (offline — `/xref`
shaping, the `/search` and `/xref` handler tests, and the shed / coalescing / cancellation regressions
in `test_shed_coalescing.py` and `test_resilience.py`), the client's request-shaping tests,
`check_parity.py` (ordering vs the real website JS, needs node and a `geppetto-vfb` checkout),
`check_recall.py --gate` (the exact-label boost, hits the live index), and the client's **live** tests
run against a server started from this checkout. That last one exists because `/search` and `/xref` are
not on the public deploy yet, so pointing `VFB_LIVE_TESTS=1` at `v3-cached` would only ever prove their
absence; started locally they are a real pre-merge gate, and they are the only place the `/xref` round
trip runs end to end. The first gate is the whole directory rather than a list of files, so a test
added later is covered by having been written rather than by also remembering to name it here — the
`--no-deps` round taught me that a test which runs nowhere is indistinguishable from one that does not
exist. A missing prerequisite is a **failure**, not a pass — "could not check" and "checked, fine" must
not look alike from the exit code, and the script refuses outright if `vfbquery` is not importable
rather than dying at collection with a bare `ModuleNotFoundError`. `--skip-parity`, `--skip-recall` and
`--skip-live` are the explicit opt-outs (`--offline` is all three) and each says so in the summary;
`--seed N` sets the **parity** gate's fuzz draw (the recall gate takes no seed; its corpus is sampled
by `check_recall.py` itself), and the script rejects a `--seed` with no value rather than silently
running the default sample. Exit codes are distinct on purpose: 1 is a gate that failed, 2 is an
environment that could not run one.

**In CI** (`docs/ci/search-gates.yml` — see the note below on why it is not yet in
`.github/workflows/`): the offline gates run on pushes to `main`, `dev` and
`feature/**` and on PRs into `main` or `dev`; the live ones run weekly and on demand. Splitting them is
deliberate — `parity` and `recall` measure this branch against things that move on their own (the
website's JS, the ontology), so putting them on the merge path would turn somebody else's release into
this branch's red build, and a green run would have a shelf life either way. The catch is that
`schedule` and `workflow_dispatch` only fire from the default branch, so while this branch is unmerged
the live job cannot be triggered at all — which is the other reason `scripts/check_gates.sh` exists as
a single command a human runs from a checkout. Of the repo's five pre-existing workflows, three run
tests — `python-test.yml` (`src/test/term_info_queries_test.py`), `performance-test.yml`
(`src/test/test_query_performance.py`) and `examples.yml` (`src.test.readme_parser` and
`src.test.test_examples_diff`) — and every one of them points at `src/test/`. Nothing ran `tests/` or
the client's suite, so before this workflow none of the new tests ran anywhere.

The offline half is two jobs rather than two steps, because the halves need genuinely different
environments. The client package depends on nothing but `requests` and `pandas` and declares support
back to 3.8, so it is installed from its own `pyproject` on 3.8 and 3.11 — installing it that way is
what keeps "pure requests + pandas, installs in seconds" an assertion rather than a claim. The server
tests import `vfbquery.ha_api`, which goes through the package `__init__` and therefore needs the
whole runtime set (`pysolr`, `marshmallow`, `vfb_connect` and so navis), so they get a full
`pip install -e .` on the deploy's 3.11 only. An earlier version of this workflow used
`--no-deps` to skip navis and instead suppressed exactly the imports collection dies on: both matrix
legs were red by construction, which is a thing worth stating because it looked like a thrifty
install and was actually a gate that could never pass.

**One manual step before this CI is live.** The file is committed at `docs/ci/search-gates.yml`, not
`.github/workflows/search-gates.yml`, and GitHub only reads workflows from the latter. The token this
branch was pushed with has no `workflow` scope, and GitHub rejects the *whole push* — not just that
file — when the diff touches `.github/workflows/`. Parking the definition one directory over keeps it
in the diff to review; `git mv docs/ci/search-gates.yml .github/workflows/` from a checkout with a
workflow-scoped credential is all that is left. Until that happens, `scripts/check_gates.sh` is the
only thing running these gates.

### Done for `/search`

**Ranking parity with the real website JS.** `docs/search-parity/` runs the website's
`refineResults` + `sorter` under Node against the Python port on the same Solr response:
`python3 docs/search-parity/check_parity.py`. The `sorter` is loaded **live** from the geppetto-vfb
checkout `GEPPETTO_VFB` points at, so it is whatever that checkout holds; `refine.js` is a **vendored
verbatim copy** of `refineResults` from `SOLRclient.tsx` at `openworm/geppetto-client@VFBv2.3.8.1`,
because it lives in the client package rather than in the config file. So the sorter half tracks
upstream automatically and the refine half is pinned — if `refineResults` changes upstream, that copy
has to be refreshed by hand or the gate will keep passing against a stale definition. A query whose
Solr response is empty now **fails** rather than comparing `[] == []`. All **78** queries identical — the 22 hand-picked
discriminating cases plus a 56-query fuzz sample drawn from real labels, synonyms and short_forms
(`--fuzz 56`, seed `20260722`, `--seed N` for a different draw). Re-run it after touching
`search_config.py` §3 (refine) or §4 (sort) — the comparator is non-transitive, so both TimSorts
*tend* to agree but are not guaranteed to, which makes this a measurement and not a proof.

Both halves of that "78" were worth less than the number suggested until recently, and the fix is
part of this branch. The fuzz pool used to be drawn with no `fq` and `sort=short_form asc`, i.e. the
alphabetical head of the *unfiltered* index — which is the imported `BFO_`/`CHEBI_`/`CL_`/`ENVO_`
terms that `FQ_BASE` excludes from `/search` by design. **15 of the 56 fuzz queries returned zero
docs**, so both sides produced `[]`, and `[] == []` was scored as a pass. The pool query now carries
`FQ_BASE` + `FQ_NOT_DEPRECATED`, and it is drawn from six windows at seed-determined random offsets
rather than one head, because a single head under `short_form asc` is all FlyBase alleles and would
never fuzz an anatomy class, an individual, a dataset or a publication. The sample now spans all of
those, and 78/78 compare non-vacuously. Re-run it after touching
`search_config.py` §3 (refine) or §4 (sort) — the comparator is non-transitive, so both TimSorts
*tend* to agree but are not guaranteed to, which makes this a measurement and not a proof.

**No drift from the HTTP layer.** 15 cases through `/search` matched module-level `search()`
byte-for-byte on rows and counts. Measured once, by hand, against a locally started server; there is
**no committed harness for it**, so it is a result from a point in time and not a gate — unlike the two
claims above and below it, nothing re-checks this on demand. Worth building if the HTTP layer grows any
shaping of its own; today it has none, which is why it was left.

**Load, measured against the 80-at-peak target.** Same caveat, more strongly: these numbers came from
ad-hoc runs against a locally started server on one machine, and no harness for them is committed
either. Treat them as evidence that the design behaves, not as figures reproducible from this branch.
Two things the reading did not tell me:

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

### Done for `/xref`

**Offline**, `tests/test_xref.py` — 11 tests over a trimmed real `term_info` fixture: row shaping and
assembled links (including `link_postfix`), `db` matching case-insensitively on symbol / short_form /
label, `db` falling back to short_form when `symbol` is blank, whole-string-not-substring matching
(`neuprint` must **not** match `neuprint_JRC_Hemibrain_1point2point1`), no-`db` returning everything,
malformed or missing pieces returning nothing rather than raising, and the label → symbol fallback.

**Offline**, `tests/test_search_xref_endpoints.py` — the handlers themselves, which the helper tests
cannot reach: the reverse direction's exact-accession confirmation (asserted with the near-miss ranked
*first*, so dropping the confirmation returns a confident wrong answer and the test fails), candidate
de-duplication and the `XREF_MAX_CANDIDATES` cap, the exactly-one-direction and `MAX_ID_LEN` rejections,
and that `db` and the four facet parameters are part of the two cache keys. Solr is replaced at its two
seams (`_solr_search_ranked`, `_fetch_term_info_docs`); everything between them is the real handler,
coalescer, cache and response envelope. Written against mutations rather than for coverage — each test
was confirmed to fail when the line it guards is deleted.

**Round trip, live** — `VFB_jrchjtdb → 1734350908 → VFB_jrchjtdb`, asserted both through raw HTTP and
through `VfbClient` (`test_live_xref_round_trips_a_hemibrain_bodyid`). The same test asserts that an
accession VFB does not hold returns **empty**, not the best-ranked near miss — that is the property
the whole confirm-don't-guess design exists for.

**Two bugs the matrix caught, both in the reverse direction.** `refine_results` emits one ranked row
per matching synonym, so the candidate list held the same `short_form` several times and the answer
came back duplicated; de-duplicated order-preservingly. And `XREF_MAX_CANDIDATES` passed as `limit`
truncated ranked *rows* before de-duplication, making the constant cap an unpredictable number of
distinct *terms*; it now slices the de-duplicated list instead, which costs nothing because the
sorter ranks the full set either way.

**No drift between the two endpoints.** `/xref`'s reverse lookup and `/search` share one
`_solr_search_ranked` helper rather than two copies of the query-and-rank block, so the reverse
lookup uses the canonical construction by construction. Parity re-ran identical on all 22 cases after
that extraction, confirming it was behaviour-neutral.

### Done for degraded answers

The failure mode this branch keeps meeting is not an error but a **plausible incomplete 200**: an
unresolved connectivity type returning zero rows like a genuinely unconnected pair, `/xref`'s
best-ranked near miss standing in for an accession VFB does not hold, and — found by gate 5 on its
first run — `get_instances` serving 10 of 68 rows from the SOLR fallback while Neo4j was down. The
convention for all of them is a top-level `warnings` list, already used by
`vfb_connectivity.get_connected_neurons_by_type` and documented on `ResultCache._weight`.

Two changes finish it. Server side, the `get_instances` Neo4j→SOLR fallback attaches a `warnings`
entry naming the outage and what the fallback cannot see (only instances with an aligned image;
`source`/`dataset` blank), and also raises a Python warning so in-process library callers on the
DataFrame path — which has nowhere to put a key — are told too. Client side, re-raising moved out of
`get_connected_neurons_by_type` into `_get`, so it covers every endpoint: any handler that starts
reporting a partial answer is surfaced by having said so, not by a method remembering to look.
`_cap_result_rows`, `_prepare_full_for_cache` and `_slice_page` all copy the payload dict, so the key
survives capping, caching and paging untouched.

Covered by `test_server_warnings_reach_the_caller_from_any_endpoint` (two endpoints, asserted through
a stubbed *transport* rather than a stubbed `_get`, so the surfacing code is inside the test rather
than replaced by it) and `test_a_clean_result_stays_quiet` (without which "warn always" would pass).
Both were confirmed to fail with the `_raise_server_warnings` call deleted.
`test_live_get_instances_da1lpn` now asserts the absence of a degradation warning **before** the
row-count floor, so a repeat of that outage fails saying it was an outage instead of leaving
`assert 10 > 50` to be diagnosed.

### Done for `/combine`

The set algebra is split across two modules on purpose, and the split is the design decision worth
recording. Everything decidable **without the network** — tokenising, parsing, precedence and
brackets, plain-English rendering, identity-column selection, namespace diagnosis, the universe and
its degeneracies, and the lossless row/header merge — lives in `src/vfbquery/combine.py`, which
imports nothing outside the stdlib. `ha_api.py` holds only the part that needs a server: turning
operand specs into `/run_query` and `/search` calls on the existing pool. That is why 65 of the 95
tests run in well under a second, why the client can reuse the same parser to validate an expression
before spending a request, and why a bracketing bug can be reproduced without a Neo4j.

**Tested in two layers, because they fail differently.** `test_combine_endpoint.py` patches the
payload seams for the handler's own logic — the reserved-vs-operand parameter split, all eight refusal
messages, the warnings, `explain_only` running nothing — and then patches `_run_query` underneath a
real `ThreadPoolExecutor` for the four behaviours only the true dispatch path exercises: that an
operand lands on the **same cache key** a direct `/run_query?id=…&query_type=…` would (the one test
that would catch a key drift — answers stay correct either way, only the cost changes), that a paged
query asks `offset=0, limit=0`, that `a AND [b OR a]` runs two queries and not three, and that a full
queue sheds the whole combination as a single 503 with `Retry-After` having run nothing.

**Every hazard the design guards against was measured first, not imagined.** Silent truncation
(`DatasetImages`/`Nern2024` reports `count: 60002` and returns 25,000 rows), duplicate ids (8,935 rows
over 894 terms), namespace mismatch (`FBbt_` / `VFB_` / `FBlc_` / `FBgn_` sets that can never
intersect), cross-dataset divergence (`T4c_R` spans 1,766 distinct VFB ids across five datasets, so an
*individual*-level intersection across datasets is always ≈0 and the useful question is a class-level
one), and the implicit-universe algebra. Each of those is a way to get a confidently wrong empty set,
which is the same failure this branch has been removing everywhere else: a partial or meaningless
answer that is shaped exactly like a complete one. `why_empty` on the step record, the truncation
warning, and `require_complete`'s 409 are the three places that failure is made to announce itself.

One test is worth naming because it encodes a decision rather than a behaviour:
`test_and_not_is_two_operators_rather_than_one`. `a AND NOT b` is parsed as two operators, not as an
alias for `a NOT b`, because the two readings **diverge** the moment an explicit `universe=` is
narrower than `a` — and a phrase alias that silently agrees in the common case and disagrees in the
rare one is worse than no alias.
