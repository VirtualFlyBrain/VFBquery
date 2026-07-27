# `vfbquery.combine`

The set-algebra engine behind [`/combine`](../combine-endpoint.md).

This module is worth documenting on its own because of what it deliberately does **not** contain.
Everything decidable without the network lives here — tokenising and parsing the expression,
precedence and brackets, rendering it back as English, choosing the identity column, diagnosing
namespace mismatches, the universe and its degeneracies, and the lossless row and header merge. It
imports nothing outside the standard library.

The part that needs a server — turning `NeuronsPartHere:FBbt_00007401` into an actual query on the
process pool, under the cache and the coalescer — lives in `vfbquery.ha_api` and is the thin half.

That split is why the expression tests run in well under a second, why a bracketing bug can be
reproduced without a Neo4j, and why a client can validate an expression before spending a request on
it.

## Errors

```{eval-rst}
.. autoclass:: vfbquery.combine.CombineError
   :show-inheritance:
```

## Parsing an expression

```{eval-rst}
.. autofunction:: vfbquery.combine.tokenize
.. autofunction:: vfbquery.combine.parse
.. autofunction:: vfbquery.combine.to_expression
.. autofunction:: vfbquery.combine.describe
.. autofunction:: vfbquery.combine.plain_english
```

### Nodes

```{eval-rst}
.. autoclass:: vfbquery.combine.Operand
   :members:
.. autoclass:: vfbquery.combine.Complement
   :members:
.. autoclass:: vfbquery.combine.BinOp
   :members:
```

## Identifying rows

```{eval-rst}
.. autofunction:: vfbquery.combine.id_column
.. autofunction:: vfbquery.combine.namespace_of
.. autofunction:: vfbquery.combine.namespaces_in
```

## Operands and the universe

```{eval-rst}
.. autoclass:: vfbquery.combine.OperandResult
   :members:
.. autoclass:: vfbquery.combine.Universe
   :members:
.. autofunction:: vfbquery.combine.implicit_universe
```

## Evaluating

```{eval-rst}
.. autofunction:: vfbquery.combine.evaluate
```

## Merging results without losing columns

```{eval-rst}
.. autofunction:: vfbquery.combine.merge_rows
.. autofunction:: vfbquery.combine.merge_headers
.. autofunction:: vfbquery.combine.build_rows
```
