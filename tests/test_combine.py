"""The /combine expression language, its set algebra and its explanations.

Everything here is offline by construction: `vfbquery.combine` imports nothing
but the standard library, which is the whole reason the parser, the precedence
rules, the universe semantics and the lossless merge live there rather than in
the handler. The endpoint half is in `test_combine_endpoint.py`.

The cases are chosen around the four things that make this module more than a
few set operations, each of which was a real observation against the live index
rather than a hypothetical:

* what counts as "the same row" when two queries return different tables,
* what "everything else" means when a user writes NOT,
* what a truncated operand does to an intersection,
* and what happens to the columns nobody thought to keep.
"""
import pytest

from vfbquery import combine as c


# ---------------------------------------------------------------------------
# Parsing: precedence, association and brackets
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("expr,expected", [
    # Precedence, loosest first: OR/NOR, then XOR/XNOR, then AND/NAND/NOT.
    ("a OR b AND c",        "(a OR (b AND c))"),
    ("a AND b OR c",        "((a AND b) OR c)"),
    ("a OR b XOR c",        "(a OR (b XOR c))"),
    ("a XOR b AND c",       "(a XOR (b AND c))"),
    ("a NOT b OR c",        "((a NOT b) OR c)"),
    # Left-associative, so successive exclusions read as successive exclusions.
    # `a NOT b NOT c` grouped the other way would be `a NOT (b NOT c)`, which
    # *adds back* everything in both b and c — the opposite of what someone
    # narrowing a set down means by it.
    ("a NOT b NOT c",       "((a NOT b) NOT c)"),
    ("a OR b OR c",         "((a OR b) OR c)"),
    # Brackets override all of it, which is the point of having them.
    ("(a OR b) AND c",      "((a OR b) AND c)"),
    ("a AND (b OR c)",      "(a AND (b OR c))"),
    ("((a))",               "a"),
    ("(a AND b) NOT (c OR d)", "((a AND b) NOT (c OR d))"),
    # Square and curly brackets too: a user pasting from a paper's methods
    # section should not have to translate them.
    ("[a OR b] AND c",      "((a OR b) AND c)"),
    ("{a OR b} AND c",      "((a OR b) AND c)"),
])
def test_precedence_and_bracketing(expr, expected):
    assert c.to_expression(c.parse(expr)) == expected


@pytest.mark.parametrize("expr,expected", [
    # Words, symbols and phrases all reach the same tree. Someone who knows the
    # notation can write it; someone who does not can say what they mean.
    ("a | b",                   "(a OR b)"),
    ("a & b",                   "(a AND b)"),
    ("a - b",                   "(a NOT b)"),
    ("a ^ b",                   "(a XOR b)"),
    ("a union b",               "(a OR b)"),
    ("a intersect b",           "(a AND b)"),
    ("a minus b",               "(a NOT b)"),
    ("a except b",              "(a NOT b)"),
    ("a but not b",             "(a NOT b)"),
    # "and not" is deliberately absent: it is two operators, not an alias for
    # one. See test_and_not_is_two_operators_rather_than_one.
    ("a found in both b",       "(a AND b)"),
    ("a in both b",             "(a AND b)"),
    ("a either but not both b", "(a XOR b)"),
    ("a in exactly one of b",   "(a XOR b)"),
    # Case is irrelevant; so is extra whitespace.
    ("a or b",                  "(a OR b)"),
    ("  a   OR    b  ",         "(a OR b)"),
])
def test_aliases_reach_the_same_tree(expr, expected):
    assert c.to_expression(c.parse(expr)) == expected


def test_multi_word_aliases_beat_their_own_prefixes():
    """'but not' must not be read as 'not', and 'not both' must not be 'not'.

    The phrase table is applied longest-first before tokenising for exactly
    this reason: read left to right a character at a time, `a but not b` finds
    `not` and produces the right answer by luck, while `a not both b` finds
    `not` and produces NOT where the user asked for NAND.
    """
    assert c.to_expression(c.parse("a not both b")) == "(a NAND b)"
    assert c.to_expression(c.parse("a but not b")) == "(a NOT b)"


def test_bare_in_both_does_not_cannibalise_the_longer_in_both_phrases():
    """`in both` is last in PHRASE_ALIASES, and has to stay last.

    Substitution runs in list order over the whole string, so a bare `in both`
    placed any earlier would consume the tail of every longer phrase that ends
    in those words, leaving fragments like `same AND` and `present AND` that do
    not parse at all. Each of these would have been an error rather than a wrong
    answer, which is the only mercy in it — this test is what stops someone
    tidying the table into alphabetical order.
    """
    assert c.to_expression(c.parse("a in both b")) == "(a AND b)"
    assert c.to_expression(c.parse("a present in both b")) == "(a AND b)"
    assert c.to_expression(c.parse("a found in both b")) == "(a AND b)"
    assert c.to_expression(c.parse("a same in both b")) == "(a XNOR b)"
    assert c.to_expression(c.parse("a in both or neither b")) == "(a XNOR b)"
    # And the guard stated structurally, so a reordering fails here too.
    assert c.PHRASE_ALIASES[-1] == ("in both", "AND")


def test_unary_not_is_told_from_binary_not_by_position():
    """`NOT a` and `a NOT b` are different operators spelled the same way.

    Position decides: an operator token where an operand is expected is the
    unary one. Nothing else can distinguish them, and refusing to accept one
    spelling would mean either "everything except a" or "a minus b" needs a
    notation nobody uses.
    """
    assert c.to_expression(c.parse("NOT a")) == "NOT a"
    assert c.to_expression(c.parse("a NOT b")) == "(a NOT b)"


def test_and_not_is_two_operators_rather_than_one():
    """`a AND NOT b` keeps both operators instead of collapsing to `a NOT b`.

    The two agree under the implicit universe and diverge under an explicit one
    narrower than `a`. Since the user wrote two operators, they get two — see
    the note against PHRASE_ALIASES.
    """
    assert c.to_expression(c.parse("a AND NOT b")) == "(a AND NOT b)"
    assert c.to_expression(c.parse("a but not b")) == "(a NOT b)"


@pytest.mark.parametrize("expr,fragment", [
    ("a OR",        "trailing operator"),
    ("(a OR b",     "never closed"),
    ("a OR b)",     "one bracket too many"),
    ("a b",         "usually a missing operator"),
    ("a OR OR b",   "nothing to its left"),
    ("",            "No expression given"),
])
def test_errors_say_what_to_do(expr, fragment):
    """Every parse error names the mistake in the user's own terms.

    This is not politeness. The audience for this endpoint is a biologist at a
    workshop, and a `CombineError` reading 'unexpected token' costs a raised
    hand; one reading 'this is usually a missing operator' does not.
    """
    with pytest.raises(c.CombineError) as excinfo:
        c.parse(expr)
    assert fragment in str(excinfo.value)


def test_an_unknown_operand_lists_the_ones_that_exist():
    with pytest.raises(c.CombineError) as excinfo:
        c.parse("a AND typo", known_names={"a", "b"})
    message = str(excinfo.value)
    assert "typo" in message
    assert "a" in message and "b" in message


# ---------------------------------------------------------------------------
# Identity: which column is "the same row"
# ---------------------------------------------------------------------------

def test_the_id_column_is_the_one_the_schema_declares():
    """`selection_id` is the contract, not a name or a position.

    Query tables disagree on almost everything — column names, order, how many
    there are — but every one of them declares exactly one column as the thing
    the UI puts in a selection basket, and that is the term the row is *about*.
    Combining on anything else combines the wrong axis.
    """
    headers = {
        "label": {"title": "Name", "type": "markdown"},
        "target": {"title": "Target", "type": "selection_id"},
        "id": {"title": "Internal", "type": "text"},
    }
    assert c.id_column(headers) == "target"


def test_a_missing_declaration_falls_back_but_never_guesses_from_values():
    """With no declared column the fallback is by *name*, and only by name.

    `NeuronInputsTo` is the one query type in the map with no `selection_id`
    header, so the fallback is load-bearing rather than defensive. What it must
    not do is look at values: half the tables carry a `parent` or `template`
    column full of perfectly good VFB ids, and a value-shaped guess would
    cheerfully combine a set of neurons on which brain template they happen to
    be aligned to.
    """
    rows = [{"id": "VFB_1", "parent": "FBbt_2", "label": "x"}]
    assert c.id_column({}, rows) == "id"
    # No declared column, no conventional name, and a column full of real VFB
    # ids sitting right there: it refuses rather than takes it.
    with pytest.raises(c.CombineError) as excinfo:
        c.id_column({}, [{"parent": "FBbt_2", "label": "x"}])
    assert "parent" in str(excinfo.value)


def test_an_empty_result_is_combinable_even_with_no_schema_at_all():
    """Zero rows cannot be placed on the wrong axis, so there is nothing to refuse.

    A query that legitimately finds nothing — "Kenyon cells in this dataset" for
    a dataset that has none — is an ordinary thing to intersect with. Failing
    the whole expression over it would make an empty answer indistinguishable
    from a broken request.
    """
    operand = c.OperandResult("a", {"rows": []})
    assert operand.ids == set()
    assert operand.id_column is None


def test_namespaces_are_named_in_plain_words():
    assert c.namespace_of("FBbt_00007401").startswith("anatomy class")
    assert c.namespace_of("VFB_00101567").startswith("individual")
    assert c.namespace_of("FBgn_0000123") == "gene"
    # Longest prefix wins: VFBexp_ is not a VFB_ individual.
    assert c.namespace_of("VFBexp_FBtp0121686") == "expression pattern"


# ---------------------------------------------------------------------------
# OperandResult: duplicates and truncation
# ---------------------------------------------------------------------------

def _operand(name, ids, count=None, headers=None, rows=None):
    payload = {
        "headers": headers or {"id": {"title": "ID", "type": "selection_id"}},
        "rows": rows if rows is not None else [{"id": i} for i in ids],
    }
    if count is not None:
        payload["count"] = count
    return c.OperandResult(name, payload)


def test_rows_are_folded_per_term_before_anything_is_counted():
    """A class query runs once per subclass and concatenates the results.

    `DownstreamClassConnectivity` on Kenyon cell returns 8,935 rows describing
    894 terms. Counting rows would report a set nine times its real size and
    make every proportion computed from it wrong.
    """
    operand = _operand("a", [], rows=[{"id": "VFB_1"}, {"id": "VFB_1"},
                                      {"id": "VFB_2"}])
    assert operand.ids == {"VFB_1", "VFB_2"}
    assert operand.rows_returned == 3
    assert operand.duplicate_rows == 1


def test_a_repeated_id_with_a_reported_count_is_not_truncation():
    """894 terms across 8,935 rows is complete, and must not be flagged.

    `count` describes terms; `len(rows)` describes rows. Comparing them
    directly — the obvious implementation — calls the most common shape in the
    whole API truncated, and a warning that fires on healthy data is a warning
    people learn to ignore.
    """
    operand = _operand("a", [], count=2, rows=[{"id": "VFB_1"}, {"id": "VFB_1"},
                                               {"id": "VFB_2"}])
    assert operand.truncated is False


def test_a_capped_result_is_truncation_and_says_so():
    """`DatasetImages/Nern2024` reports 60,002 and returns 25,000."""
    operand = _operand("a", [f"VFB_{i}" for i in range(10)], count=60002)
    assert operand.truncated is True


def test_rows_with_no_id_are_counted_rather_than_silently_dropped():
    operand = _operand("a", [], rows=[{"id": "VFB_1"}, {"label": "no id here"}])
    assert operand.ids == {"VFB_1"}
    assert operand.rows_without_id == 1


# ---------------------------------------------------------------------------
# The algebra, and the traps the implicit universe sets
# ---------------------------------------------------------------------------

def _evaluate(expr, sets, universe=None):
    operands = {name: _operand(name, ids) for name, ids in sets.items()}
    tree = c.parse(expr, known_names=set(operands))
    # The implicit universe covers the operands the *expression* uses, not every
    # operand that happens to be defined — as the handler does. An unused
    # operand widening the universe would silently change what NOT means.
    used = {name: operands[name] for name in tree.names()}
    uni = universe or c.implicit_universe(used)
    warnings, steps = [], []
    result = c.evaluate(tree, operands, uni, steps, warnings)
    return result, warnings, steps


SETS = {"a": {1, 2, 3}, "b": {3, 4, 5}, "c": {5, 6}}


@pytest.mark.parametrize("expr,expected", [
    ("a OR b",   {1, 2, 3, 4, 5}),
    ("a AND b",  {3}),
    ("a NOT b",  {1, 2}),
    ("b NOT a",  {4, 5}),
    ("a XOR b",  {1, 2, 4, 5}),
    # Grouping changes the answer, which is why the endpoint echoes it back.
    ("a OR b AND c",    {1, 2, 3, 5}),
    ("(a OR b) AND c",  {5}),
    ("a NOT b NOT c",   {1, 2}),
])
def test_the_algebra(expr, expected):
    result, _, _ = _evaluate(expr, SETS)
    assert result == expected


def test_a_complement_against_the_implicit_universe_warns_that_it_is_hollow():
    """NOR over the union of its own operands is empty. Always. By construction.

    `a NOR b` is "everything in neither", and when "everything" *is* what the
    queries found, nothing survives. The user gets zero rows from a well-formed
    request and no reason, and concludes the biology said no. It did not: the
    algebra did, before the biology was consulted. So the guarantee is stated
    rather than left to be discovered.
    """
    result, warnings, _ = _evaluate("a NOR b", SETS)
    assert result == set()
    assert any("always" in w and "universe=" in w for w in warnings)


def test_nand_and_xnor_collapse_the_same_way_and_say_so():
    """With the implicit universe, NAND is XOR and XNOR is AND.

    Both are true of any universe equal to the union of the operands, so the
    user who reached for NAND because it is the operator they know gets a right
    answer to a smaller question than they asked. Worth one sentence.
    """
    nand, nand_warnings, _ = _evaluate("a NAND b", SETS)
    xor, _, _ = _evaluate("a XOR b", SETS)
    assert nand == xor
    assert any("XOR" in w for w in nand_warnings)

    xnor, xnor_warnings, _ = _evaluate("a XNOR b", SETS)
    and_, _, _ = _evaluate("a AND b", SETS)
    assert xnor == and_
    assert any("AND" in w for w in xnor_warnings)


def test_an_explicit_universe_makes_complements_mean_something():
    """Given a wider universe the same expression stops being hollow."""
    everything = c.Universe(set(range(1, 11)), "explicit", "the numbers 1-10")
    result, warnings, _ = _evaluate("a NOR b", SETS, universe=everything)
    assert result == {6, 7, 8, 9, 10}
    # No trap warning: the traps are consequences of the implicit universe only.
    assert not any("always empty" in w for w in warnings)


def test_an_empty_intersection_across_namespaces_is_diagnosed_not_reported():
    """Classes and individuals cannot intersect, and the reason is structural.

    An `FBbt_` class id and a `VFB_` individual id are never equal, so an
    intersection of a class-level query with an image-level one is empty for
    every input — including inputs where the biology overlaps completely. Left
    unexplained this reads as 'no such neurons', which is the single most
    misleading answer this endpoint can give.
    """
    operands = {
        "a": _operand("a", {"FBbt_00007401", "FBbt_00003685"}),
        "b": _operand("b", {"VFB_00101567", "VFB_00101568"}),
    }
    tree = c.parse("a AND b", known_names=set(operands))
    warnings, steps = [], []
    result = c.evaluate(tree, operands, c.implicit_universe(operands),
                        steps, warnings)
    assert result == set()
    assert "why_empty" in steps[-1]
    assert "structural mismatch" in steps[-1]["why_empty"]
    assert any("structural mismatch" in w for w in warnings)


def test_a_genuinely_empty_overlap_in_one_namespace_is_not_explained_away():
    """The diagnosis must not fire when the emptiness is a real result."""
    operands = {
        "a": _operand("a", {"FBbt_1", "FBbt_2"}),
        "b": _operand("b", {"FBbt_3", "FBbt_4"}),
    }
    tree = c.parse("a AND b", known_names=set(operands))
    steps = []
    c.evaluate(tree, operands, c.implicit_universe(operands), steps, [])
    assert "why_empty" not in steps[-1]


def test_every_step_reports_the_sizes_it_went_in_and_came_out_with():
    """The trace is the explanation people actually read.

    'a found 567, b found 314, both found 91' tells a biologist whether the
    answer is interesting without their having to trust the operator at all —
    and it is how they notice that one side returned nothing.
    """
    _, _, steps = _evaluate("a AND b", SETS)
    assert steps[-1]["input_counts"] == [3, 3]
    assert steps[-1]["result_count"] == 1
    assert "BOTH" in steps[-1]["description"]


def test_plain_english_reads_as_a_sentence_and_names_the_queries():
    operands = {
        "calyx": c.OperandResult("calyx", {"rows": []},
                                 description="neurons with part in calyx"),
        "lh": c.OperandResult("lh", {"rows": []},
                              description="neurons with part in lateral horn"),
    }
    sentence = c.plain_english(c.parse("calyx AND lh"), operands)
    assert "BOTH" in sentence
    assert "neurons with part in calyx" in sentence
    assert "neurons with part in lateral horn" in sentence


# ---------------------------------------------------------------------------
# Lossless merging: no column from any operand may be lost
# ---------------------------------------------------------------------------

def _merge(payloads, expr="a OR b"):
    operands = {name: c.OperandResult(name, payload)
                for name, payload in payloads.items()}
    order = list(payloads)
    tree = c.parse(expr, known_names=set(operands))
    ids = c.evaluate(tree, operands, c.implicit_universe(operands))
    rows = c.build_rows(ids, operands, order)
    headers = c.merge_headers(operands, order, rows)
    return rows, headers


HEADERS_A = {"id": {"title": "ID", "type": "selection_id"},
             "label": {"title": "Name", "type": "markdown"},
             "nt": {"title": "Neurotransmitter", "type": "text"}}
HEADERS_B = {"id": {"title": "ID", "type": "selection_id"},
             "label": {"title": "Name", "type": "markdown"},
             "weight": {"title": "Synapses", "type": "numeric"}}


def test_columns_from_every_operand_survive_the_merge():
    """The union of the columns, not the intersection.

    Two queries carry different evidence — one has neurotransmitter
    predictions, the other synapse counts — and the reason to intersect them is
    usually to look at both together. Keeping only the columns they share
    throws away the answer.
    """
    rows, headers = _merge({
        "a": {"headers": HEADERS_A,
              "rows": [{"id": "VFB_1", "label": "DA1 lPN", "nt": "ACh"}]},
        "b": {"headers": HEADERS_B,
              "rows": [{"id": "VFB_1", "label": "DA1 lPN", "weight": 42}]},
    }, expr="a AND b")
    assert len(rows) == 1
    assert rows[0]["nt"] == "ACh"
    assert rows[0]["weight"] == 42
    assert set(headers) >= {"id", "label", "nt", "weight",
                            c.FOUND_IN, c.FOUND_IN_COUNT}


def test_agreeing_values_appear_once_and_disagreeing_ones_appear_all_of_them():
    """Disagreement is kept, under a column name that says where it came from.

    Two queries can legitimately give the same term different labels — one
    matched a synonym, the other the primary label — and there is no way to
    know which the user wanted. Picking one silently is the lossy option;
    picking one *and* keeping the other under `label__b` is not.
    """
    rows, headers = _merge({
        "a": {"headers": HEADERS_A,
              "rows": [{"id": "VFB_1", "label": "DA1 lPN", "nt": "ACh"}]},
        "b": {"headers": HEADERS_B,
              "rows": [{"id": "VFB_1", "label": "DA1 adPN", "weight": 42}]},
    }, expr="a AND b")
    row = rows[0]
    # Expression order decides which reading holds the plain name...
    assert row["label"] == "DA1 lPN"
    # ...and the other is not thrown away.
    assert row["label__b"] == "DA1 adPN"
    # The invented column inherits its base column's type, so a client that
    # renders markdown as markdown keeps doing so.
    assert headers["label__b"]["type"] == "markdown"
    assert headers["label__b"]["from_query"] == "b"


def test_several_rows_for_one_term_keep_all_their_distinct_values():
    """Folding duplicates must not mean discarding what made them different.

    The 8,935-row Kenyon cell result has 21 different query ids per term; those
    rows differ in the column that says which subclass produced them, and that
    column is often exactly what the user is after.
    """
    rows, _ = _merge({
        "a": {"headers": {"id": {"type": "selection_id"},
                          "via": {"title": "Via", "type": "text"}},
              "rows": [{"id": "VFB_1", "via": "KCg"},
                       {"id": "VFB_1", "via": "KCab"}]},
    }, expr="a")
    assert rows[0]["via"] == "KCg"
    assert rows[0]["via__a"] == ["KCg", "KCab"]


def test_provenance_is_a_column_so_the_answer_can_be_read_without_the_query():
    """`found_in` turns a merged table into its own audit trail."""
    rows, _ = _merge({
        "a": {"headers": HEADERS_A, "rows": [{"id": "VFB_1"}, {"id": "VFB_2"}]},
        "b": {"headers": HEADERS_B, "rows": [{"id": "VFB_2"}]},
    }, expr="a OR b")
    by_id = {row["id"]: row for row in rows}
    assert by_id["VFB_1"][c.FOUND_IN] == ["a"]
    assert by_id["VFB_2"][c.FOUND_IN] == ["a", "b"]
    assert by_id["VFB_2"][c.FOUND_IN_COUNT] == 2
    # Best-supported first: the term both queries found leads.
    assert rows[0]["id"] == "VFB_2"


def test_a_universe_member_no_query_returned_still_gets_a_row():
    """A complement must not silently shorten its own answer.

    With an explicit universe, `NOT a` can contain terms that appear in no
    operand at all, so there are no columns to merge for them. Emitting the bare
    id is the only answer that keeps `count` equal to the size of the set the
    algebra produced.
    """
    operands = {"a": _operand("a", {"VFB_1"})}
    universe = c.Universe({"VFB_1", "VFB_2"}, "explicit", "two terms")
    tree = c.parse("NOT a", known_names={"a"})
    ids = c.evaluate(tree, operands, universe)
    rows = c.build_rows(ids, operands, ["a"])
    assert [row["id"] for row in rows] == ["VFB_2"]
    assert rows[0][c.FOUND_IN] == []
