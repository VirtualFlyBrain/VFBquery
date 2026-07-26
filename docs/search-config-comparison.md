# Free-text search: where the existing configs diverge

Context for plan item **C1** (`/search`) and its "single source of truth" TODO. Before wiring a
`/search` route we need to know *which* query config it should serve, because there is not one VFB
search config — there are five, and they do not agree.

All of them hit the **same Solr core** (`https://solr.virtualflybrain.org/solr/ontology/select`) with
`defType=edismax`, so the disagreement is entirely in query construction, filters, boosts and
post-processing.

## 1. The copies

| # | Copy | Where | Notes |
|---|---|---|---|
| 1 | Website main search overlay | `geppetto-vfb/components/configuration/VFBMain/searchConfiguration.js` (`datasourceConfiguration`) | The one users actually type into. `rows=500`. |
| 2 | Website query builder | `geppetto-vfb/.../VFBMain/queryBuilderConfiguration.js` (URL string, `rows=100`) | Same params as #1 inline in a URL; `fl` carries a `type:"class"` pseudo-field constant. |
| 3 | Website spotlight | `geppetto-vfb/.../VFBMain/spotlightConfiguration.js` | **Older schema** — `type:class`, `ontology_name:(vfb)`, `is_defining_ontology`, `label_autosuggest_ws/_e`, `is_obsolete`. Different field set entirely. |
| 4 | geppetto-client default | `node_modules/@geppettoengine/geppetto-client/geppetto-ui/src/search/datasources/SOLRclient.tsx` | Library fallback; points at **solr-dev** and the same older schema as #3. Overridden by #1 at runtime, so it only matters if a config is ever omitted. |
| 5 | MCP `search_terms` | `VFB3-MCP/dist/index.js` (~L468–500) | What the MCP tool, and currently `vfbquery-client.search()`, send. |

(#6 and #7 would be this repo's `docs/draft_search_xref_endpoints.py` and
`clients/vfbquery-client/.../client.py`, which replicate #5 — the drift the C1 TODO is about.)

## 2. Website main search (#1) vs MCP `search_terms` (#5)

Identical: core URL, `defType=edismax`, `mm=45%`,
`qf=label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest`, `pf=true`,
`fl`, and the base `fq`
(`(short_form:VFB* OR short_form:FB* OR facets_annotation:DataSet OR facets_annotation:pub) AND NOT short_form:VFBc_*`).

Different in four ways:

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

No recall loss was observed on real terms — the top hit is the same or better. Where the two configs
disagree on the *top hit*, the factors were isolated (each row = one parameter changed):

| Query | config | numFound | top hit |
|---|---|---|---|
| `1734350908` (hemibrain bodyId) | phrase `q` + MCP `bq` (**= MCP**) | 2 | `olfactory PN(DT3a)_R` ❌ |
| | tokens `q` + MCP `bq` | 2 | `olfactory PN(DT3a)_R` ❌ |
| | phrase `q` + website `bq`/`fq` | 1 | `DA1_lPN_R (FlyEM-HB:1734350908)` ✅ |
| | tokens `q` + website `bq`/`fq` (**= website**) | 1 | `DA1_lPN_R (FlyEM-HB:1734350908)` ✅ |
| `MBON-a2` | phrase `q` + MCP `bq` (**= MCP**) | 1585 | `MBON-a2 (L1EM:15617305)` (individual) |
| | phrase `q` + website `bq`/`fq` | 1581 | `larval mushroom body output neuron a2` (class) |
| | tokens `q` + MCP `bq` | 43 | `larval mushroom body output neuron a2` (class) |
| | tokens `q` + website `bq`/`fq` (**= website**) | 39 | `larval mushroom body output neuron a2` (class) |

So attributing precisely:

- The **bodyId fix is the `fq`, not the tokenisation** — the competing hit is a Deprecated term, which
  the website hard-excludes and the MCP merely demotes. Tokenisation alone does not fix it (confirmed
  against the client with `q_mode="tokens"`).
- On **`MBON-a2` either change alone** flips class-above-individual. That one is a preference, not a
  bug: MCP surfacing the L1EM individual is defensible; the website's `Class^200.0` is a deliberate
  choice to lead with types.
- Tokenisation's own contribution is **precision** (43 vs 1585 candidates here), which matters most
  for the long tail below the top hit — and for `rows`-limited consumers like the client's
  `_resolve_to_id`.

Case where the phrase form looks better: a single ambiguous token like `lPN`, where MCP's top hit is
the right projection neuron and the website's raw Solr top hit is `larval lateropharyngeal nerve
root` — but see (d): the website never shows raw Solr order, so this comparison is not what a user
experiences.

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
(`VFB*^100` = `FBbt*^100`, no Class/DataSet/pub boost), which is why it returns individuals first for
`MBON-a2`.

**d. Post-processing (website only).** After Solr returns, the website does two things the MCP and
the client do not:

1. `refineResults` **explodes synonyms into separate result rows** — one row per synonym, relabelled
   `"synonym (canonical label)"`, plus the canonical row relabelled `"label (short_form)"`.
2. It then applies the ~350-line custom `sorter` in `searchConfiguration.js` (official-symbol vs
   synonym detection, synonym position in the list, exact/case-insensitive short-form match,
   token-overlap scoring, class-over-individual, `VFBexp` promotion, match-position, length).

**So the ordering a website user sees is not Solr's ordering.** Any server-side `/search` that wants
to "match the website" has to reproduce this stage too, not just the Solr params.

## 3. Implication for C1

The stated aim of C1 was "expose the existing search, don't build new search logic". That still
holds, but "the existing search" is ambiguous: `search_terms` and the website are different searches.
Recommendation, in order:

1. **Pick the website's query construction** (tokenised AND + wildcards) and its `bq`/`fq` as the
   canonical config for `/search`. It is measurably more precise, fixes the bodyId case, and is what
   users' expectations are calibrated against.
2. **Move the sorter server-side** (or accept raw Solr order and document it). The synonym-explosion +
   sorter is where most of the website's perceived quality lives; without it, `/search` will feel
   different from the website even with identical Solr params. Port it once, in `/search`.
3. **One config, four consumers.** Ship the params from a single module in VFBquery, have `/search`
   serve them, and have the MCP `search_terms`, the website (`datasourceConfiguration`), and
   `vfbquery-client.search()` all call `/search` instead of Solr directly. That collapses copies
   1, 2, 5, 6, 7 to one, and makes the cache/coalescer front the Solr core.
4. **Retire or update the stale copies** — spotlight (#3) and the geppetto-client default (#4) still
   use the pre-migration schema (`type:class`, `ontology_name`, `is_defining_ontology`,
   `label_autosuggest_ws/_e`, `is_obsolete`) and #4 points at **solr-dev**. Either they are dead code
   or they are quietly behaving differently from everything else; worth confirming which.

Until (1) is agreed, `vfbquery-client.search()` keeps MCP `search_terms` parity — its `q` builder
takes a `q_mode` so the tokenised form can be switched on without touching anything else.

## 4. Reproducing the measurements

`python3 docs/compare_search_configs.py` (offline-safe: it only issues read-only Solr GETs).
