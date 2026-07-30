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
(commit "Repoint vfbquery-client search at /search").

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
MCP only *tries* to demote them (`facets_annotation:Deprecated^0.001` in `bq`), so deprecated terms
can still surface — and in fact that clause demotes nothing at all: `^0.001` is a small *positive*
boost, so it nudges deprecated terms very slightly **up**. In the website's config it is harmless
because the hard `fq` has already removed those documents; in the MCP's, where there is no such `fq`,
it is a demote that does not demote. See §5b for what a demote has to look like to work.

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
front of Solr.

Until they do, the arithmetic is worth stating plainly rather than flatteringly. All six copies above
still exist, so `/search` is a **seventh** implementation of VFB search — a faithful one, and the only
one anything can be repointed *at*, but for now an addition to the count and not a subtraction from
it. It has **one** consumer (`clients/vfbquery-client`, which is why the count did not go to eight:
that client used to be a copy of #5). Three is the target — website, MCP, client — and only at three
is "single source of truth" a description rather than an intention.

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

**Shipped**, after sign-off, as `build_exact_label_boost` in `search_config.py` (`EXACT_LABEL_BOOST =
6000`), on by default and disableable per call with `build_params(..., exact_label_boost=False)`. That
switch is not decoration: `check_recall.py`'s `baseline` variant *uses* it to reconstruct the website's
unpatched retrieval, so the harness keeps measuring a real before/after instead of quietly comparing
the fix to itself once the fix is the default. `shipped` calls the same builder production does — a
disagreement between harness and server is therefore a test failure, not a silent divergence.

Because retrieval changes are invisible to the parity gate, the guard is `check_recall.py --gate`
(wired into `scripts/check_gates.sh`), which fails unless the shipped config still recalls strictly
more than the baseline and still moves nothing else. Its thresholds are relative — "no worse than
measured" — because it hits the live index and absolute ranks drift as the ontology does.

**`MBON-a2`'s top hit is an individual, and that is correct.** Earlier revisions of this document
claimed the website leads with the class `larval mushroom body output neuron a2`. It does not, and
the `Class^200` boost is not being overridden: `FBbt_00047966`'s synonyms are
`["larval MBON-a2", "odd", "MBE7b"]` — **not** `MBON-a2` — so the L1EM individuals are the only exact
label matches, and no amount of class boosting invents a match that is not there. If the class should
be findable as `MBON-a2`, the fix is a synonym in the ontology, not a search change.

## 5b. Where `/search` now deliberately diverges from the website

Everything above this section is a faithful port: same `fq`, same boosts, same comparator, byte-identical
ordering on 78 queries. Three things in that inheritance were not worth being faithful to, and this
section is the record of choosing not to be. All three were reported as "faithful to the website rather
than broken" in an earlier live-test writeup, on the reasoning that changing them changes what the
website returns. That reasoning was wrong in one respect: none of the three changes the *ordering* the
parity gate protects, and each of them silently mislead a caller.

**A misspelled type name was a 200 with zero rows.** `filter_types=NotAType` produced
`fq=facets_annotation:NotAType`, which matches nothing, so the response was a well-formed empty result
— indistinguishable from "that type exists and nothing in it matched your query". A caller filtering by
`Neurone` got a biological-looking answer of zero. Type names are now resolved against the live facet
vocabulary first (233 names, all lowercase in the index although stored *row* values are capitalised —
`Nervous_system`, `has_subClass` — so resolution folds case and separators), and an unknown one is a
**400** naming the parameter, the value, and the nearest real names. Prefixes deliberately do not
resolve: `neuro` is not `neuron`. Contrast `/xref`'s `db` matcher, where prefix widening *is* right
because the user is naming a data source they know by an abbreviation; here widening a filter changes
which biology comes back. If the vocabulary cannot be fetched, validation **fails open** — an outage in
a convenience feature must not take search down with it. The vocabulary is also exposed directly, as
`GET /facets`.

**`boost_types` / `demote_types` were accepted and had no visible effect.** They alter the Solr score,
and the comparator that decides the order a person actually sees ranks on label text and never consults
that score (§2, §4) — so the two parameters were documented, accepted, and inert. Fixing it needed both
halves. In `bq`, a demote is now `(*:* -facets_annotation:X)^100`, a positive boost on everything that
is *not* X: `^-100` is not a Solr syntax error but an HTTP 500, and `^0.001` is a boost so small it
demotes nothing (§2b). And after the comparator runs, the ranked rows are partitioned into
boosted / neither / demoted, stably — the comparator's order survives *within* each group, so this is a
three-way stable partition and not a re-sort. A type named in both parameters takes the boost. Nothing
is added or removed by either parameter; `exclude_types` remains the way to actually drop rows.

**One term could occupy several rows.** `refineResults` emits one row per matching label *or* synonym,
which is what the website's dropdown wants — it is showing you *why* each row matched — and it is why
`count` is legitimately larger than Solr's `numFound`. For a programmatic caller asking for 25 results
it means an unknown number of distinct terms, and no way to tell without inspecting. The rows are
unchanged by default; every response now also reports `distinct_terms`, and `unique=true` collapses to
one row per term (highest-ranked occurrence kept) *before* `limit`, so a page of 25 is 25 terms.

## 6. Reproducing the measurements

Everything this branch has to keep true, in one command:

```bash
git clone --depth 1 https://github.com/VirtualFlyBrain/geppetto-vfb /tmp/gvfb
scripts/check_gates.sh          # unit + client + parity + recall; non-zero on any failure
```

The individual harnesses, for when one of them fails and you want the detail:

```bash
python3 docs/compare_search_configs.py             # config-vs-config comparison, read-only GETs
python3 docs/compare_search_configs.py --check-pf  # the two pf measurements from §2e

GEPPETTO_VFB=/tmp/gvfb python3 docs/search-parity/check_parity.py --fuzz 56

python3 docs/search-parity/check_recall.py                     # baseline vs shipped, the §5 table
python3 docs/search-parity/check_recall.py --gate              # same, but exits non-zero on regression
python3 docs/search-parity/check_recall.py --variant rows1000 --variant augment   # rejected alternatives
```

`check_recall.py` is deliberately *not* part of the parity gate, and the two measure opposite things.
The parity harness feeds the **same** Solr response to the JS sorter and the Python port — which is
what makes it a clean ranking test, and exactly why it cannot see the §5 bug: a term that scores below
`rows` never reaches either sorter, so both agree perfectly on a candidate set that is already missing
the right answer. Any change to retrieval is invisible to the parity gate and needs this harness
instead. It reports recall, rank 0, and top-10 churn on queries with no exact-label intent, and it hits
live Solr (read-only), so absolute numbers move as the index does.

`docs/search-parity/` is the parity gate: it runs the website's `sorter` and `refineResults` under
Node against the **same** Solr docs the Python port is given, and diffs the ordering row by row. It
isolates ranking from query construction, and exits non-zero on any mismatch — including on a query
that returns no docs at all, where `[] == []` would otherwise read as a pass.

The two JS halves come from different places, which is worth knowing before trusting a green run.
`sort_under_node.js` `require`s `searchConfiguration.js` **live** out of the geppetto-vfb checkout, so
the sorter is always whatever that checkout holds. `refineResults` is not in the config file — it
lives in `SOLRclient.tsx` in the client package — so `refine.js` is a **vendored verbatim copy**
pinned at `openworm/geppetto-client@VFBv2.3.8.1`. The sorter half therefore tracks upstream by
itself; the refine half does not, and must be refreshed by hand if `refineResults` changes, or the
gate will keep passing against a definition the website has stopped using.

The fuzz sample is drawn with `/search`'s own filters (`FQ_BASE` + `FQ_NOT_DEPRECATED`) and from six
windows at seed-determined random offsets. Both of those are corrections, not decoration. Drawing
without the `fq` sampled the whole index rather than the 741,035 docs `/search` can return, and under
`short_form asc` the head of the difference is entirely imported `BFO_`/`CHEBI_`/`CL_`/`ENVO_` terms
— so 15 of 56 fuzz queries returned zero docs and were scored as passes on `[] == []`. Drawing from
one window instead of six makes the sample an alphabetical prefix: all FlyBase alleles, never an
anatomy class, individual, dataset or publication.

Current state: **byte-identical ordering on 78 queries**, none of them vacuous — 22 hand-picked
discriminating cases plus a 56-query fuzz sample drawn from real labels, synonyms and short_forms —
including 2432-row result sets, empty input, double spaces, braces, quotes and apostrophes. Re-run it
after touching anything in `search_config.py` sections 3 or 4, or after pulling geppetto-vfb.
