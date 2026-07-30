# The HTTP API

Everything VFBquery can answer is reachable over HTTP from the cached service, deployed as
`https://v3-cached.virtualflybrain.org`. The [client](getting-started.md) wraps it, but the endpoints
are plain `GET` requests returning JSON and there is nothing wrong with calling them directly — the
website and the MCP server do.

```{note}
`/search`, `/xref` and `/combine` are new in this branch and are **not yet on the public deploy**.
Until they are, run the service locally to use them:
`python -m vfbquery.ha_api --port 8080` and point at `http://localhost:8080`.
```

## Endpoints

| Path | What it answers |
|---|---|
| `/get_term_info` | Everything VFB holds about one term: name, synonyms, definition, relationships, images, xrefs, NT predictions, publications. |
| `/run_query` | Any of the ~40 named query types — instances, subclasses, parts, connectivity, NBLAST, expression, single-cell. The workhorse. |
| `/query_connectivity` | Connectivity between two *types*, aggregated, across connectome datasets. |
| `/search` | Free-text search over the ontology, ranked the way the website ranks it. |
| `/xref` | VFB id ↔ external accession, both directions. |
| `/facets` | Every type name `/search`'s type filters accept, with term counts. |
| `/combine` | Set algebra over the results of other queries. See [the reference](combine-endpoint.md). |
| `/resolve_entity`, `/resolve_combination` | FlyBase-Chado exact resolution (features, genotypes). Not a search — see the note below. |
| `/find_stocks`, `/find_combo_publications` | Stock and publication lookups for a resolved entity or combination. |
| `/list_connectome_datasets` | The connectome datasets currently loaded. |
| `/get_hierarchy` | The `part_of` or `subclass_of` tree around a term, up, down or both. |
| `/health`, `/status` | Liveness, version, pool and cache statistics. |

```{admonition} `/resolve_entity` is not the search endpoint
:class: warning

It is tiered exact→synonym→broad resolution against FlyBase-Chado, for FlyBase features. It returns
`NOT_FOUND` for a partial or fuzzy anatomy name, so it is the wrong tool for "what is this thing
called". Use `/search`.
```

There is a second hierarchy route, `/get_hierarchy_html`, which returns the same tree as a rendered
HTML page. It stays inside the cluster network (it is not in `ALLOWED_PATHS`, so it 404s from
outside) because it exists to serve one consumer — the ROI browser on the geppetto site — and its
markup is that consumer's presentation, not an API contract. The JSON carries the same tree.

## `/get_term_info`

```
GET /get_term_info?id=FBbt_00007401
```

| Parameter | |
|---|---|
| `id` | **Required.** A VFB short_form: `FBbt_…` (anatomy class), `VFB_…` (individual), `VFBexp_…`, `FBgn_…`, `FBlc_…`. |
| `force_refresh` | `true` bypasses the result cache for this call. |

## `/run_query`

```
GET /run_query?id=FBbt_00007401&query_type=NeuronsPartHere
```

| Parameter | |
|---|---|
| `id` | **Required.** The term the query is *about*. (Not `short_form` — that is a common mistake and returns 400.) |
| `query_type` | **Required.** One of the ~40 names — `ListAllAvailableImages`, `SubclassesOf`, `PartsOf`, `NeuronsPartHere`, `NeuronsSynaptic`, `NeuronsPresynapticHere`, `NeuronsPostsynapticHere`, `DownstreamClassConnectivity`, `UpstreamClassConnectivity`, `NeuronNeuronConnectivityQuery`, `NeuronInputsTo`, `SimilarMorphologyTo`, `anatScRNAseqQuery`, `clusterExpression`, `scRNAdatasetData`, `AnatomyExpressedIn`, `TransgeneExpressionHere`, `DatasetImages`, `AllDatasets`, `TermsForPub`, `FindStocks`, and more. |
| `offset`, `limit` | Paging, for the 16 query types that support it. `limit=0` (the default) means the function's own page size. |
| `include_graph` | Include the graph structure alongside the table. |
| `force_refresh` | Bypass the cache. |

The response is a table: `headers` (one entry per column, carrying a `title`, a `type` and an
`order`), `rows`, and `count`. **`count` is the number of results that exist, which is not always the
number of rows returned** — see [Partial answers](#partial-answers).

## `/query_connectivity`

```
GET /query_connectivity?upstream_type=DA1 lPN&downstream_type=Kenyon cell
```

| Parameter | |
|---|---|
| `upstream_type`, `downstream_type` | Neuron type labels, synonyms or FBbt ids. **At least one is required**; giving one asks "everything downstream of / upstream of this". |
| `weight` | Minimum synapse count for a connection to be reported. Default 5. |
| `group_by_class` | `true` aggregates to one row per class pair, with `pairwise_connections`, `average_weight` and `percent_connected`. Default is one row per neuron pair. |
| `exclude_dbs` | Comma-separated dataset symbols to leave out. Defaults to `hb,fafb` — see below. Pass `exclude_dbs=` (empty) for every dataset. |
| `include_graph` | Attach a graph structure alongside the table. |
| `force_refresh` | Bypass the cache. |

### A type means its subclasses too

Asking for `Kenyon cell` asks for Kenyon cells *and every class beneath it*. This is not a
convenience: in FBbt the classes people name are usually not the classes individual neurons are
typed to. `Kenyon cell` (`FBbt_00003686`) has **zero** directly-typed instances — all ~16,000 hang
off its 38 subclasses — so matching the named class alone answers the most obvious question in the
mushroom body with an empty table, which reads as "these cells are not connected".

The response says what it did, in a `resolved` block: which term each label was taken to mean, how
many classes the expansion covered, and how many individuals those classes hold. Worth reading when
a count surprises you.

```json
"resolved": {
  "upstream":   {"query": "DA1 lPN", "id": "FBbt_00067363",
                 "label": "adult antennal lobe projection neuron DA1 lPN",
                 "classes_searched": 1, "instances": 68},
  "downstream": {"query": "Kenyon cell", "id": "FBbt_00003686", "label": "Kenyon cell",
                 "classes_searched": 38, "instances": 15994}
}
```

Labels resolve through exact match, then case-insensitive, then exact synonym, then — as a last
resort — the only term containing the string. That last tier is what makes `DA1 lPN` find *adult
antennal lobe projection neuron DA1 lPN*, and when it fires it says so in `warnings`. Two or more
candidates are never guessed between: the error lists them.

### How long a broad type takes

Expansion makes some questions large. `DA1 lPN → Kenyon cell` is 68 individuals against 15,994 and
answers in about 5s; `Tm1 → T3` is 4,915 against 5,430 and has been measured between 30 and 60s on a
cold cache. The query is driven from whichever side has fewer individuals, which is worth several
times the difference on an asymmetric pair, but a genuinely big walk is a genuinely big walk.

The result is cached, so only the first caller waits — which is why the client's read timeout
defaults to 180s rather than 60s. A workshop room asking the same broad question at the same second
coalesces onto one query rather than 80.

### Why `hb` and `fafb` are excluded by default

Both are good data. The reason is **double-counting**, and it is about the shape of the answer
rather than the quality of the source:

`fafb` (VFB CATMAID Adult Brain) and `fw` (FlyWire v783) are two reconstructions of *the same EM
volume*. A neuron traced in both appears twice, so a connection found in both is counted twice, and
"how many partners does this cell have" silently doubles for the cells that happen to have been
traced in both. FlyWire is the proofread whole-brain segmentation of that volume, so it is the one
kept.

`hb` (hemibrain v1.2.1) is a partial volume — one hemisphere of one female brain — largely
superseded for whole-brain questions by `fw` and `mc` (male CNS v0.9). Its cells overlap heavily in
*type* with those two without being the *same* cells, which inflates per-type counts in a way that is
easy to misread as biological variation.

The cost of this default is that a plain query does not reproduce a published hemibrain figure. To
do that, name the dataset you want by excluding the others, or pass `exclude_dbs=` to get everything
and deduplicate yourself. `/list_connectome_datasets` gives the symbols.

## `/get_hierarchy`

```
GET /get_hierarchy?id=FBbt_00005801&relationship=part_of&direction=both&max_depth=1
```

| Parameter | |
|---|---|
| `id` | **Required.** A VFB short_form. |
| `relationship` | `part_of` (default) or `subclass_of`. |
| `direction` | `descendants`, `ancestors`, or `both` (default). |
| `max_depth` | How many steps out from the term. Default 1. |

This is the query behind the ROI browser on the VFB site: "what is inside the mushroom body, and
what is the mushroom body inside of". `part_of` walks anatomical containment, `subclass_of` walks the
ontology. Depth is worth keeping small — `part_of` descendants of a large region fan out quickly.

## `/search`

```
GET /search?query=mushroom body output neuron&limit=25
```

| Parameter | |
|---|---|
| `query` (or `q`) | **Required.** Free text: a name, a synonym, a symbol, an ID, a bare connectome bodyId. |
| `rows` | How deep to fetch candidates before ranking. Default 500. Raise it if a known-good hit is missing. |
| `limit` | Page size of the returned, ranked list. |
| `filter_types`, `exclude_types` | Hard filters (Solr `fq`) — a term either passes or is not returned. |
| `boost_types`, `demote_types` | Soft preferences — reorder the ranked list without dropping anything. |
| `unique` | Collapse the label/synonym rows so each term appears once. Default false. |

The ranking is not Solr's. It is three stages — an `edismax` query that ANDs a wildcard OR-group per
token, a synonym explosion that emits one row per matching synonym, and a comparator ported from the
website's JavaScript — and the third stage is what decides the order a person actually sees. This is
why a "top hit" comparison done at the Solr level describes an order nobody experiences. The full
account, including the six divergent copies of this configuration that existed across three repos, is
in [the search config comparison](search-config-comparison.md).

### Type names are validated

All four type parameters are checked against the live facet vocabulary before Solr is asked. A name
that does not exist is a **400** naming the parameter, the value and the closest real names:

```
GET /search?query=neuron&filter_types=Neurone
400  {"error": "filter_types: unknown type Neurone. Did you mean: neuron, neuron_projection_bundle? GET /facets lists every type name."}
```

This replaces the previous behaviour, which was a 200 with zero rows — indistinguishable from "that
type exists and nothing matched", and the reason a misspelling could look like a biological result.
Matching is case- and separator-insensitive (`NERVOUS-SYSTEM` resolves to `nervous_system`), so the
capitalisation you see in a row's `facets_annotation` works as an input. Prefixes deliberately do
**not** match: `neuro` is not `neuron`, because silently widening a filter is worse than rejecting it.
If the vocabulary cannot be fetched the check **fails open** — search keeps working, unvalidated.

### `boost_types` / `demote_types` now change the order

They previously changed the Solr score and nothing else, because the comparator that produces the
final order ranks on label text and never consults that score — so the parameters were accepted,
documented, and invisible. The boost is now also applied to the ranked list: boosted types move to the
front, demoted types to the back, and the comparator's order is preserved *within* each of the three
groups. Nothing is added or removed, so a demote is still not a filter — use `exclude_types` for that.
A type named in both wins the boost.

(Underneath, a demote is expressed to Solr as `(*:* -facets_annotation:X)^100` — a positive boost on
everything that is *not* X. The website's `^0.001` is a tiny positive boost, which demotes nothing,
and Solr rejects a negative one with a 500.)

### `unique` and `distinct_terms`

`/search` returns one row per matching *label or synonym*, which is how the website's dropdown works —
so `count` is legitimately larger than the number of terms, and a term with three matching synonyms
appears three times. Every response now reports `distinct_terms` alongside `count`, and `unique=true`
collapses the rows to one per term (keeping the highest-ranked occurrence) before `limit` is applied,
so a page of 25 is 25 distinct terms.

## `/facets`

```
GET /facets                      # every type name, with how many terms carry it
GET /facets?contains=lineage     # filtered, case- and separator-insensitive
```

The vocabulary that the four type parameters are validated against: 233 names at the time of writing,
each with a `docs` count, sorted by count. This is the list to offer in a UI and the list to check a
name against before sending it. Cached for `VFBQUERY_FACET_VOCAB_TTL` seconds (default 3600); returns
**503** if Solr cannot be reached, with a message noting that search itself still works.

## `/xref`

```
GET /xref?id=VFB_jrchjtdb                    # forward: every accession VFB holds
GET /xref?accession=1734350908&db=hb         # reverse: which term is this?
```

| Parameter | |
|---|---|
| `id` | Forward direction: a VFB short_form. |
| `accession` | Reverse direction: an external id — hemibrain bodyId, FlyWire root id, CATMAID skeleton id, FlyBase accession. |
| `db` | Optional filter, matching a site's symbol (`hb`), short_form or label, whole-string and case-insensitively. |

Rows carry `id`, `label`, `db`, `db_label`, `site_id`, `accession`, `is_data_source` and `link`.

The reverse direction is search-plus-confirmation, not search alone: each candidate is checked
against its own xref list and returned only if it really carries that accession. That is the point of
the endpoint. No accession is indexed anywhere in VFB — the only reason a bodyId is findable at all
is that VFB writes it into the label (`DA1_lPN_R (FlyEM-HB:1734350908)`) — so a free-text search on a
bare number will happily rank a near-miss first. **An accession VFB does not hold returns no rows**,
which is the correct answer; the alternative is a confidently wrong neuron.

## `/combine`

Set algebra over the results of the other endpoints: `calyx AND lateral_horn`,
`mb_dan NOT octopaminergic`, `[a OR b] NOT c`, with the reading of the expression returned alongside
the answer. It has [a reference page of its own](combine-endpoint.md), including about twenty worked
biological examples.

## Partial answers

The failure mode worth designing against here is not an error — it is a **plausible incomplete 200**.
A connectivity query whose type never resolved returns zero rows, which looks exactly like a
genuinely unconnected pair. A result set past the row cap returns 25,000 rows and a `count` of 60,002.
A fallback path running while Neo4j is unavailable returns the subset it can reach.

Every one of those attaches a top-level **`warnings`** list to the response. The convention is: a
`warnings` key means *this 200 is well-formed but partial*. The client re-raises them as Python
warnings from every endpoint. If you are calling the API directly, check for the key — a response
carrying `warnings` should not be treated as an answer without reading them.

`/combine` goes further, because set algebra over a truncated input is not partially right but wrong:
`require_complete=true` turns truncation into a 409 refusal.

## Errors and backpressure

| Status | Means |
|---|---|
| 400 | The request is malformed, and the body's `error` is a sentence saying how. |
| 404 | Unknown path, or a path not in `ALLOWED_PATHS` for your network. |
| 409 | `/combine` with `require_complete=true`, where an operand was truncated. |
| 500 | A genuine fault. `detail` carries `"ExcType: message"`. |
| 503 | Overloaded — the queue is full. Honour `Retry-After`. |

The 503 is a real design feature rather than a failure: the service holds a bounded queue in front of
a process pool, and shedding early is what keeps the pool answering the requests it accepted. In a
workshop room this matters less than it sounds, because the second half of the design is that
identical in-flight queries are **coalesced** onto one worker and results are cached for five
minutes. Eighty people running the same cell is one backend query, not eighty.

## Reading the tables

Every table response carries `headers`, and the header entry for each column declares a `type`. Two
of those types matter when you write code against the API:

`selection_id` marks the **identity column** — the term each row is *about*, and the column the
website uses for "add to search". It is not reliably the first column, and its name varies by query
type. Anything that matches rows across two different queries must match on this column;
[`/combine`](combine-endpoint.md) does, and getting it wrong is the single most likely way to compute
a wrong intersection.

The list-valued columns arrive pipe-joined, and link and thumbnail columns arrive as HTML. The
client's DataFrame adapter unwraps both.
