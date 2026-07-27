# VFBquery

VFBquery answers questions about the [Virtual Fly Brain](https://virtualflybrain.org) knowledge graph
— *Drosophila* neuroanatomy, connectomics, expression and single-cell transcriptomics — and it does
so in three shapes, from the same code:

**As a Python library.** `pip install vfbquery`, call `get_term_info` or `run_query` in process. This
is the original shape and what the VFB services themselves use.

**As an HTTP service.** The same queries behind an aiohttp front end (`ha_api`), deployed as
`v3-cached.virtualflybrain.org`, with a process pool, request coalescing, a result cache and queue
backpressure in front of them. This is what the website and the MCP server talk to.

**As a lightweight HTTP client.** `pip install vfbquery-client` — `requests` and `pandas`, nothing
else. It installs in seconds on a fresh Colab runtime, needs no `navis` and no `setuptools` pin, and
returns DataFrames. If you are writing a notebook, this is the one you want.

```{admonition} Which one do I want?
:class: tip

If you are exploring, teaching, or writing a notebook, start with the
[client](getting-started.md) — nothing to compile, and it works from Colab.
Reach for the library instead when you need VFBquery *inside* a service, or when you want the query
functions without a network hop.
```

## Start here

```{toctree}
:maxdepth: 2
:caption: Using it

getting-started
http-api
combine-endpoint
python-client
```

```{toctree}
:maxdepth: 2
:caption: API reference

api/client
api/combine
```

```{toctree}
:maxdepth: 1
:caption: The query catalogue

_root/queries-reference
_root/schema
_root/readme
```

```{toctree}
:maxdepth: 1
:caption: Running and releasing it

_root/caching
_root/performance
_root/releasing
```

```{toctree}
:maxdepth: 1
:caption: Design notes

vfbconnect-http-api-plan
search-config-comparison
```

## A worked question, three ways

"Which neurons have arbours in both the mushroom body calyx and the lateral horn?" — a question no
single VFB query answers, because each query returns one region's neurons.

With the client:

```python
from vfbquery_client import VfbClient

vfb = VfbClient()
both = vfb.combine(
    "calyx AND lateral_horn",
    {"calyx":        "NeuronsPartHere:FBbt_00007401",
     "lateral_horn": "NeuronsPartHere:FBbt_00007053"},
)
print(both.attrs["plain_english"])   # neurons in both lists
print(len(both))
```

Over HTTP directly:

```
GET /combine?expr=calyx AND lateral_horn
            &calyx=NeuronsPartHere:FBbt_00007401
            &lateral_horn=NeuronsPartHere:FBbt_00007053
```

And in the library, by calling `run_query` twice and intersecting on the identity column yourself —
which is precisely the fiddly part [`/combine`](combine-endpoint.md) exists to get right, because
"the identity column" is not always the first one and duplicate rows are common.

## Where things live

| | |
|---|---|
| Source | [github.com/VirtualFlyBrain/VFBquery](https://github.com/VirtualFlyBrain/VFBquery) |
| Library on PyPI | [`vfbquery`](https://pypi.org/project/vfbquery/) |
| Client on PyPI | [`vfbquery-client`](https://pypi.org/project/vfbquery-client/) |
| Live service | [v3-cached.virtualflybrain.org](https://v3-cached.virtualflybrain.org/health) |
| The site itself | [virtualflybrain.org](https://virtualflybrain.org) |

This documentation is built for version **{{ release }}**.
