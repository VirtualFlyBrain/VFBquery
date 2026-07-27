# vfbquery-client

A lightweight HTTP client for the [Virtual Fly Brain](https://virtualflybrain.org) query API
(the cached `v3-cached` / `ha_api` service). Pure `requests` + `pandas` — **no `navis`, no
`setuptools<58` pin, installs in seconds** — so notebooks (Colab included) and scripts get the common
`vfb_connect`-style queries without the heavy local stack.

> Part of the "VFB Connect as an API service" plan — see
> [`docs/vfbconnect-http-api-plan.md`](../../docs/vfbconnect-http-api-plan.md).

## Install

```bash
pip install vfbquery-client        # once published
# or, from this repo:
pip install clients/vfbquery-client
```

## Use

```python
from vfbquery_client import VfbClient
vfb = VfbClient()          # https://v3-cached.virtualflybrain.org, or $VFB_API_BASE

vfb.search("DA1 lPN")                              # ranked hits, website order
vfb.term("FBbt_00067363")                          # TermInfo (dict)
vfb.get_instances("adult antennal lobe projection neuron DA1 lPN")   # 68-row DataFrame
vfb.get_connected_neurons_by_type(                 # Tm1 -> T3, >=60 synapses
    upstream_type="transmedullary neuron Tm1",
    downstream_type="T3 neuron", weight=60)
vfb.get_similar_neurons("VFB_jrchjtdb")            # NBLAST matches, sorted by score
vfb.get_transcriptomic_profile("Kenyon cell")      # scRNAseq profile
vfb.get_vfb_link(["VFB_jrchjtdb", "VFB_fw035286"]) # shareable 3D-scene link
```

## Status

| Method | Endpoint | Implemented |
|---|---|---|
| `term` / `terms` | `/get_term_info` | ✅ |
| `get_instances` / `get_subclasses` | `/run_query` (+ `/search` to resolve a name) | ✅ |
| `get_connected_neurons_by_type` | `/query_connectivity` | ✅ |
| `get_neuron_connectivity` | `/run_query` | ✅ |
| `get_similar_neurons` | `/run_query SimilarMorphologyTo` | ✅ |
| `get_transcriptomic_profile` | `/run_query anatScRNAseqQuery` (+ `/search` to resolve a name) | ✅ |
| `list_connectome_datasets` | `/list_connectome_datasets` | ✅ |
| `get_vfb_link` | client-side | ✅ |
| `search` | `/search` | ✅ |
| `xref` | `/xref` | ✅ |

`/search` and `/xref` are new in this branch and go live with that VFBquery build. Against the public
deploy until then, this client works wherever it is given an **id**: everything routed through
`/run_query`, `/get_term_info`, `/query_connectivity` or `/list_connectome_datasets` answers today.
What does not is passing a *name* — `get_instances`, `get_subclasses` and
`get_transcriptomic_profile` resolve one through `_resolve_to_id`, which calls `/search`. So
`get_instances("FBbt_00067363")` returns its 68 rows now, while
`get_instances("adult antennal lobe projection neuron DA1 lPN")` will 404 until the build ships.

Point the client at a deploy that has them with `VfbClient(base_url=...)` or by setting
`VFB_API_BASE` in the environment.

### Search

`search` calls `/search`, which returns results **in the order the website shows them** — the server
runs a port of the website's own query construction, filters, boosts and ~370-line comparator. So
there is no Solr configuration in this client, and nothing to keep in step by hand. (Repointing the
website and the MCP at `/search` as well is the remaining step and lives outside this repo.)

One deliberate exception to "the order the website shows them": `/search` always applies an
exact-label boost that the website has no equivalent for, and it cannot be switched off. It exists
because the website loses exact matches outright — searching `neuron` ranks the term *neuron*
itself 705th by score, past the candidate cutoff, so no amount of re-sorting can recover it. The
boost only lifts a term whose label *is* the query, and the recall gate holds churn in the top ten
of unrelated queries at exactly zero, so in practice the difference shows up on the queries the
website was getting wrong and nowhere else.

```python
vfb.search("DA1 lPN")                              # top 50, ranked
vfb.search("kenyon cell", limit=None)              # everything (306 rows)
vfb.search("neuron", limit=10, filter_types=["Class"])
vfb.search("medulla", limit=10, demote_types=["Individual"])
```

Rows carry `short_form`, a display `label` (`"synonym (label)"` or `"label (short_form)"`),
`original_label`, `id`, `facets_annotation` and `unique_facets`.

`limit` is the page size. `rows` (default 500, the website's value) is how many candidates the server
asks Solr for, so it is a **ranking** knob, not a paging one — lowering it can drop the best answer
before ranking ever sees it. That is why name→id resolution inside `get_instances` and friends uses
`limit=1` rather than `rows=1`: rank the full candidate set, then take the top.

Resolution goes through this search, **not** `resolve_entity`, which is FlyBase-Chado exact resolution
and won't resolve ontology term names. Passing a short_form id always works directly and skips the
lookup entirely.

### Connectivity

`get_connected_neurons_by_type` takes two type names and returns the synaptic connections between
them, one row per partner pair.

```python
vfb.get_connected_neurons_by_type(upstream_type="transmedullary neuron Tm1",
                                  downstream_type="T3 neuron", weight=60)
```

`weight` is the minimum synapse count and is applied **server-side**, so the threshold in the call is
the threshold that ran. Its default is 5 — the server's own — rather than 0: omitting the parameter
does not mean "unfiltered", it means the server picks, so a client default of 0 would be a promise
the client cannot keep.

A type the server cannot resolve is a **warning plus zero rows**, not an error. Zero rows on their
own are ambiguous — a misspelt type and a genuinely unconnected pair look identical — so those
warnings are re-raised as Python `UserWarning`s rather than dropped:

```python
>>> vfb.get_connected_neurons_by_type("DA1 lPN", "Kenyon cell")
UserWarning: query_connectivity: Neuron type not found in VFB: 'DA1 lPN'.
             Use list_connectome_datasets() or check spelling.
```

Note that this endpoint wants a name the connectivity index knows, which is not always the term
label search would return — the warning is how you find that out.

### Warnings mean "this answer may be incomplete"

That re-raising is not specific to connectivity: **any** endpoint's `warnings` are surfaced, because
the service uses them for every case where a `200` is well-formed but partial. The other one you can
hit today is `get_instances` while the graph backend is briefly unavailable — the service falls back
to a SOLR extract that only sees instances with an aligned image, so you get a plausible subset:

```python
>>> vfb.get_instances("FBbt_00067363")
UserWarning: run_query: Neo4j unavailable (...); get_instances(FBbt_00067363) answered from the
             SOLR anatomy_channel_image fallback, which covers only instances with an aligned
             image and leaves source/dataset blank — this result may be partial.
```

Nothing in the returned rows distinguishes that from a complete answer, which is why it is worth not
running notebooks with warnings suppressed. Retrying a minute later is usually all it takes.

### Cross-references

`xref` converts between VFB ids and external database accessions, one direction per call:

```python
vfb.xref(id="VFB_jrchjtdb")             # -> every external accession VFB holds for that term
vfb.xref(id="VFB_jrchjtdb", db="hb")    # -> just the hemibrain one: 1734350908
vfb.xref(accession="1734350908", db="hb")   # -> back to VFB_jrchjtdb
```

Exactly one of `id=` or `accession=` is required; passing both raises rather than silently answering
a different question. `db` is optional and matches a site's symbol, short_form or label
case-insensitively (`"hb"`, `"neuprint_JRC_Hemibrain_1point2point1"`, `"Hemibrain"`), whole-string —
`"neuprint"` matches the site whose symbol *is* `neuprint`, not every site containing the word.

Rows carry `id`, `label`, `db`, `db_label`, `site_id`, `accession`, `is_data_source` and a ready-made
`link` into the external site (empty when that site has no link template).

The reverse direction is **confirmed, not guessed**. No Solr field indexes accessions — `term_info`
is `indexed=false` and is not in the `_text_` catch-all — so the server searches for candidates and
then checks each one's own xref list for an exact match. An accession VFB does not hold comes back
**empty** rather than as the best-ranked near miss, which is the failure mode this replaces.

## Licence

GPL-2.0-or-later, matching VFBquery.
