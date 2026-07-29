# `/combine` — asking questions no single VFB query can answer

Plan item **C5**. Implemented in `src/vfbquery/ha_api.py` (`handle_combine`, the thin part) and
`src/vfbquery/combine.py` (the grammar, the algebra, the explanations and the column merge — pure
standard library, no network).

Every VFB query answers one question: *what is inside the calyx*, *what does DNa02 talk to*, *what is
morphologically similar to this neuron*. Plenty of real questions are two or three of those with a
word like "and", "but not" or "either" between them:

> Which projection neurons arborise in **both** the calyx **and** the lateral horn?
> Which medulla neurons reach the lobula **but not** the lobula plate?
> What does DNa02 target that DNp09 does **not**?

`/combine` runs the queries, matches their results up by term ID, and applies the set operation. It
returns the merged rows — not just the IDs — together with a step-by-step account of what it did.

```
GET /combine?expr=calyx AND lh
            &calyx=NeuronsPartHere:FBbt_00007401
            &lh=NeuronsPartHere:FBbt_00007053
```

Contents: [the request](#1-the-request) · [operators in plain English](#2-the-operators-in-plain-english) ·
[precedence and brackets](#3-precedence-and-brackets) · [what everything means](#4-what-everything-means-the-universe) ·
[how rows are matched](#5-how-rows-from-different-queries-are-matched) ·
[how columns are merged](#6-how-columns-are-merged-nothing-is-dropped) · [the response](#7-reading-the-response) ·
[worked biological examples](#8-worked-biological-examples) · [the traps](#9-the-traps-and-what-the-endpoint-says-about-them) ·
[limits](#10-limits) · [Python client](#11-from-python) · [going bigger](#12-expressions-bigger-than-the-operand-limit)

---

## 1. The request

Two kinds of parameter. `expr` is the expression; **every other parameter is an operand** — its name
is a name you may use inside the expression, and its value is the query to run.

| Parameter | Meaning |
|---|---|
| `expr` (or `expression`, `q`) | The expression. Required. |
| *anything else* | An operand: `&calyx=NeuronsPartHere:FBbt_00007401` |
| `universe` | What "everything" means for complements. See [§4](#4-what-everything-means-the-universe). |
| `limit` | Return at most this many rows. `count` still reports the full size. |
| `require_complete` | `true` → refuse (409) rather than warn if any operand was truncated. |
| `explain_only` | `true` → return the reading of the expression without running any query. |

Operand names are yours to choose (`calyx`, `lh`, `dan`), which is what lets an expression read like
the question it encodes rather than like `op1 AND op2`. The names reserved by the endpoint itself are
`expr`, `expression`, `q`, `universe`, `limit`, `offset`, `require_complete`, `explain_only`,
`order_by` and `force_refresh` — so an operand cannot be called any of those.

Three of them, `offset`, `order_by` and `force_refresh`, are **reserved but do nothing yet**: pass
one and it is ignored, not rejected. They are held back rather than left free because on the day
paging or caller-chosen ordering is added, a saved expression that had been using `offset` as an
operand name would quietly start meaning something else. Use `limit` for a shorter answer today.

An operand value takes one of three forms:

| Form | Example | What it does |
|---|---|---|
| `<QueryType>:<id>` | `NeuronsPartHere:FBbt_00007401` | Runs it exactly as `/run_query` would — same cache entry, so a room of people running the same example costs one Neo4j query, not forty. Any of the ~40 `/run_query` types. |
| `search:<text>` | `search:kenyon cell` | Runs the ranked free-text `/search`. |
| `ids:<id>,<id>,…` | `ids:VFB_00101567,VFB_jrchjtdb` | A literal set — no query at all. This is how an outside list (a paper's supplementary table, a hand-curated set, **the output of a previous `/combine`**) enters the algebra. |

The three prefixes cannot collide with a query type: every `/run_query` type name is CamelCase, and
the query-type branch is tried first regardless.

---

## 2. The operators, in plain English

You do not need to know Boolean algebra to use this. Each operator below is stated as the English
sentence it means; the endpoint echoes the same sentence back in `plain_english` so you can check it
read you correctly.

| Write | Means | Also accepted |
|---|---|---|
| `a OR b` | everything either query found, listed once | `\|`, `+`, `∪`, `union`, `any`, `either`, `plus`, `a in either b` |
| `a AND b` | only what **both** found | `&`, `∩`, `*`, `intersect`, `both`, `found in both`, `present in both` |
| `a NOT b` | what `a` found, minus anything `b` also found | `-`, `\`, `minus`, `except`, `without`, `excluding`, `but not` |
| `a XOR b` | what one side found but not the other — i.e. how they **differ** | `^`, `⊕`, `difference`, `either but not both`, `only one of`, `in exactly one of` |
| `a NAND b` | everything **except** the overlap | `not both` |
| `a NOR b` | what **neither** found | `neither` |
| `a XNOR b` | what the two sides **agree** on — in both, or in neither | `agree`, `same in both`, `in both or neither` |
| `NOT a` | everything except what `a` found (unary — see [§4](#4-what-everything-means-the-universe)) | |

Case is irrelevant and whitespace is free, so `calyx and lh`, `calyx AND lh` and `calyx & lh` are the
same request. The response always names the operator canonically (`AND`), so the reply teaches the
standard vocabulary even when the request did not use it.

**The four you will actually use** are `OR`, `AND`, `NOT` and `XOR`. `NAND`, `NOR` and `XNOR` are
complements, and complements need [a universe](#4-what-everything-means-the-universe) before they
mean anything; the endpoint warns you when you have used one in a way that cannot give a useful
answer.

One deliberate non-alias: **`AND NOT` is two operators, not one.** `a AND NOT b` parses as `a AND
(NOT b)`, not as `a NOT b`. They agree under the default universe but diverge under an explicit one,
and someone who typed two operators is entitled to both. Write `a NOT b` or `a but not b` if that is
what you mean.

---

## 3. Precedence and brackets

When you write three or more operands without brackets, something has to decide the order. The rule,
**loosest binding first**:

| Binding | Operators | Read as |
|---|---|---|
| loosest | `OR`, `NOR` | joined last |
| middle | `XOR`, `XNOR` | |
| tightest | `AND`, `NAND`, `NOT` | joined first |

Everything is **left-associative**: equal-strength operators group left to right. So `a NOT b NOT c`
is `((a NOT b) NOT c)` — successive exclusions, which is what "in the antennal lobe, but not the
calyx, and not the lateral horn" means in English.

`NOT` binds with `AND` on purpose. Set difference *is* an intersection with a complement, and putting
it any looser would make `a AND b NOT c` mean `a AND (b NOT c)` — the same answer in that particular
case, but not once an `OR` is involved.

### The brackets

`[ ]`, `( )` and `{ }` all work and are interchangeable. **In a URL, prefer `[ ]`**: parentheses are
legal in a query string but tend to be mangled by shells, curl invocations and copy-paste, whereas
square brackets survive. Nesting is unlimited.

### Why bracketing changes the answer

The classic case is an `OR` on one side of an `AND`:

| Expression | Read as | Question it asks |
|---|---|---|
| `mb AND dan OR oct` | `((mb AND dan) OR oct)` | "MB dopaminergic neurons, **plus every octopaminergic neuron anywhere**" |
| `mb AND [dan OR oct]` | `(mb AND (dan OR oct))` | "MB neurons that are dopaminergic **or** octopaminergic" |

Only the second is the question anyone meant. The first quietly adds a few thousand unrelated
neurons, and the row count is large enough to look like a real answer. This is the single most common
way a combination goes wrong, and it is why `as_read` exists in every response.

The same shape appears wherever an exclusion follows an alternative:

| Expression | Read as | Question |
|---|---|---|
| `eb OR pb NOT fb` | `(eb OR (pb NOT fb))` — no! `NOT` binds tighter than `OR` | "everything in EB, plus PB-not-FB neurons" |
| `[eb OR pb] NOT fb` | `((eb OR pb) NOT fb)` | "neurons in EB or PB, excluding anything in FB" |

And where a complement's scope matters:

| Expression | Read as | Question |
|---|---|---|
| `a AND b NOT c` | `((a AND b) NOT c)` | "in both a and b, then drop anything in c" |
| `a AND [b NOT c]` | `(a AND (b NOT c))` | "in a, and also in the part of b that is not in c" |

Those two often agree — but not always, and not when `a` and `c` overlap in ways `b` does not.

### Checking before you pay

`explain_only=true` returns the reading with no query run at all:

```
GET /combine?expr=mb AND [dan OR oct]&explain_only=true
            &mb=NeuronsPartHere:FBbt_00005801
            &dan=search:dopaminergic neuron
            &oct=search:octopaminergic neuron
```

```json
{
  "as_read": "(mb AND (dan OR oct))",
  "plain_english": "only the things found by BOTH NeuronsPartHere of FBbt_00005801 and anything found by search for 'dopaminergic neuron', together with anything found by search for 'octopaminergic neuron' (everything from either side, listed once)",
  "operands": {"mb": "NeuronsPartHere:FBbt_00005801", "dan": "search:dopaminergic neuron", "oct": "search:octopaminergic neuron"},
  "unused_operands": []
}
```

It costs nothing, so it is worth calling on any expression whose grouping you would otherwise be
assuming. Every full response carries the same `as_read` and `plain_english` fields.

---

## 4. What "everything" means (the universe)

`NOT a`, `NAND`, `NOR` and `XNOR` are **complements**: they say "everything except…". That has no
answer until "everything" is defined, and VFB holds roughly 750,000 terms — "every term that is not a
Kenyon cell" is never the intended answer.

**By default, "everything" means everything your own queries found** — the union of all the operands
used in this expression. That default is what makes `a NOT b` behave the way you expect, and it makes
three of the complement operators degenerate in ways that are worth knowing:

| With the default universe | Behaves as | Why |
|---|---|---|
| `a NOR b` | always empty | "in neither" has nothing left to be in when "everything" *is* the two sides. |
| `a NAND b` | identical to `a XOR b` | "everything except the overlap", where everything is the two sides. |
| `a XNOR b` | identical to `a AND b` | the "or in neither" half is empty by construction. |
| `NOT a` alone | always empty | with only one operand, the universe *is* `a`. |

The endpoint warns rather than silently returning zero rows. To make a complement mean something,
state the universe:

```
&universe=SubclassesOf:FBbt_00005106      # "of all neuron types…"
&universe=DatasetImages:Nern2024          # "of everything in this dataset…"
&universe=ids:VFB_1,VFB_2,VFB_3           # "of this list…"
```

`universe=` takes the same three forms as an operand. With it, `a NOR b` becomes a real question:
*of the neurons in this dataset, which innervate neither region?* The universe's own columns are kept
in the merged output too, so a universe-only row still comes back with its label rather than as a
bare ID.

---

## 5. How rows from different queries are matched

Different query types return completely different tables. `SubclassesOf` gives you `id, label, tags,
template, technique, thumbnail`; `SimilarMorphologyTo` gives you `id, score, name, …`; `/search`
calls its ID column `short_form`. They still have to be comparable.

Every VFB query result carries a `headers` map that **declares** which column holds the row's term
ID: the one whose `type` is `"selection_id"` (it is the column the website uses for "add to search").
`/combine` reads that declaration rather than guessing a column name, which is what lets a `/search`
result (`short_form`) intersect correctly with a `/run_query` result (`id`).

Two consequences worth knowing:

**Duplicate IDs are folded.** Some queries return several rows per term — `DownstreamClassConnectivity`
on a class with subclasses runs once per subclass and concatenates, so one Kenyon cell query returns
8,935 rows covering 894 distinct terms. Set sizes count *terms*, not rows; counting rows would
overstate every set by an order of magnitude. The rows themselves are merged, not discarded
([§6](#6-how-columns-are-merged-nothing-is-dropped)).

**Rows with no ID are reported, not silently dropped.** If a result has rows whose ID column is
empty, the count appears in `warnings`.

There is currently one query type whose schema omits the declaration —
`NeuronInputsTo` — and it still carries a conventional `id` column, which is used as the fallback. If
a table has neither a declared ID column nor a conventionally-named one, the endpoint refuses the
operand with a message naming the columns it saw. It does not guess from the values: a column full of
`FBbt_` strings might be the row's identity or might be its parent class, and picking wrong gives a
confident wrong answer rather than an error.

---

## 6. How columns are merged (nothing is dropped)

A set operation over query results should return the **evidence**, not send you back to re-fetch it.
So the output is not a list of IDs; it is a merged table.

The rule: take the union of every operand's columns. Where the sources that have a column agree on
its value, emit it once under its own name. Where they disagree, emit the first value (in expression
order) under the plain name **and** every distinct value under `column__operand`, so the disagreement
is visible and nothing is lost.

Two columns are added by the merge itself:

| Column | Meaning |
|---|---|
| `found_in` | which of your operands returned this term |
| `found_in_count` | how many of them did |

`found_in` is the interesting one after an `OR`: it turns "the union" into "here is which query each
row came from", which is usually the actual question. Rows are ordered by `found_in_count`
descending, then by label — most-corroborated first, and stable between calls, which matters if you
diff results across data releases.

The `headers` map of the response describes every column, including the merged ones: a `label__b`
column inherits the *type* of the `label` column it came from (so a client that renders by declared
type keeps rendering it correctly) and gains a `from_query` field naming its source.

Worked example — `calyx AND lh`, where one query carries `via` and the other carries `nt`:

```json
{
  "found_in": ["calyx", "lh"], "found_in_count": 2,
  "id": "VFB_00100000", "label": "DA1 lPN (FlyEM-HB:1734350908)",
  "via": "calyx", "nt": "acetylcholine"
}
```

Neither `via` nor `nt` existed in both tables; both survive.

---

## 7. Reading the response

```json
{
  "expression": "calyx AND lh",
  "as_read": "(calyx AND lh)",
  "plain_english": "only the things found by BOTH NeuronsPartHere of FBbt_00007401 and NeuronsPartHere of FBbt_00007053",
  "steps": [
    {"operation": "AND",
     "description": "only the things found by BOTH …",
     "input_counts": [567, 314],
     "result_count": 91}
  ],
  "headers": { "...": "one entry per column, including found_in" },
  "rows": [ "..." ],
  "count": 91,
  "operands": {
    "calyx": {"query": "NeuronsPartHere:FBbt_00007401", "description": "NeuronsPartHere of FBbt_00007401",
              "id_column": "id", "rows_returned": 567, "distinct_terms": 567,
              "reported_count": 567, "truncated": false}
  },
  "universe": {"source": "operands", "size": 790, "description": "everything found by any of the queries in this expression (790 terms)", "note": "..."},
  "warnings": []
}
```

`steps` is the part to read when a number surprises you. Each entry gives the size of both inputs and
of the result, in evaluation order. `91 of 567 and 314` is a plausible intersection; `91 of 567 and
91` means the right-hand query is a subset of the left and the `AND` told you nothing new; `0 of 567
and 314` means look at [§9](#9-the-traps-and-what-the-endpoint-says-about-them). Steps for complement
operators also carry `universe_size`, and a step that came out empty for a structural reason carries
a `why_empty` explanation.

`operands` is the per-query accounting: how many rows came back, how many distinct terms that was
(the gap is duplicate folding), and whether the server truncated it.

---

## 8. Worked biological examples

Counts were measured live on **2026-07-27**. They move with each data release; they are given so you
can tell "this worked" from "this returned something odd", not as fixed values.

### 8.1 Multi-region arborisation — the bread and butter

**Projection neurons in both the calyx and the lateral horn.** The canonical olfactory-projection
question: PNs that innervate the mushroom body calyx *and* the lateral horn, rather than one or the
other.

```
expr = calyx AND lh
calyx = NeuronsPartHere:FBbt_00007401     # mushroom body calyx
lh    = NeuronsPartHere:FBbt_00007053     # lateral horn
```
→ **91** of 567 ∩ 314.

**Lateral-horn-only PNs** — reaching the LH but avoiding the calyx entirely:

```
expr = [al AND lh] NOT calyx
al    = NeuronsPartHere:FBbt_00003885      # antennal lobe
lh    = NeuronsPartHere:FBbt_00007053
calyx = NeuronsPartHere:FBbt_00007401
```
→ **136**. Note the brackets: without them `al AND lh NOT calyx` happens to give the same answer
here (`AND` and `NOT` bind equally, left to right), but write them anyway — the reader should not
have to know the precedence table.

**Antennal lobe local neurons**, by successive exclusion — in the AL, but projecting to neither of
the two downstream targets:

```
expr = al NOT calyx NOT lh
```
→ **340**. Reads left to right: `((al NOT calyx) NOT lh)`.

### 8.2 Visual system — following a pathway through neuropils

**Transmedullary neurons**: medulla *and* lobula, but not lobula plate.

```
expr = [med AND lo] NOT lop
med = NeuronsPartHere:FBbt_00003748       # medulla        (471)
lo  = NeuronsPartHere:FBbt_00003852       # lobula         (528)
lop = NeuronsPartHere:FBbt_00003885       # lobula plate   (198)
```
→ **101**.

**The T4 motion pathway** is the mirror image — medulla *and* lobula plate, but *not* lobula:

```
expr = [med AND lop] NOT lo
```
→ **13**. The asymmetry between 101 and 13 is the anatomy: many cell types bridge medulla→lobula,
few bridge medulla→lobula plate without also touching the lobula.

### 8.3 Central complex — compass and steering circuits

**EB and PB but not FB** — the classic compass-neuron signature (E-PG and friends):

```
expr = [eb AND pb] NOT fb
eb = NeuronsPartHere:FBbt_00003637        # ellipsoid body   (103)
pb = NeuronsPartHere:FBbt_00003668        # protocerebral bridge (193)
fb = NeuronsPartHere:FBbt_00003679        # fan-shaped body  (229)
```
→ **63**.

**PFN-type neurons** — FB and NO, excluding EB:

```
expr = [fb AND no] NOT eb
no = NeuronsPartHere:FBbt_00003680        # noduli
```
→ **59**.

### 8.4 Neuromodulation — where bracketing earns its keep

**Dopaminergic or octopaminergic neurons of the mushroom body.** The `OR` must be bracketed or the
`AND` binds first and the answer becomes "MB dopaminergic neurons plus every octopaminergic neuron in
the brain":

```
expr = mb AND [dan OR oct]
mb  = NeuronsPartHere:FBbt_00005801       # mushroom body      (129)
dan = search:dopaminergic neuron          # (64)
oct = search:octopaminergic neuron        # (22)
```
→ **17**.

### 8.5 Connectivity set algebra

**Recurrent calyx neurons** — both presynaptic and postsynaptic in the same region:

```
expr = pre AND post
pre  = NeuronsPresynapticHere:FBbt_00007401   # (188)
post = NeuronsPostsynapticHere:FBbt_00007401  # (148)
```
→ **33** recurrent; `pre NOT post` → **155** output-only; `post NOT pre` → **115** input-only. The
three numbers together are the calyx's input/output/recurrent decomposition, and no single query
gives them.

**What DNa02 targets that DNp09 does not** — the descending-neuron comparison that motivated the
endpoint:

```
expr = a NOT b
a = DownstreamClassConnectivity:<DNa02>
b = DownstreamClassConnectivity:<DNp09>
```
→ **613** unique to DNa02, with `a AND b` → **297** shared and `a XOR b` → **952** the two differ
by. `XOR` is the right operator for "how do these two cell types differ" — it is symmetric, so you do
not have to run it twice.

**Kenyon cell → MBON connectivity** as an intersection of a downstream set with a type:

```
expr = kc_out AND mbon
```
→ **38**; the DAN→KC direction → **35**.

### 8.6 Anatomy crossed with genetics and expression

**Split-GAL4 lines labelling both T4 and T5.** Small numbers, and that is the useful part — a driver
that hits both is rare enough to be worth naming.

```
expr = t4 AND t5
```
→ **4** shared, `t4 NOT t5` → **2** T4-specific.

**Driver lines with expression in both antennal lobe and ellipsoid body**:

```
expr = al_lines AND eb_lines          # 4377 ∩ 352
```
→ **127**.

**Kenyon cell transcriptomic clusters crossed with neurotransmitter markers.** This one is
instructive because two of the four answers are zero, and both zeroes are real:

```
expr = kc AND marker
kc = <Kenyon cell clusters>            # 72
```

| marker | result |
|---|---|
| ChAT (975) | **64** |
| *fru* | **72** |
| Gad1 | **0** |
| *dsx* | **0** |

Kenyon cells are cholinergic, so ChAT and *fru* hitting and Gad1 and *dsx* missing is the expected
biology — but you only know that because the operand counts show Gad1 returned plenty of rows on its
own. An empty result with a large right-hand side is a finding; an empty result with an empty
right-hand side is a broken query, and the `steps` block is what distinguishes them.

**α'β' versus αβ Kenyon cell marker genes** — genes in one profile and not the other:

```
expr = apbp NOT ab                     # 1773 NOT 1557
```
→ **340**.

### 8.7 Dataset coverage — an honest use for an empty answer

**Which T4 neurons does the Zhao2023 dataset cover?**

```
expr = t4 AND zhao
```
→ **350**. The same expression with T5 → **0**. That zero is a genuine coverage gap in the dataset,
not a mistake, and it is exactly the kind of thing worth checking before building an analysis on a
dataset you have not used before.

### 8.8 Descending neurons

**Descending neurons with arbours in the ventral nerve cord**:

```
expr = dn AND vnc                      # 822 ∩ 4495
```
→ **504**.

### 8.9 Development and lineage

**Lobula lineages that do not contribute to the medulla**:

```
expr = lo_lin NOT med_lin              # 32 NOT 7
```
→ **25**.

---

## 9. The traps, and what the endpoint says about them

Five ways a combination is silently wrong. Each one produces a `warnings` entry rather than a
plausible number.

**1. A truncated operand.** Large queries are capped at 25,000 rows (`VFBQUERY_RESULT_ROW_CAP`).
`DatasetImages` on a big dataset reports `count: 60002` and returns 25,000 of them. Set algebra over a
truncated set is confidently wrong in both directions: an `AND` loses members that were cut off, and
a `NOT` keeps members it should have removed. The warning names the operand and both numbers.
`require_complete=true` turns it into a `409` instead — use that when the number is going in a paper.

**2. Two sides that can never intersect.** VFB IDs come in namespaces: `FBbt_` is an anatomy class
(a cell type or region), `VFB_` is an individual (one imaged or reconstructed specimen), `VFBexp_` is
an expression pattern, `FBlc_` a dataset or transcriptomic cluster, `FBgn_` a gene. An `AND` between
two different namespaces is empty *by construction*, not by biology. The endpoint diagnoses this on
the step that went empty and names the kinds in words ("individual on the left, anatomy class on the
right"), because the user who made the mistake is precisely the one who does not yet read ID prefixes
fluently. The fix is to compare like with like: use the class-level query on both sides, or map
individuals up to their types first.

**3. Cross-dataset intersection at the individual level.** A subtler version of the same thing. Ask
for individual images of `T4c_R` and you get 1,766 distinct `VFB_` IDs spread across five datasets —
every dataset reconstructs *its own* copies of the same cell type. Intersecting individuals from two
datasets is therefore always ≈0, and it is not telling you the cell types differ. Combine at the
class level, or use one dataset on both sides.

**4. A complement against the implicit universe.** Covered in [§4](#4-what-everything-means-the-universe):
`NOR` is always empty, `NAND` collapses to `XOR`, `XNOR` collapses to `AND`, and a bare `NOT a` on a
single operand is empty. All four are warned about, with `universe=` named as the fix.

**5. An operand that returned nothing.** Anything `AND`-ed with an empty set is empty and anything
`NOT`-ed by it is unchanged, so one failed query quietly determines the whole answer. Warned, with
the advice to check that query on its own first. (The same applies to a name you defined and never
used: it is listed in `unused_operands`, warned about, and — deliberately — *not run*, since an
unused operand would otherwise widen the implicit universe and change what `NOT` means.)

A combination that comes back empty with no warnings at all gets a closing note pointing at the step
counts, because "empty" is the one result that looks identical whether it is a discovery or a
mistake.

---

## 10. Limits

| Limit | Default | Why |
|---|---|---|
| Operands per expression | 12 (`VFBQUERY_MAX_COMBINE_OPERANDS`) | Each operand is a separate Neo4j or Solr query, issued concurrently. One request fanning out to fifty is a denial of service against everyone else. Twelve is well past any hand-written expression; the documented examples top out at four. |
| Expression length | 2000 characters | Roughly 150 operators. Guards the tokeniser. |
| Rows per operand | 25,000 (`VFBQUERY_RESULT_ROW_CAP`) | Shared with every other endpoint; exceeded means truncation, which is warned about. |

Operands are run concurrently under the same cache, request-coalescer and queue-depth backpressure as
every other endpoint, and an operand cache key is byte-identical to the one a direct `/run_query`
would use. A full queue sheds the whole combination as a single `503` with `Retry-After`, rather than
half-answering it.

---

## 11. From Python

```python
from vfbquery_client import VfbClient
vfb = VfbClient()

df = vfb.combine("calyx AND lh", {
    "calyx": "NeuronsPartHere:FBbt_00007401",
    "lh":    "NeuronsPartHere:FBbt_00007053",
})

df.attrs["as_read"]        # '(calyx AND lh)'  — check this
df.attrs["plain_english"]  # the sentence version
df.attrs["steps"]          # [{'operation': 'AND', 'input_counts': [567, 314], 'result_count': 91}]
df.attrs["count"]          # full size, which differs from len(df) if you passed limit=
```

The frame is an ordinary `DataFrame` — every column from every operand, plus `found_in` and
`found_in_count` — so anything downstream that understands a DataFrame understands this. The
explanation rides along in `.attrs` rather than in extra columns.

Operands accept a string, a `(query_type, id)` pair, or **any iterable of IDs** — a list, a set, or a
DataFrame column:

```python
vfb.combine("a NOT b", {"a": ("NeuronsPartHere", "FBbt_00007401"),
                        "b": previous_result["id"]})
```

`vfb.explain_combination(expr, operands)` returns the reading without running anything. Server
warnings arrive as Python `UserWarning`s; a `4xx` (including the `409` from `require_complete=True`)
raises `VfbError` carrying the server's own message.

---

## 12. Expressions bigger than the operand limit

Twelve operands is a cost limit, not a mathematical one. To go further, run the expression in stages
and feed each result back in as an `ids:` operand:

```python
stage1 = vfb.combine("a AND b AND c", {...})
stage2 = vfb.combine("prev NOT d", {"prev": stage1["id"], "d": "..."})
```

`ids:` costs no query at all, so a staged expression is not slower than a monolithic one would have
been — and it has the side benefit that every intermediate result is inspectable, which for anything
you intend to publish is worth doing anyway.

---

## Implementation notes

`src/vfbquery/combine.py` is deliberately free of network and aiohttp imports: the parser, the
algebra, the explanations and the merge are pure functions over dicts. That is what lets
`tests/test_combine.py` cover the grammar and the traps in under a second without a server or a Solr
index, and it means a client can explain an expression locally before sending it.
`tests/test_combine_endpoint.py` covers the rest: query-string parsing, the reserved-parameter split,
the refusals, and — the expensive one — that an operand hits exactly the cache key a direct
`/run_query` would.
