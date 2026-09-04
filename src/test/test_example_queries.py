"""The worked examples that used to live in the README, as a real test.

Historically the README embedded example queries with their JSON results,
a workflow executed the python blocks with `sed`, `readme_parser.py`
regenerated three throwaway modules from the markdown, and
`test_examples_diff.py` (run as a script, not pytest) checked result
*structure*. This module replaces all of that: the same five canonical
calls run live against the VFB backend, their structure is asserted the
way the old script asserted it, and each result is compared — shape,
not content — against the recorded expectation in
``example_expected/<name>.json`` (originally the JSON blocks the README
carried; re-recorded from live whenever the schema legitimately moves).

Shape-not-content is deliberate and preserves the old contract: backend
content changes (new images, edited descriptions, more rows) must not
fail CI, but a key or type disappearing from a payload is exactly the
regression these examples exist to catch. Additive change is allowed —
keys present live but not in the recording pass.

Run: ``pytest src/test/test_example_queries.py`` (live backend; the
``examples`` workflow runs it on every push and monthly). When a schema
change is intentional, re-record the expectations from live with
``python -m src.test.test_example_queries --record`` and commit the
fixture diff — the successor to the old ``update_readme.py`` flow.
"""

import json
import numbers
import os

import pytest

import vfbquery as vfb

HERE = os.path.dirname(__file__)
EXPECTED_DIR = os.path.join(HERE, "example_expected")

#: The canonical examples: (fixture name, callable). Mirrors the calls the
#: old pipeline ran, including which ones force_refresh (the performance
#: baseline terms deliberately exercise the cache path).
EXAMPLES = {
    "term_info_FBbt_00003748":
        lambda: vfb.get_term_info("FBbt_00003748", force_refresh=True),
    "term_info_VFB_00000001":
        lambda: vfb.get_term_info("VFB_00000001"),
    "term_info_VFB_00101567":
        lambda: vfb.get_term_info("VFB_00101567"),
    "instances_FBbt_00003748":
        lambda: vfb.get_instances("FBbt_00003748", return_dataframe=False,
                                  force_refresh=True),
    "templates":
        lambda: vfb.get_templates(return_dataframe=False),
}

_results = {}


def _run(name):
    """Run each example once per session, however many tests look at it."""
    if name not in _results:
        _results[name] = EXAMPLES[name]()
    return _results[name]


def _expected(name):
    with open(os.path.join(EXPECTED_DIR, name + ".json")) as f:
        return json.load(f)


def _type_bucket(value):
    """Coarse type category for leaf comparison: content may change freely,
    a bool becoming a string may not.

    Live results can carry numpy scalars (int64 counts out of pandas on
    some environments) where the JSON recording holds plain numbers; both
    are "number" — the environment's box type is not a schema property.
    numpy scalar types register with the ``numbers`` ABCs, so no numpy
    import is needed; ``bool_``/``str_`` are matched by name for the same
    reason.
    """
    name = type(value).__name__
    if isinstance(value, bool) or name == "bool_":
        return "bool"
    if isinstance(value, numbers.Number):
        return "number"
    if isinstance(value, str) or name == "str_":
        return "string"
    return name


#: Recorded maps whose KEYS are data rather than schema, compared like
#: lists: the map must still be non-empty and its values must still have
#: the recorded shape, but *which* keys appear is content.
#:
#: ``Examples`` and ``Images`` are keyed by template short_form and
#: ``Domains``/``Licenses`` by index, so their key sets follow whichever
#: images the indexer happened to pick. The class documents cap
#: ``anatomy_channel_image`` at ten entries however many images a class
#: really has (56,384 for adult cholinergic neuron; 12 for medulla), so a
#: class whose only image on some template falls outside that ten loses
#: that template key entirely — no schema changed, and nothing is missing
#: from the backend. That is exactly the "backend content changes must not
#: fail CI" case in this module's docstring, and treating these keys as
#: schema turned it into a failure (medulla lost VFB_00030786, adult brain
#: template Ito2014, on 2026-09-03 while the individual, its own SOLR
#: document and all its image files were intact).
#:
#: ``Meta`` is deliberately absent: its keys ARE the schema.
DATA_KEYED_MAPS = frozenset({"$.Examples", "$.Images", "$.Domains",
                             "$.Licenses"})


def shape_mismatches(expected, live, path="$"):
    """Recursively compare recorded vs live result SHAPE.

    Every key in the recording must exist live with a compatible type;
    lists are compared through their first element; leaf values only have
    to agree on coarse type. Keys the live result has gained are fine.

    The exception is the maps in :data:`DATA_KEYED_MAPS`, whose keys are
    data: those are compared the way lists are — non-emptiness and the
    shape of one value — because their key sets legitimately change with
    the backend content.
    """
    if isinstance(expected, dict):
        if not isinstance(live, dict):
            return ["%s: recorded an object, live is %s"
                    % (path, _type_bucket(live))]
        if path in DATA_KEYED_MAPS:
            if expected and not live:
                return ["%s: recorded non-empty, live is empty" % path]
            if expected and live:
                return shape_mismatches(next(iter(expected.values())),
                                        next(iter(live.values())),
                                        path + ".*")
            return []
        problems = []
        for key, value in expected.items():
            live_key = key
            if key not in live and isinstance(key, str) and key.isdigit():
                # JSON stringifies integer dict keys; the live Python
                # result still uses ints (e.g. sort: {0: 'Asc'}).
                if int(key) in live:
                    live_key = int(key)
            if live_key not in live:
                problems.append("%s.%s: missing from live result"
                                % (path, key))
            elif live[live_key] is not None and value is not None:
                problems.extend(
                    shape_mismatches(value, live[live_key],
                                     "%s.%s" % (path, key)))
        return problems
    if isinstance(expected, list):
        if not isinstance(live, list):
            return ["%s: recorded a list, live is %s"
                    % (path, _type_bucket(live))]
        if expected and not live:
            return ["%s: recorded non-empty, live is empty" % path]
        if expected and live:
            return shape_mismatches(expected[0], live[0], path + "[0]")
        return []
    if _type_bucket(expected) != _type_bucket(live):
        return ["%s: recorded %s, live is %s"
                % (path, _type_bucket(expected), _type_bucket(live))]
    return []


# ---------------------------------------------------------------------------
# Structure assertions — the checks test_examples_diff.py used to make.
# ---------------------------------------------------------------------------

TERM_INFO_EXAMPLES = ["term_info_FBbt_00003748", "term_info_VFB_00000001",
                      "term_info_VFB_00101567"]
ROW_EXAMPLES = ["instances_FBbt_00003748", "templates"]


@pytest.mark.parametrize("name", TERM_INFO_EXAMPLES)
def test_term_info_examples_have_the_expected_structure(name):
    result = _run(name)
    assert isinstance(result, dict), "get_term_info should return a dict"
    for key in ("IsIndividual", "IsClass", "Images", "Examples", "Domains",
                "Licenses", "Publications"):
        assert key in result, "missing key: %s" % key
    for key in ("IsIndividual", "IsClass"):
        assert isinstance(result[key], bool), "%s is not bool" % key
    assert isinstance(result.get("SuperTypes", []), list)
    assert isinstance(result.get("Queries", []), list)


@pytest.mark.parametrize("name", ROW_EXAMPLES)
def test_row_examples_have_rows(name):
    result = _run(name)
    assert isinstance(result, dict), "%s should return a dict" % name
    assert "rows" in result and isinstance(result["rows"], list)
    assert result["rows"], "%s returned no rows" % name
    assert isinstance(result["rows"][0], dict)


def test_term_info_examples_answer_for_the_requested_term():
    assert _run("term_info_FBbt_00003748")["Id"] == "FBbt_00003748"
    assert _run("term_info_VFB_00000001")["Id"] == "VFB_00000001"
    assert _run("term_info_VFB_00101567")["Id"] == "VFB_00101567"


# ---------------------------------------------------------------------------
# Shape comparison against the recorded expectations.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_live_result_matches_recorded_shape(name):
    problems = shape_mismatches(_expected(name), _run(name))
    assert not problems, (
        "%s drifted from src/test/example_expected/%s.json:\n  %s\n"
        "If the schema change is intentional, update the recording."
        % (name, name, "\n  ".join(problems)))


# ---------------------------------------------------------------------------
# The comparator itself.
# ---------------------------------------------------------------------------

def test_shape_comparator_catches_regressions():
    recorded = {"Name": "x", "count": 1, "rows": [{"id": "a", "n": 2}],
                "flag": True}
    assert not shape_mismatches(recorded, recorded)
    # additive live keys pass; content changes pass
    assert not shape_mismatches(
        recorded, {"Name": "y", "count": 9, "rows": [{"id": "b", "n": 3,
                                                      "extra": 1}],
                   "flag": False, "new_key": "fine"})
    assert shape_mismatches(recorded, {"count": 1, "rows": [], "flag": True})
    assert shape_mismatches(recorded, {"Name": 1, "count": 1,
                                       "rows": [{"id": "a", "n": 2}],
                                       "flag": True})
    assert shape_mismatches(recorded, {"Name": "x", "count": 1, "rows": [],
                                       "flag": True})


def test_numpy_scalars_count_as_numbers():
    numpy = pytest.importorskip("numpy")
    assert not shape_mismatches({"count": 3}, {"count": numpy.int64(5)})
    assert not shape_mismatches({"score": 0.5}, {"score": numpy.float64(1.5)})
    assert not shape_mismatches({"flag": True}, {"flag": numpy.bool_(False)})
    assert shape_mismatches({"count": 3}, {"count": "5"})   # still a drift


def test_data_keyed_maps_ignore_which_keys_appear():
    """Examples/Images/Domains/Licenses key sets are content, not schema."""
    recorded = {"Examples": {"VFB_00030786": [{"id": "VFB_00030810",
                                               "label": "medulla",
                                               "thumbnail": "https://x/t.png"}]}}
    # A different template carrying the same record shape is not a drift --
    # this is the medulla / Ito2014 case, where the class document's ten-image
    # cap dropped the only image on one template.
    assert not shape_mismatches(recorded, {"Examples": {"VFB_00101567": [
        {"id": "VFB_00107fob", "label": "ME_R", "thumbnail": "https://y/t.png"}]}})
    # Losing the map altogether still fails.
    assert shape_mismatches(recorded, {"Examples": {}})
    # So does a record that lost a field, or changed a field's type.
    assert shape_mismatches(recorded, {"Examples": {"VFB_00101567": [
        {"id": "VFB_00107fob", "label": "ME_R"}]}})
    assert shape_mismatches(recorded, {"Examples": {"VFB_00101567": [
        {"id": 7, "label": "ME_R", "thumbnail": "https://y/t.png"}]}})
    # An empty recording stays permissive: gaining content is allowed.
    assert not shape_mismatches({"Examples": {}}, recorded)


def test_meta_keys_are_still_schema():
    """Meta is not data-keyed -- a missing Meta field is still a regression."""
    recorded = {"Meta": {"Name": "medulla", "Types": "x"}}
    assert shape_mismatches(recorded, {"Meta": {"Name": "medulla"}})


# ---------------------------------------------------------------------------
# Re-recording — `python -m src.test.test_example_queries --record`
# ---------------------------------------------------------------------------

def record():
    """Rewrite every fixture in example_expected/ from a live run."""
    for name in sorted(EXAMPLES):
        result = EXAMPLES[name]()
        path = os.path.join(EXPECTED_DIR, name + ".json")
        with open(path, "w") as f:
            json.dump(result, f, indent=1, default=str)
        print("recorded %s (%d bytes)" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    import sys
    if "--record" in sys.argv:
        record()
    else:
        print(__doc__)
