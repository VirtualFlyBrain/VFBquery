# Getting started

The fastest route into VFB data is the lightweight client. It talks to the cached HTTP service, so
your machine does no graph work and installs nothing heavy.

## Install

```bash
pip install vfbquery-client
```

That is `requests` and `pandas` and nothing else — seconds on a fresh Colab runtime. There is no
`navis`, no `setuptools<58` pin and no two-minute term-cache warm-up on first import, because none of
that happens on your side of the wire.

If instead you want the query functions *in process* — inside a service of your own, or where a
network hop is unacceptable — install the full library:

```bash
pip install vfbquery
```

The rest of this page uses the client. The library's own function-level reference is the
[query catalogue](_root/queries-reference.md).

## First queries

```python
from vfbquery_client import VfbClient

vfb = VfbClient()
```

`VfbClient()` points at the public service by default. Pass `base_url=` to talk to your own
deployment, or set `VFB_API_URL` in the environment.

**Look a term up by name.** Most methods accept a name, a symbol or an ID interchangeably: anything
that is not already an ID is resolved through the search endpoint first.

```python
info = vfb.term("DA1 lPN")
info["Name"], info["Id"]
```

**Search**, when you do not know what you are looking for yet:

```python
hits = vfb.search("mushroom body output neuron", limit=20)
hits[["short_form", "label", "types"]].head()
```

The ordering here is the website's ordering, not Solr's — the same three-stage construction the VFB
site uses, ported server-side. See [design notes](search-config-comparison.md) if you care why that
distinction matters.

**Instances of a type** — every imaged or reconstructed neuron of a class:

```python
vfb.get_instances("DA1 lPN")          # a DataFrame
```

**Connectivity**, by type or for one neuron:

```python
vfb.get_connected_neurons_by_type("DA1 lPN", "Kenyon cell")
vfb.get_neuron_connectivity("VFB_00100000")
```

**Similar morphology** (NBLAST, precomputed):

```python
vfb.get_similar_neurons("VFB_00100000")
```

**Cross-reference an external accession** — a hemibrain bodyId, a FlyWire root id, a CATMAID skeleton
id — in either direction:

```python
vfb.xref(accession="1734350908")      # → the VFB term
vfb.xref(id="VFB_jrchjtdb")           # → every external id VFB holds for it
```

**Combine results**, when the question spans more than one query — see the
[`/combine` reference](combine-endpoint.md) for the whole language:

```python
vfb.combine("a NOT b",
            {"a": "NeuronsPartHere:FBbt_00007053",
             "b": "NeuronsPartHere:FBbt_00007401"})
```

## Everything comes back as a DataFrame

Every method that returns a table returns a `pandas.DataFrame`, with the service's typed columns
already unwrapped: pipe-joined multi-values are split into lists, and link and thumbnail cells are
left as the HTML the service returns so a notebook can render them.

```python
from IPython.display import HTML
HTML(vfb.get_instances("DA1 lPN").to_html(escape=False))
```

## When an answer is incomplete, you are told

This is worth knowing before you build anything on top. A VFB query can return a *partial* answer
that looks exactly like a complete one — a connectivity query whose type never resolved returns zero
rows, which is indistinguishable from a genuinely unconnected pair; a fallback path that runs while
Neo4j is unavailable returns the rows it can reach and no marker that the rest exist.

The service attaches a `warnings` list to any response like that, and the client re-raises those as
Python warnings from every endpoint. So:

```python
import warnings
warnings.simplefilter("error")        # in a script where a partial answer is a bug
```

turns a quietly-degraded answer into an exception. In a notebook the default is fine — you will see
the warning printed under the cell. For [`/combine`](combine-endpoint.md) specifically there is a
stronger form, `require_complete=True`, which refuses (HTTP 409) rather than performing set algebra
over a truncated input.

## Errors

Everything the service can explain comes back as a `VfbError` carrying the service's own sentence —
which expression failed to parse, which operand was truncated, which name was never bound:

```python
from vfbquery_client import VfbError

try:
    vfb.combine("a AND c", {"a": "NeuronsPartHere:FBbt_00007401"})
except VfbError as exc:
    print(exc)     # names `c` as undefined, rather than "400 Client Error"
```

A busy service returns 503 with a `Retry-After`; the client raises `VfbError` for that too. Genuine
server faults (5xx without a message) raise the underlying `requests` error, because those are not
yours to fix.

## Next

- [The HTTP API](http-api.md) — every endpoint, if you would rather call it directly.
- [`/combine`](combine-endpoint.md) — set algebra over queries, with the biology worked through.
- [Client API reference](api/client.md) — every method and argument.
