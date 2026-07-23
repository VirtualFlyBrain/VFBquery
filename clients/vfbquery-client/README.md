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
| `search` | `search_terms` edismax (Solr `ontology` core) | ✅ works today; repoint to `/search` once it ships |
| `xref` | `/xref` | ⏳ needs server endpoint (plan C3) |

`search` runs the **same** `edismax` query as the MCP `search_terms` (ranked / fuzzy / synonym-aware),
so name→id resolution in `get_instances` etc. uses that — **not** `resolve_entity`, which is
FlyBase-Chado exact resolution and won't resolve ontology term names. Passing a short_form id always
works directly. `search_url` in the constructor can be pointed at a future cached `/search` route to
keep the query config server-side.

## Licence

GPL-2.0-or-later, matching VFBquery.
