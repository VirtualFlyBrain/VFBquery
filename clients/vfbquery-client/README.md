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
vfb = VfbClient()                                  # defaults to https://v3-cached.virtualflybrain.org

vfb.search("DA1 lPN")                              # ranked hits, website order
vfb.term("FBbt_00067363")                          # TermInfo (dict)
vfb.get_instances("adult antennal lobe projection neuron DA1 lPN")   # 68-row DataFrame
vfb.get_connected_neurons_by_type(                 # DA1 lPN -> Kenyon cell, weighted
    upstream_type="adult antennal lobe projection neuron DA1 lPN",
    downstream_type="Kenyon cell", weight=10)
vfb.get_similar_neurons("VFB_jrchjtdb")            # NBLAST matches, sorted by score
vfb.get_transcriptomic_profile("Kenyon cell")      # scRNAseq profile
vfb.get_vfb_link(["VFB_jrchjtdb", "VFB_fw035286"]) # shareable 3D-scene link
```

## Status

| Method | Endpoint | Works today |
|---|---|---|
| `term` / `terms` | `/get_term_info` | ✅ |
| `get_instances` / `get_subclasses` | `/run_query` | ✅ |
| `get_connected_neurons_by_type` | `/query_connectivity` | ✅ |
| `get_neuron_connectivity` | `/run_query` | ✅ |
| `get_similar_neurons` | `/run_query SimilarMorphologyTo` | ✅ |
| `get_transcriptomic_profile` | `/run_query anatScRNAseqQuery` | ✅ |
| `list_connectome_datasets` | `/list_connectome_datasets` | ✅ |
| `get_vfb_link` | client-side | ✅ |
| `search` | `/search` | ✅ |
| `xref` | `/xref` | ⏳ needs server endpoint (plan C3) |

### Search

`search` calls `/search`, which returns results **in the order the website shows them** — the server
runs the website's own query construction, filters, boosts and ~370-line comparator, and the website
and the MCP call the same endpoint. So there is no Solr configuration in this client, and nothing to
keep in step by hand.

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

## Licence

GPL-2.0-or-later, matching VFBquery.
