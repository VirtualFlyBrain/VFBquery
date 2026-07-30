"""Set algebra over the results of any two or more VFB queries.

`/combine` answers questions no single VFB query can: "which neurons are in the
medulla *and* the lobula *but not* the lobula plate", "which dopaminergic types
innervate the gamma lobe", "what does DNa02 target that DNp09 does not". Each
operand is an ordinary query; this module is the part that combines them.

Four things in here are load-bearing and none of them are obvious, so they are
explained where they are implemented rather than here:

1.  **What counts as "the same row" across two different queries.** Different
    query types return different tables — `SubclassesOf` gives you `id, label,
    tags, template, technique, thumbnail`, `SimilarMorphologyTo` gives you
    `id, score, name, ...`. They are compared on the row's term ID, and the
    query schema *declares* which column that is (`headers[col].type ==
    "selection_id"`). See `id_column`.

2.  **The universe.** `NOT`, `NAND`, `NOR` and `XNOR` are complements, and a
    complement is meaningless without a universe to complement against. VFB has
    ~750,000 terms; "everything that is not a Kenyon cell" is not an answer
    anybody wants. See `UNIVERSE_NOTE` and `Universe`.

3.  **Losing rows silently.** An operand whose `count` exceeds the rows actually
    returned has been truncated by the server, and set algebra over a truncated
    set produces a confident wrong answer. See `OperandResult.truncated`.

4.  **Losing columns silently.** Merging a row that appeared in three operands
    must not throw away two thirds of the data. See `merge_rows`.

The module is deliberately free of network and aiohttp imports: everything here
is pure functions over dicts, so the parser, the algebra and the explanations
are testable without a server or a Solr index.
"""
from __future__ import annotations

import re
from collections import OrderedDict


# ---------------------------------------------------------------------------
# 1. Operators
#
# The alias tables exist because the audience is biologists, not logicians. A
# researcher writing "neurons in the medulla BUT NOT the lobula plate" should
# not have to discover that the endpoint spells it `MINUS`. Every alias maps to
# one of seven canonical operations, and the canonical name is what appears in
# the explanation, so the response always teaches the standard vocabulary even
# when the request did not use it.
# ---------------------------------------------------------------------------

#: Canonical operator -> the plain-English template used in explanations.
#: `{l}` and `{r}` are filled with the descriptions of the two sides.
PLAIN_ENGLISH = {
    "OR":   "anything found by {l}, together with anything found by {r} "
            "(everything from either side, listed once)",
    "AND":  "only the things found by BOTH {l} and {r}",
    "NOT":  "the things found by {l}, after removing anything also found by {r}",
    "XOR":  "the things found by {l} or by {r}, but NOT by both — "
            "i.e. what makes the two sides differ",
    "NAND": "everything except the things found by both {l} and {r}",
    "NOR":  "everything found by neither {l} nor {r}",
    "XNOR": "the things the two sides agree on — found by both {l} and {r}, "
            "or by neither",
}

#: Which operators need a universe to be meaningful. See `Universe`.
COMPLEMENT_OPS = frozenset({"NAND", "NOR", "XNOR", "COMPLEMENT"})

#: Multi-word aliases, matched before single tokens (longest first) so that
#: "but not" does not tokenise as `BUT` followed by `NOT`. Order matters.
PHRASE_ALIASES = [
    ("either but not both", "XOR"),
    ("only one of",         "XOR"),
    ("in exactly one of",   "XOR"),
    ("but not",             "NOT"),
    # Deliberately NOT here: "and not". It reads as binary NOT in English, and
    # collapsing it to one is *usually* harmless — `a AND NOT b` and `a NOT b`
    # agree whenever a is inside the universe, which it always is under the
    # implicit one. But with an explicit `universe=` narrower than a, they
    # differ: the first drops members of a that the universe excludes, the
    # second keeps them. Someone typing `AND NOT` has written two operators and
    # is entitled to both, so it is parsed literally as AND followed by unary
    # NOT. The English readings are covered by "but not", minus, except,
    # without and excluding, none of which is ambiguous.
    ("not both",            "NAND"),
    ("same in both",        "XNOR"),
    ("in both or neither",  "XNOR"),
    ("present in both",     "AND"),
    ("found in both",       "AND"),
    ("in either",           "OR"),
    # MUST STAY LAST. `tokenize` substitutes these in list order, so a bare
    # "in both" placed any earlier would eat the tail of "same in both",
    # "in both or neither", "present in both" and "found in both", leaving
    # unparseable fragments ("same AND", "present AND") in their place. Kept
    # because it is the phrasing the /combine docs advertise and the one a
    # biologist reaches for first: "the neurons in both calyx and lateral horn".
    ("in both",             "AND"),
]

#: Single-token aliases.
WORD_ALIASES = {
    "or": "OR", "union": "OR", "any": "OR", "either": "OR", "plus": "OR",
    "and": "AND", "intersect": "AND", "intersection": "AND", "both": "AND",
    "not": "NOT", "minus": "NOT", "except": "NOT", "without": "NOT",
    "excluding": "NOT", "andnot": "NOT",
    "xor": "XOR", "difference": "XOR",
    "nand": "NAND",
    "nor": "NOR", "neither": "NOR",
    "xnor": "XNOR", "agree": "XNOR",
}

#: Symbolic aliases. `-` is set difference, not unary negation: `a - b` is what
#: a spreadsheet user expects and `NOT a` covers the unary case.
SYMBOL_ALIASES = {
    "|": "OR", "+": "OR", "∪": "OR", "||": "OR",
    "&": "AND", "∩": "AND", "&&": "AND", "*": "AND",
    "-": "NOT", "\\": "NOT", "−": "NOT",
    "^": "XOR", "⊕": "XOR",
}

#: Binding strength, loosest first. Everything is left-associative, so
#: `a NOT b NOT c` is `(a NOT b) NOT c` — successive exclusions, which is what
#: "in the antennal lobe, but not the calyx, and not the lateral horn" means.
#:
#: `NOT` (as a binary operator) sits with `AND` because set difference is an
#: intersection with a complement, and putting it any looser would make
#: `a AND b NOT c` mean `a AND (b NOT c)` — which is the same answer here, but
#: stops being the same answer as soon as `OR` is involved.
PRECEDENCE = [
    ("OR", "NOR"),
    ("XOR", "XNOR"),
    ("AND", "NAND", "NOT"),
]


class CombineError(ValueError):
    """A user-facing problem with the expression or the operands.

    Distinct from an internal failure: every raise site here produces a message
    that a workshop attendee can act on without reading this file.
    """


# ---------------------------------------------------------------------------
# 2. Tokeniser
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def tokenize(expr):
    """Expression text -> a list of ``('name'|'op'|'(' |')', value)`` tuples.

    Phrase aliases are substituted first, on the lower-cased text, so that
    "but not" becomes a single NOT before word-splitting can turn it into two
    tokens. The substitution is done on word boundaries to keep a phrase from
    matching inside an operand name.
    """
    if expr is None or not expr.strip():
        raise CombineError(
            "No expression given. Provide `expr`, e.g. expr=(a AND b) NOT c"
        )

    text = expr
    for phrase, canonical in PHRASE_ALIASES:
        text = re.sub(r"\b" + phrase.replace(" ", r"\s+") + r"\b", f" {canonical} ",
                      text, flags=re.IGNORECASE)

    tokens = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in "([{":
            tokens.append(("(", ch))
            i += 1
            continue
        if ch in ")]}":
            tokens.append((")", ch))
            i += 1
            continue

        # Two-character symbols before one-character ones.
        pair = text[i:i + 2]
        if pair in SYMBOL_ALIASES:
            tokens.append(("op", SYMBOL_ALIASES[pair]))
            i += 2
            continue
        if ch in SYMBOL_ALIASES:
            tokens.append(("op", SYMBOL_ALIASES[ch]))
            i += 1
            continue

        match = _NAME_RE.match(text, i)
        if not match:
            raise CombineError(
                f"Could not understand {text[i]!r} at position {i} of the "
                f"expression. Operand names are letters, digits and "
                f"underscores; operators are AND, OR, NOT, XOR, NAND, NOR, "
                f"XNOR (or & | - ^); grouping uses parentheses."
            )
        word = match.group(0)
        lowered = word.lower()
        if lowered in WORD_ALIASES:
            tokens.append(("op", WORD_ALIASES[lowered]))
        elif lowered in {"nand", "nor", "xnor"}:      # defensive; covered above
            tokens.append(("op", lowered.upper()))
        else:
            tokens.append(("name", word))
        i = match.end()

    return tokens


# ---------------------------------------------------------------------------
# 3. Parser
#
# Precedence climbing with parentheses. The one subtlety is that `NOT` is both
# a binary operator (`a NOT b`, set difference) and a unary one (`NOT a`,
# complement). They are told apart by position, which is unambiguous: in a
# well-formed expression an operator token appearing where an *operand* is
# expected can only be unary, and one appearing where an *operator* is expected
# can only be binary. That is also how people read it, so nobody has to be told.
# ---------------------------------------------------------------------------

class Operand:
    __slots__ = ("name",)
    kind = "operand"

    def __init__(self, name):
        self.name = name

    def names(self):
        yield self.name


class Complement:
    """Unary ``NOT x`` — everything in the universe that is not in x."""
    __slots__ = ("operand",)
    kind = "complement"

    def __init__(self, operand):
        self.operand = operand

    def names(self):
        yield from self.operand.names()


class BinOp:
    __slots__ = ("op", "left", "right")
    kind = "binop"

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def names(self):
        yield from self.left.names()
        yield from self.right.names()


def parse(expr, known_names=None):
    """Parse `expr` into a tree. Raises `CombineError` with a usable message."""
    tokens = tokenize(expr)
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else (None, None)

    def advance():
        token = peek()
        pos[0] += 1
        return token

    def parse_primary():
        kind, value = peek()
        if kind == "(":
            advance()
            node = parse_level(0)
            kind2, _ = peek()
            if kind2 != ")":
                raise CombineError(
                    "Unbalanced brackets: an opening bracket was never closed. "
                    "Check that every '(' has a matching ')'."
                )
            advance()
            return node
        if kind == "op":
            # Operator where an operand was expected -> unary. Only NOT (and its
            # aliases, which all normalise to NOT) is meaningful here.
            if value != "NOT":
                raise CombineError(
                    f"'{value}' needs something on both sides of it, but there "
                    f"is nothing to its left. Did you mean 'NOT' (which can "
                    f"stand in front of a single operand), or is an operand "
                    f"missing?"
                )
            advance()
            return Complement(parse_primary())
        if kind == "name":
            advance()
            if known_names is not None and value not in known_names:
                known = ", ".join(sorted(known_names)) or "(none defined)"
                raise CombineError(
                    f"Unknown operand '{value}' in the expression. "
                    f"Defined operands: {known}. Define it by passing "
                    f"{value}=<query> alongside `expr`."
                )
            return Operand(value)
        if kind == ")":
            raise CombineError(
                "Unbalanced brackets: a ')' appears with no matching '('."
            )
        raise CombineError(
            "The expression ends where an operand was expected — a trailing "
            "operator, e.g. 'a AND'. Every operator needs something after it."
        )

    def parse_level(level):
        if level >= len(PRECEDENCE):
            return parse_primary()
        node = parse_level(level + 1)
        while True:
            kind, value = peek()
            if kind == "op" and value in PRECEDENCE[level]:
                advance()
                right = parse_level(level + 1)
                node = BinOp(value, node, right)
            else:
                return node

    tree = parse_level(0)
    kind, value = peek()
    if kind is not None:
        raise CombineError(
            f"Unexpected {value!r} after the end of the expression. This is "
            f"usually a missing operator (e.g. 'a b' should be 'a AND b') or "
            f"one bracket too many."
        )
    return tree


# ---------------------------------------------------------------------------
# 4. Identity — which column is "the row's term"
# ---------------------------------------------------------------------------

#: Column names accepted as the identity column when the schema does not
#: declare one, in preference order. `NeuronInputsTo` is the one query type
#: observed without a `selection_id` header, and it does have a plain `id`.
ID_COLUMN_FALLBACKS = ("id", "short_form", "VFB_id", "vfb_id")


def id_column(headers, rows=()):
    """Return the name of the column holding the row's term ID.

    The query schemas declare this: every result carries a `headers` map, and
    the identity column is the one whose declared type is `selection_id` — the
    same field the website uses to know what a click selected. That is a fact
    about the data rather than a guess, which matters because the alternative
    (assuming `id`) silently picks the wrong column the first time a query type
    names it something else.

    Falls back to a small list of conventional names, then fails loudly. It
    never guesses from the *values*: an ID-shaped string in a `parent` or
    `template` column would combine two queries on the wrong axis entirely and
    return a plausible, wrong answer.
    """
    if isinstance(headers, dict):
        for column, meta in headers.items():
            if isinstance(meta, dict) and meta.get("type") == "selection_id":
                return column
    candidates = set(headers or ())
    if not candidates and rows:
        candidates = set(rows[0])
    for name in ID_COLUMN_FALLBACKS:
        if name in candidates:
            return name
    raise CombineError(
        "Cannot tell which column identifies the term in this result: no "
        "column is declared as `selection_id` and none is named "
        + ", ".join(ID_COLUMN_FALLBACKS)
        + ". Columns present: " + (", ".join(sorted(candidates)) or "(none)")
    )


#: ID prefix -> what kind of thing it is. Used only to explain empty results;
#: nothing depends on it for correctness.
NAMESPACES = [
    ("VFBexp_", "expression pattern"),
    ("VFBc_",   "channel"),
    ("VFB_",    "individual (a single imaged or reconstructed specimen)"),
    ("FBbt_",   "anatomy class (a cell type or region)"),
    ("FBlc_",   "dataset / transcriptomic cluster"),
    ("FBgn_",   "gene"),
    ("FBal_",   "allele"),
    ("FBti_",   "transposon insertion"),
    ("FBtp_",   "transgenic construct"),
    ("FBdv_",   "developmental stage"),
    ("FBcv_",   "controlled vocabulary term"),
    ("GO_",     "GO term"),
]


def namespace_of(identifier):
    """Human name for the kind of thing an ID refers to, or None."""
    if not isinstance(identifier, str):
        return None
    for prefix, description in NAMESPACES:
        if identifier.startswith(prefix):
            return description
    return None


def namespaces_in(ids, sample=200):
    """The distinct namespaces present in a set of IDs."""
    found = OrderedDict()
    for count, identifier in enumerate(ids):
        if count >= sample:
            break
        name = namespace_of(identifier)
        if name:
            found[name] = None
    return list(found)


# ---------------------------------------------------------------------------
# 5. Operand results
# ---------------------------------------------------------------------------

class OperandResult:
    """One query's rows, indexed by term ID and de-duplicated.

    Two properties of the upstream data make this more than a dict comprehension:

    *Duplicate IDs.* `DownstreamClassConnectivity` on a class with subclasses
    runs once per subclass and concatenates, so a Kenyon cell query returns
    8,935 rows covering 894 distinct terms. Counting rows instead of terms would
    overstate every set size by an order of magnitude, so rows are folded per ID
    — losslessly, see `merge_rows`.

    *Truncation.* The result carries a `count` that is the true size of the
    answer, and a `rows` list that the server may have capped (a dataset image
    query has been observed reporting `count: 60002` while returning 25,000
    rows). Set algebra over a truncated operand is not approximately right, it
    is confidently wrong: an intersection silently loses members and a
    difference silently gains them. It is recorded here and refused or warned
    about upstream — never ignored.
    """

    def __init__(self, name, payload, spec=None, description=None):
        self.name = name
        self.spec = spec
        self.description = description or name
        payload = payload or {}
        self.headers = payload.get("headers") or {}
        rows = payload.get("rows")
        if rows is None:
            rows = payload.get("connections")
        if rows is None and isinstance(payload.get("results"), list):
            rows = payload["results"]
        rows = rows or []

        try:
            self.id_column = id_column(self.headers, rows)
        except CombineError:
            if rows:
                raise
            # A query that legitimately found nothing must not fail the whole
            # expression. There is no axis to get wrong when there are no rows
            # to place on it, and an empty operand is a perfectly ordinary
            # thing to intersect with — "no Kenyon cells in this dataset" is an
            # answer, not an error.
            self.id_column = None
        self.reported_count = payload.get("count")
        self.rows_returned = len(rows)

        by_id = OrderedDict()
        skipped = 0
        for row in rows:
            identifier = row.get(self.id_column)
            if not identifier:
                skipped += 1
                continue
            by_id.setdefault(identifier, []).append(row)
        self.by_id = by_id
        self.rows_without_id = skipped

    @property
    def ids(self):
        return set(self.by_id)

    @property
    def duplicate_rows(self):
        """Rows folded away because several described the same term."""
        return self.rows_returned - len(self.by_id) - self.rows_without_id

    @property
    def truncated(self):
        """True when the server returned fewer rows than the answer contains.

        Compared against distinct IDs as well as raw rows: a query that reports
        894 and returns 8,935 rows for 894 terms is complete, not truncated.
        """
        if not isinstance(self.reported_count, int):
            return False
        return self.reported_count > max(self.rows_returned, len(self.by_id))


# ---------------------------------------------------------------------------
# 6. The universe
# ---------------------------------------------------------------------------

UNIVERSE_NOTE = (
    "A complement ('NOT a', NAND, NOR, XNOR) means 'everything except…', so it "
    "only has an answer once 'everything' is defined. VFB holds around 750,000 "
    "terms and returning most of them is never the intended answer, so by "
    "default 'everything' means everything your own queries found — the union "
    "of all the operands in this expression. Pass `universe=<query>` to widen "
    "or narrow that deliberately."
)


class Universe:
    """The set a complement is taken against, plus why it is that set."""

    def __init__(self, ids, source, description):
        self.ids = ids
        self.source = source              # "operands" | "explicit"
        self.description = description


def implicit_universe(operands):
    ids = set()
    for operand in operands.values():
        ids |= operand.ids
    return Universe(
        ids, "operands",
        "everything found by any of the queries in this expression "
        f"({len(ids)} terms)",
    )


#: Warnings raised when a complement is evaluated against the implicit
#: universe. Each of these is a *guaranteed* algebraic consequence of setting
#: the universe to the union of the operands, not a heuristic — which is why
#: they are worth saying out loud rather than leaving the user to discover an
#: empty result and assume the biology was the reason.
IMPLICIT_UNIVERSE_TRAPS = {
    "NOR": (
        "`NOR` with the default universe always returns nothing. 'Found by "
        "neither side' is empty by construction when 'everything' is defined "
        "as 'what the two sides found'. If you meant 'terms in some wider set "
        "that neither query found', pass `universe=<query>` naming that wider "
        "set — e.g. universe=SubclassesOf:FBbt_00005106 for 'neurons'."
    ),
    "NAND": (
        "`NAND` with the default universe gives exactly the same answer as "
        "`XOR` (everything except the overlap, where 'everything' is the two "
        "sides combined). That is usually what was wanted, but if you meant "
        "'anything at all except the overlap', set `universe=` explicitly."
    ),
    "XNOR": (
        "`XNOR` with the default universe gives exactly the same answer as "
        "`AND` (the 'or by neither' half is empty by construction). Set "
        "`universe=` explicitly if you meant something wider."
    ),
    "COMPLEMENT": (
        "`NOT a` on its own means 'everything the *other* queries found that "
        "a did not'. With only one operand in the expression that is always "
        "empty. Set `universe=` to say what it should be complemented against."
    ),
}


# ---------------------------------------------------------------------------
# 7. Evaluation
# ---------------------------------------------------------------------------

def evaluate(node, operands, universe, steps=None, warnings=None):
    """Evaluate the tree to a set of IDs, appending a trace to `steps`."""
    if node.kind == "operand":
        return operands[node.name].ids

    if node.kind == "complement":
        inner = evaluate(node.operand, operands, universe, steps, warnings)
        result = universe.ids - inner
        _note_complement("COMPLEMENT", universe, warnings)
        if steps is not None:
            steps.append({
                "operation": "NOT (complement)",
                "description": f"everything in the universe except "
                               f"{describe(node.operand, operands)}",
                "input_counts": [len(inner)],
                "universe_size": len(universe.ids),
                "result_count": len(result),
            })
        return result

    left = evaluate(node.left, operands, universe, steps, warnings)
    right = evaluate(node.right, operands, universe, steps, warnings)
    op = node.op

    if op == "OR":
        result = left | right
    elif op == "AND":
        result = left & right
    elif op == "NOT":
        result = left - right
    elif op == "XOR":
        result = left ^ right
    elif op == "NAND":
        result = universe.ids - (left & right)
        _note_complement("NAND", universe, warnings)
    elif op == "NOR":
        result = universe.ids - (left | right)
        _note_complement("NOR", universe, warnings)
    elif op == "XNOR":
        result = universe.ids - (left ^ right)
        _note_complement("XNOR", universe, warnings)
    else:                                              # pragma: no cover
        raise CombineError(f"Unsupported operator {op!r}")

    if steps is not None:
        step = {
            "operation": op,
            "description": PLAIN_ENGLISH[op].format(
                l=describe(node.left, operands), r=describe(node.right, operands)
            ),
            "input_counts": [len(left), len(right)],
            "result_count": len(result),
        }
        if op in COMPLEMENT_OPS:
            step["universe_size"] = len(universe.ids)
        # An empty intersection between two different kinds of thing is the
        # single most common surprise, and it is never biological: individuals
        # (VFB_) and classes (FBbt_) simply cannot be equal. Diagnosed here,
        # where both sides are in hand.
        if op in {"AND", "XNOR"} and not result and left and right:
            left_ns, right_ns = namespaces_in(left), namespaces_in(right)
            if left_ns and right_ns and not (set(left_ns) & set(right_ns)):
                step["why_empty"] = (
                    "The two sides return different kinds of thing — "
                    f"{' / '.join(left_ns)} on the left, "
                    f"{' / '.join(right_ns)} on the right — so no ID can appear "
                    "in both. This is a structural mismatch, not a biological "
                    "finding. Compare like with like: e.g. use the class-level "
                    "query on both sides, or map individuals up to their types "
                    "first."
                )
                if warnings is not None:
                    warnings.append(step["why_empty"])
        steps.append(step)
    return result


def _note_complement(op, universe, warnings):
    if warnings is None or universe.source != "operands":
        return
    message = IMPLICIT_UNIVERSE_TRAPS.get(op)
    if message and message not in warnings:
        warnings.append(message)


def describe(node, operands):
    """A short phrase naming a subtree, for use inside explanations."""
    if node.kind == "operand":
        operand = operands.get(node.name)
        if operand is not None and operand.description != node.name:
            return f"{node.name} ({operand.description})"
        return node.name
    if node.kind == "complement":
        return f"everything except {describe(node.operand, operands)}"
    return f"({describe(node.left, operands)} {node.op} "\
           f"{describe(node.right, operands)})"


def to_expression(node):
    """Render the parsed tree back to canonical, fully-bracketed text.

    Echoing this back is how a user checks that the brackets were read the way
    they meant them — `a OR b AND c` is not `(a OR b) AND c`, and the cheapest
    way to prevent that misunderstanding is to show the grouping that was used.
    """
    if node.kind == "operand":
        return node.name
    if node.kind == "complement":
        return f"NOT {to_expression(node.operand)}"
    return f"({to_expression(node.left)} {node.op} {to_expression(node.right)})"


def plain_english(node, operands):
    """The whole expression as one sentence a non-logician can check."""
    if node.kind == "operand":
        return describe(node, operands)
    if node.kind == "complement":
        return (f"everything found by the other queries, except "
                f"{describe(node.operand, operands)}")
    return PLAIN_ENGLISH[node.op].format(
        l=plain_english(node.left, operands) if node.left.kind != "operand"
          else describe(node.left, operands),
        r=plain_english(node.right, operands) if node.right.kind != "operand"
          else describe(node.right, operands),
    )


# ---------------------------------------------------------------------------
# 8. Lossless row merging
# ---------------------------------------------------------------------------

#: Columns added by the combine step itself. Named with a prefix that no query
#: schema uses, so a merged table can always be told from a plain one.
FOUND_IN = "found_in"
FOUND_IN_COUNT = "found_in_count"


def merge_rows(identifier, contributions, operand_order):
    """Fold every row describing one term into a single row, losing nothing.

    `contributions` maps operand name -> the list of rows that operand returned
    for this ID. A term can appear in several operands, and each operand may
    have returned several rows for it, and the tables need not agree: one query
    calls the label column `label` and another calls it `name`; one carries
    `score`, another carries `outputs`/`inputs`.

    The rule is: take the union of all columns. Where every source that has a
    column agrees on its value, emit it once under its own name. Where they
    disagree, emit the first value (in expression order) under the plain name
    *and* every distinct value under `column__operand`, so the disagreement is
    visible and nothing is dropped. A user who does not care sees a normal
    table; a user who does can recover exactly which query said what.

    This is why the endpoint does not simply return IDs: a set operation over
    query results should return the merged evidence, not send the caller back
    to re-fetch it.
    """
    merged = OrderedDict()
    merged[FOUND_IN] = [name for name in operand_order if name in contributions]
    merged[FOUND_IN_COUNT] = len(merged[FOUND_IN])

    # column -> list of (operand, value) in expression order, de-duplicated per
    # operand (an operand's own duplicate rows usually repeat the same values).
    per_column = OrderedDict()
    for name in operand_order:
        for row in contributions.get(name, ()):
            for column, value in row.items():
                bucket = per_column.setdefault(column, [])
                if not any(existing_name == name and existing_value == value
                           for existing_name, existing_value in bucket):
                    bucket.append((name, value))

    for column, pairs in per_column.items():
        distinct = []
        for _, value in pairs:
            if value not in distinct:
                distinct.append(value)
        merged[column] = pairs[0][1]
        if len(distinct) > 1:
            # Disagreement: keep every source's version alongside the primary.
            seen_per_operand = OrderedDict()
            for name, value in pairs:
                seen_per_operand.setdefault(name, [])
                if value not in seen_per_operand[name]:
                    seen_per_operand[name].append(value)
            for name, values in seen_per_operand.items():
                merged[f"{column}__{name}"] = (
                    values[0] if len(values) == 1 else values
                )
    return merged


def merge_headers(operands, operand_order, merged_rows):
    """Header map for the merged table: every operand's headers, plus ours.

    Columns invented by the merge (`label__a`, `label__b`) inherit the type of
    the column they came from, so a client that renders by declared type — the
    website does — keeps rendering them correctly instead of falling back to
    plain text.
    """
    headers = OrderedDict()
    headers[FOUND_IN] = {
        "title": "Found in", "type": "tags", "order": -2,
        "description": "Which of your queries returned this term.",
    }
    headers[FOUND_IN_COUNT] = {
        "title": "In how many", "type": "numeric", "order": -1,
        "description": "How many of your queries returned this term.",
    }
    for name in operand_order:
        operand = operands[name]
        for column, meta in (operand.headers or {}).items():
            if column not in headers and isinstance(meta, dict):
                headers[column] = dict(meta, from_query=name)

    present = set()
    for row in merged_rows:
        present.update(row)
    for column in present:
        if column in headers:
            continue
        base, _, source = column.partition("__")
        template = headers.get(base)
        if isinstance(template, dict):
            headers[column] = dict(
                template, from_query=source,
                title=f"{template.get('title', base)} (from {source})",
            )
        else:
            headers[column] = {"title": column, "type": "text",
                               "from_query": source or None}
    return headers


def build_rows(result_ids, operands, operand_order):
    """Merged output rows for `result_ids`, in a stable, useful order.

    Ordering is by how many operands found the term (descending) and then by
    label, so the terms supported by the most evidence are at the top — which
    is what a researcher scanning an intersection wants, and is stable across
    calls, which matters for anything diffing results between releases.

    There is deliberately no `order_by` argument. Caller-chosen ordering is a
    real request, but it belongs to a column set that only exists *after* the
    merge (`found_in`, `column__operand`), so it needs a name-resolution rule of
    its own rather than a parameter threaded through here. `order_by` is
    reserved in the endpoint's query string so adding it later cannot collide
    with an operand of that name — see `_COMBINE_RESERVED` in `ha_api`.
    """
    rows = []
    for identifier in result_ids:
        contributions = {}
        for name in operand_order:
            operand = operands[name]
            found = operand.by_id.get(identifier)
            if found:
                contributions[name] = found
        if not contributions:
            # In the universe but in no operand: only reachable via an explicit
            # `universe=` whose rows are not part of the expression. Emit the
            # ID rather than dropping it, so a complement never silently
            # shortens its own answer.
            rows.append(OrderedDict([("id", identifier), (FOUND_IN, []),
                                     (FOUND_IN_COUNT, 0)]))
            continue
        rows.append(merge_rows(identifier, contributions, operand_order))

    def sort_key(row):
        label = row.get("label") or row.get("name") or row.get("id") or ""
        return (-row.get(FOUND_IN_COUNT, 0), str(label).lower())

    rows.sort(key=sort_key)
    return rows
