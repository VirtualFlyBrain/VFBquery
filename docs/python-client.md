# The Python client

`vfbquery-client` is a deliberately small package: `requests`, `pandas`, and about six hundred lines.
It exists because the full `vfbquery` install is heavy — `navis`, `psycopg`, `vfb_connect`, a
`setuptools<58` pin, and a term-cache warm-up on first import — and none of that weight buys anything
for someone who just wants to ask VFB a question from a notebook. All of it lives on the server side
of the wire instead.

```bash
pip install vfbquery-client
```

For the method-by-method reference see [the API reference](api/client.md); this page is about the
things you would otherwise have to discover by being surprised.

## Names, symbols and IDs are interchangeable

Every method that takes a term accepts `"DA1 lPN"`, `"FBbt_00067363"`, or a symbol. Anything that is
not already an ID is resolved through `/search` first, and `/search` is the *website's* search, so
what resolves in the browser resolves here.

The client therefore carries **no Solr configuration of its own** — no query construction, no boost
list, no synonym handling. That is not an omission; it is the point. There were six divergent copies
of that configuration across three repositories, and the client existing as a seventh would have made
the problem worse rather than better.

## Everything tabular is a DataFrame

```python
vfb.get_instances("DA1 lPN")           # DataFrame
vfb.search("Kenyon cell")              # DataFrame
vfb.term("DA1 lPN")                    # dict — a single term is not a table
```

The adapter unwraps whichever envelope the endpoint used (`rows`, `connections`, a bare list, or a
lone object as a one-row frame) and splits the pipe-joined multi-value columns into lists. Link and
thumbnail cells are passed through as the HTML the service returns, so `to_html(escape=False)`
renders images inline in a notebook.

## `df.attrs` carries what the table cannot

A DataFrame has nowhere to put "here is how I read your expression" or "this is what each step
produced". `combine()` puts those in `df.attrs`:

```python
both = vfb.combine("calyx AND lh", {...})

both.attrs["as_read"]         # '(calyx AND lh)' — the brackets actually applied
both.attrs["plain_english"]   # a sentence
both.attrs["steps"]           # per-operation input_counts / result_count / why_empty
both.attrs["count"]           # the full size, which len(df) may not be if you passed limit=
both.attrs["operands"]        # what each name actually ran, and whether it was truncated
```

`attrs` survives most pandas operations but not all — check it before a heavy chain of transforms if
you need it later.

## Degraded answers raise Python warnings

Any endpoint that returns a partial answer says so in a `warnings` key, and the client re-raises
those as Python warnings from `_get` — so it covers every endpoint, including ones added later,
rather than each method having to remember to look.

This matters more than it sounds. The two cases that motivated it both return a well-formed 200: an
unresolved connectivity type returns zero rows, which is indistinguishable from a genuinely
unconnected pair; and a fallback path running while Neo4j was down returned 10 of 68 instances with
nothing marking it partial. In a script where a partial answer is a bug:

```python
import warnings
warnings.simplefilter("error")
```

## Errors carry the service's own sentence

```python
from vfbquery_client import VfbError
```

A 4xx whose body carries an `error` becomes a `VfbError` with that message — which expression failed
to parse, which operand was truncated, which name was never bound. This is a deliberate departure
from `raise_for_status()`, which would replace all of it with `"400 Client Error"`; for `/combine` in
particular, that is the difference between a fixable mistake and an opaque one. A 503 becomes a
`VfbError` too. A 5xx without a message raises the underlying `requests` error, because a server
fault is not the caller's to fix and should not be dressed up as one.

## Pointing it somewhere else

```python
VfbClient()                                        # the public service
VfbClient(base_url="http://localhost:8080")        # a local server
```

or set `VFB_API_URL` in the environment — which is how a workshop can move a whole room onto a
private deployment without editing a single notebook cell.

## What it does not do

No skeleton loading, no NBLAST *computation*, no 3D rendering. Those are heavy client operations and
they stay client-side, using the existing static SWC and mesh URLs; putting them on the shared
service would put a rendering job on the same request path as a term lookup. `get_vfb_link()` builds
a viewer URL from a set of IDs and is pure string work — no request at all.
