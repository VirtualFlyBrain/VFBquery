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
| `/combine` | Set algebra over the results of other queries. See [the reference](combine-endpoint.md). |
| `/resolve_entity`, `/resolve_combination` | FlyBase-Chado exact resolution (features, genotypes). Not a search — see the note below. |
| `/find_stocks`, `/find_combo_publications` | Stock and publication lookups for a resolved entity or combination. |
| `/list_connectome_datasets` | The connectome datasets currently loaded. |
| `/health`, `/status` | Liveness, version, pool and cache statistics. |

```{admonition} `/resolve_entity` is not the search endpoint
:class: warning

It is tiered exact→synonym→broad resolution against FlyBase-Chado, for FlyBase features. It returns
`NOT_FOUND` for a partial or fuzzy anatomy name, so it is the wrong tool for "what is this thing
called". Use `/search`.
```

`/get_hierarchy` and `/get_hierarchy_html` are registered routes but are absent from the service's
`ALLOWED_PATHS`, so they return 404 to anything outside the cluster network. That is longstanding and
is left as it is; whether to publish them is an open question, not an oversight.

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
| `boost_types`, `demote_types` | Soft boosts (Solr `bq`) — the website's filter chips. |

The ranking is not Solr's. It is three stages — an `edismax` query that ANDs a wildcard OR-group per
token, a synonym explosion that emits one row per matching synonym, and a comparator ported from the
website's JavaScript — and the third stage is what decides the order a person actually sees. This is
why a "top hit" comparison done at the Solr level describes an order nobody experiences. The full
account, including the six divergent copies of this configuration that existed across three repos, is
in [the search config comparison](search-config-comparison.md).

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
