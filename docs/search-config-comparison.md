# Free-text search: where the existing configs diverge

Context for plan item **C1** (`/search`). Before wiring a `/search` route we needed to know *which*
query config it should serve, because there was not one VFB search config — there were six, and they
did not agree.

**This question is now settled** — see [§4](#4-decision) — and `/search` ships in
`src/vfbquery/ha_api.py`, serving the config in `src/vfbquery/search_config.py`. The comparison below
is kept because it is the evidence for that decision, and because §5 records live behaviour that is
still worth fixing.

All six hit the **same Solr core** (`https://solr.virtualflybrain.org/solr/ontology/select`, except
where noted) with `defType=edismax`, so the disagreement is entirely in query construction, filters,
boosts and post-processing.

## 1. The copies

| # | Copy | Where | Notes |
|---|---|---|---|
| 1 | Website main search overlay | `geppetto-vfb/components/configuration/VFBMain/searchConfiguration.js` (`datasourceConfiguration`) | The one users actually type into. `rows=500`, `pf=label^250 synonym^120`, `ps=0`. **Canonical** — this is what `/search` reproduces. |
| 2 | Website query builder | `geppetto-vfb/.../VFBMain/queryBuilderConfiguration.js` (URL string, `rows=100`) | Same params as #1 inline in a URL, but `pf=true` (see §2e) and `fl` carries a `type:"class"` pseudo-field constant. |
| 3 | Website spotlight | `geppetto-vfb/.../VFBMain/spotlightConfiguration.js` | **Pre-migration schema** — `type:class`, `ontology_name:(vfb)`, `is_defining_ontology`, `label_autosuggest_ws/_e`, `is_obsolete`. Different field set entirely. |
| 4 | geppetto-client default | `@geppettoengine/geppetto-client` (pinned to `openworm/geppetto-client#VFBv2.3.8.1`), `geppetto-ui/src/search/datasources/SOLRclient.tsx` | Library fallback; points at **solr-dev** and the same pre-migration schema as #3. Overridden by #1 at runtime, so it only matters if a config is ever omitted. |
| 5 | MCP `search_terms` | `VFB3-MCP/dist/index.js` (~L468–500) | What the MCP tool sends. |
| 6 | Website circuit browser | `geppetto-vfb/components/configuration/VFBCircuitBrowser/datasources/SOLRclient.tsx` (`datasourceConfiguration`, ~L461) | Live, current schema, prod Solr, but its own everything: `rows=100`, `pf=true`, `fq` is `has_neuron_connectivity` + `shortform_autosuggest:VFB*|FB*` + hard `NOT Deprecated` (no `VFBc_*` exclusion), `bq` is `VFB*^110 FBbt*^100` with **no Class boost** — so it leads with individuals by design, which for a connectivity picker is arguably right. Has its own sorter, run in a web worker. The `globalConfiguration` at the top of the same file is a dead pre-migration fallback. |

`clients/vfbquery-client` was a seventh copy replicating #5; it now calls `/search`
(commit "Repoint vfbquery-client search at /search"). `docs/draft_search_xref_endpoints.py` is an
early sketch, superseded by `search_config.py`.

## 2. Website main search (#1) vs MCP `search_terms` (#5)

Identical: core URL, `defType=edismax`, `mm=45%`,
`qf=label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest`, `fl`, and the
base `fq`
(`(short_form:VFB* OR short_form:FB* OR facets_annotation:DataSet OR facets_annotation:pub) AND NOT short_form:VFBc_*`).

Different in five ways:

**a. `q` construction — the big one.** MCP treats the whole input as one string:

```
q = "<query> OR <query>* OR *<query>*"
```

The website does **not**. `getResultsSOLR` in the geppetto-client SOLR datasource normalises
`- + _` to spaces, splits on whitespace, and ANDs a wildcard OR-group per token:

```
q = "(tok1 OR tok1* OR *tok1 OR *tok1*) AND (tok2 OR tok2* OR *tok2 OR *tok2*) AND …"
```

So every token must match (as prefix, suffix or infix) rather than `mm=45%` deciding how many of the
words need to hit. Measured live (same `fl`, `rows=10`):

| Query | MCP `numFound` | Website `numFound` |
|---|---|---|
| `DA1 lPN` | 718 | 51 |
| `kenyon cell` | 4749 | 117 |
| `MBON-a2` | 1585 | 39 |
| `antennal lobe DA1 projection` | 688 | 6 |
| `fan-shaped body` | 1520 | 230 |

Two quirks of that normalisation are worth knowing, because `search_config.py` reproduces both
deliberately:

- It is `searchString.replace("-", " ")`, and **JS `String.replace(str, str)` replaces only the first
  occurrence.** So `MBON-a2-b` becomes `MBON a2-b`, not `MBON a2 b`, and the surviving hyphens go to
  Solr inside a wildcard group. (Python's `str.replace` replaces all, hence the `count=1` calls in the
  port.)
- Splitting is on `" "` without dropping empties, so a double space yields an empty OR-group
  `( OR * OR * OR **)`. This is **not** inert and does **not** error: `"  double  space "` returns
  HTTP 200 with `numFound=3`, where dropping the empty token returns `numFound=0`. Being
  "helpfully" tidier here changes results, so the port keeps the empty group.

**b. Deprecated terms.** Website adds a second hard filter `fq=NOT facets_annotation:Deprecated`.
MCP only *demotes* them (`facets_annotation:Deprecated^0.001` in `bq`), so deprecated terms can still
surface.

**c. `bq` boosts.**

```
website: short_form:VFBexp*^10.0  short_form:VFB*^50.0   facets_annotation:Class^200.0
         short_form:FBbt*^150.0   short_form:FBbt_00003982^2
         facets_annotation:Deprecated^0.001
         facets_annotation:DataSet^500.0  facets_annotation:pub^100.0
MCP:     short_form:VFBexp*^10.0  short_form:VFB*^100.0
         short_form:FBbt*^100.0   short_form:FBbt_00003982^2
         facets_annotation:Deprecated^0.001
```

The website deliberately floats **types over individuals** (`Class^200`, `FBbt*^150` vs `VFB*^50`)
and floats datasets/publications hard (`DataSet^500`, `pub^100`). MCP flattens all of that
(`VFB*^100` = `FBbt*^100`, no Class/DataSet/pub boost).

**d. A runtime phrase boost the config files do not show.** `getResultsSOLR` *appends* to whatever
`bq` the config supplies, on every non-empty search:

```
label:"<normalised input>"^3000  synonym:"<normalised input>"^1500
```

(with `\` and `"` escaped). Reading `searchConfiguration.js` alone therefore gives the wrong `bq`.
Its stated purpose — see the comment in `SOLRclient.tsx` — is to rescue exact matches that the
wildcard `q` pushes past `rows`. It does not entirely work; see §5.

**e. `pf` is a red herring in every copy.** #1 sets `pf=label^250 synonym^120 ps=0`; #2, #6 and MCP
set `pf=true`. Both are moot:

- `pf=true` is a silent no-op. `pf` expects a field list, `true` is not a field, and Solr neither
  errors nor warns — measured on a plain (non-wildcard) `q`, `pf=true` scores identically to omitting
  `pf` (657.0), while a real field list scores 1429.4.
- For the website's actual `q`, even the real `pf` never fires: every token is wrapped in a wildcard
  OR-group, so there is no contiguous phrase left to boost. Measured, `kenyon cell` in website `q`
  form scores 1287.0 with `pf=label^250 synonym^120`, with `pf=true`, and with no `pf` at all —
  three identical scores.

So `pf` differences between the copies explain nothing, and the phrase boost that *does* matter is
the runtime `bq` addition in (d). This is presumably why (d) exists.

**f. Post-processing (website only).** After Solr returns, the website does two things the MCP does
not:

1. `refineResults` **explodes synonyms into separate result rows** — one row per synonym, relabelled
   `"synonym (canonical label)"`, plus the canonical row relabelled `"label (short_form)"`. This
   multiplies row counts substantially: 500 docs become 1370 rows for `neuron`, 1903 for
   `adult neuron`.
2. It then applies the ~370-line custom `sorter` in `searchConfiguration.js` (official-symbol vs
   synonym detection, synonym position in the list, exact/case-insensitive short-form match,
   token-overlap scoring, class-over-individual, `VFBexp` promotion, match-position, length).

**So the ordering a website user sees is not Solr's ordering** — which means any comparison of "top
hit" between configs at the Solr level, including the tables in earlier revisions of this document,
describes something no user experiences. `/search` reproduces this stage too.

## 3. What the sorter actually contains

Read line-by-line while porting. Four blocks are dead, and are noted as such in `search_config.py`
so nobody "fixes" the port into disagreeing with the website:

| Lines | Block | Why it never fires |
|---|---|---|
| 400–407 | "Case-insensitive official symbol match" | `aIsSymbolCaseInsensitive` is `aTermCount >= 2`, the *same predicate* as `aIsOfficialSymbol` two blocks up, and the asymmetric cases already returned. |
| 340–341 | `aIsSynonymMatch` / `bIsSynonymMatch` | Assigned, never read. |
| 237–238 | `aIsIndividual` / `bIsIndividual` | Assigned, never read. |
| 570–571 | `aIsClass` redeclared | Shadows the earlier `aIsClass` with an FBbt-only test (no FBgn). |

Two more quirks are load-bearing and reproduced exactly:

- **Lines 491–496**: the second guard tests **`a`**'s `indexOf`, not `b`'s. Almost certainly a typo,
  but it is live behaviour.
- **Lines 535–554**: `aLabel.pop()` then `aLabel.join(' (')`, so a label with no `" ("` yields the
  **empty string**, not the whole label. The port originally fell back to the whole label, which is
  the "helpful" reading and gives a different order.

The comparator is **not a consistent total order** — several rules mix label length with substring
position, so `a<b<c<a` is reachable. Both V8's `Array#sort` and CPython's `list.sort` are TimSort, so
they *tend* to agree on an inconsistent comparator, but that is not a guarantee. Parity therefore has
to be **measured**, not reasoned about; see §6.

## 4. Decision

**Adopt #1 — the website's construction, `fq` and boosts, plus its `refineResults` and sorter — as
canonical, serve it from `/search`, and have every consumer call `/search`.** Shipped:

- `src/vfbquery/search_config.py` — the params, `refine_results`, the comparator, and `search()`.
- `GET /search` in `src/vfbquery/ha_api.py` — cached, coalesced, off the Neo4j process pool.
- `clients/vfbquery-client` — calls `/search`; no Solr config left in it.

Still to do, outside this repo: repoint the website's `datasourceConfiguration` and the MCP's
`search_terms` at `/search`. That is what actually collapses copies 1, 2 and 5 and puts the cache in
front of Solr; until then `/search` is a faithful third implementation rather than a replacement.

Open, and worth a decision from someone who knows the intent:

- **#3 and #4** still use the pre-migration schema and #4 points at **solr-dev**. Dead code, or
  quietly behaving differently from everything else?
- **#6** (circuit browser) is live and deliberately different — no Class boost, so individuals lead.
  Probably correct for its purpose. If it should share `/search`, it needs `filter_types` /
  `boost_types` rather than a config of its own.

## 5. Live behaviour that looks wrong

Found while validating the port. **These are faithful reproductions of what the website does today**,
not port bugs — the parity harness confirms the ordering matches. They are recorded here because they
are worth fixing at the source.

**Exact single-token terms can be unreachable.** Searching `neuron` never surfaces the term *neuron*
(`FBbt_00005106`). It passes the `fq` (`numFound=1` when queried alone) but ranks **705th** by Solr
score — outside `rows=500`, so the sorter never sees it and cannot promote it. This is a *retrieval*
failure, not a ranking one: the sorter promotes exact matches correctly whenever it is handed them,
which is also why the parity gate is blind to it (§6).

The cause is the runtime phrase boost from §2d — but not in the way an earlier revision of this
document guessed. Isolating its two halves for `neuron` / `FBbt_00005106` at `rows=1000`:

| `bq` | score-rank of the exact term |
|---|---|
| `label:"neuron"^3000 synonym:"neuron"^1500` (shipped) | 705 |
| `label:"neuron"^3000` alone | **0** |
| `synonym:"neuron"^1500` alone | not in top 1000 |
| `BQ_BASE` only, no phrase boost | 106 |
| no `bq` at all | 99 |

The label half alone gets it exactly right. It is the *sum* that breaks it, because the two halves are
additive and competitors collect both: `dopaminergic neuron` has synonyms `dopamine neuron` /
`DA neuron`, `developing neuron` has `immature neuron` / `differentiating neuron`, so each earns
3000 + 1500 = 4500. `FBbt_00005106`'s only synonym is `nerve cell`, which does not contain the token,
so the term whose label *is* the query earns 3000 alone. **The exact match is penalised for lacking a
redundant synonym.** The boost is not unselective; it is selective on the wrong thing.

Two claims in the earlier revision of this section were wrong, and measurement killed both:

* *"The schema has no `label_s` string field."* It has `label_str` — `copyField label -> label_str`,
  with `dynamicField *_str` as `type=strings, docValues=true, indexed=false, stored=false`. Genuinely
  whole-field exact, though case-sensitive, and queryable via docValues rather than the inverted index.
* *"`label_autosuggest_e` looks like the intended exact-label field."* It is not. It is
  `text_general`, tokenized identically to `label`, and unpopulated for `FBbt_00005106` — so it can
  neither express an exact match nor match this document at all.

**Scope, measured rather than assumed.** `docs/search-parity/check_recall.py` samples real labels from
the live index, bucketed by token count, with deprecated terms excluded (the `fq` hides them on
purpose, so counting them as misses would invent a bug and then flatter any variant that appeared to
fix it). Baseline over a 43-label corpus (14 of them single-token): **42/43** retrieve their own term
at all, **41/43** at rank 0, worst rank when found 5. The single miss is `neuron`. A separate 70-label
single-token sweep found **zero** further failures.

So `neuron` is the only term a user can reach for and miss — one bug, not a systemic one. But two
latent near-misses sit just inside the window: `adult` at score-rank 424 of 500, `cell` at 137. The
same defect is one indexing change away from breaking terms that work today.

**Candidate fixes, measured against that corpus.** Churn is positions moved in the top 10 of ten
ordinary queries with no exact-label intent — i.e. collateral damage:

| variant | recall | rank 0 | churn | cost |
|---|---|---|---|---|
| `rows=1000` (more candidate depth) | +1 | +1 | 2 positions (on `PN`) | 1.0× requests |
| second exact lookup merged into the candidate set | +1 | +1 | 0 | 2.0× requests |
| …same, gated to ≤2-token queries | +1 | +1 | 0 | 1.8× requests |
| **`label_str:"<term>"^6000` appended to `bq`** | **+1** | **+1** | **0** | **1.0× requests** |

The last is the recommendation. `^6000` has to beat the *combined* 3000 + 1500, because that
combination is precisely what the exact term loses to. Unlike the label and synonym halves, this
clause cannot be earned by a longer label that merely *contains* the query, so it lifts the exact term
and nothing else — which is why the churn is zero rather than merely small.

Verified before recommending it: `adult` 424 → 0, `cell` 137 → 0, `neuron` miss → 0, `brain`
unchanged; synonym search unaffected (`nerve cell`, `DA neuron`, `KC`, `MB neuron` rank 0 both before
and after); latency differences within run-to-run noise. `kenyon cell` stays at rank 5 either way —
that one is the comparator faithfully preferring the `alpha/beta …` variants, not retrieval.

Known limitation: `label_str` is case-sensitive, so the clause enumerates four capitalisations
(as-typed, lower, capitalised, title-case) and unusual casing will still miss. Because the clause is
purely additive, a miss means no improvement — never a regression.

**Not shipped.** `search_config.py` is unchanged; the candidate exists only in the harness, as
`variant_exact_boost`. Changing retrieval changes what every consumer of `/search` sees, and the
parity gate cannot catch a regression in it, so this wants a decision rather than a commit.

**`MBON-a2`'s top hit is an individual, and that is correct.** Earlier revisions of this document
claimed the website leads with the class `larval mushroom body output neuron a2`. It does not, and
the `Class^200` boost is not being overridden: `FBbt_00047966`'s synonyms are
`["larval MBON-a2", "odd", "MBE7b"]` — **not** `MBON-a2` — so the L1EM individuals are the only exact
label matches, and no amount of class boosting invents a match that is not there. If the class should
be findable as `MBON-a2`, the fix is a synonym in the ontology, not a search change.

## 6. Reproducing the measurements

```bash
python3 docs/compare_search_configs.py             # config-vs-config comparison, read-only GETs
python3 docs/compare_search_configs.py --check-pf  # the two pf measurements from §2e

git clone https://github.com/VirtualFlyBrain/geppetto-vfb /tmp/gvfb
GEPPETTO_VFB=/tmp/gvfb python3 docs/search-parity/check_parity.py --fuzz 60

python3 docs/search-parity/check_recall.py                        # the §5 recall table, all variants
python3 docs/search-parity/check_recall.py --variant exact_boost  # just the recommended one
```

`check_recall.py` is deliberately *not* part of the parity gate, and the two measure opposite things.
The parity harness feeds the **same** Solr response to the JS sorter and the Python port — which is
what makes it a clean ranking test, and exactly why it cannot see the §5 bug: a term that scores below
`rows` never reaches either sorter, so both agree perfectly on a candidate set that is already missing
the right answer. Any change to retrieval is invisible to the parity gate and needs this harness
instead. It reports recall, rank 0, and top-10 churn on queries with no exact-label intent, and it hits
live Solr (read-only), so absolute numbers move as the index does.

`docs/search-parity/` is the parity gate: it runs the **real** `sorter` and `refineResults` under Node
(`sort_under_node.js` requires `searchConfiguration.js` straight out of a geppetto-vfb checkout;
`refine.js` is `refineResults` verbatim from `SOLRclient.tsx`) against the **same** Solr docs the
Python port is given, and diffs the ordering row by row. It isolates ranking from query construction,
and exits non-zero on any mismatch.

Current state: **byte-identical ordering on 78 queries** — 22 hand-picked discriminating cases plus a
56-query fuzz sample drawn from real labels, synonyms and short_forms — including 2432-row result
sets, empty input, double spaces, braces, quotes and apostrophes. Re-run it after touching anything in
`search_config.py` sections 3 or 4, or after pulling geppetto-vfb.
