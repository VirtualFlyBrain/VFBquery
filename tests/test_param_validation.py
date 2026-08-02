"""A malformed integer parameter is the caller's fault, and must read as one.

`weight` and `max_depth` were cast with a bare ``int()``, so
``?weight=abc`` escaped as an unhandled ValueError and aiohttp turned it into
``500 Internal Server Error / Server got itself in trouble``. Every other
endpoint already returned a 400 that names the parameter, so the fault was not
that a bad value was accepted — it was that the response blamed the server, told
the caller nothing, and put a traceback in the logs of a healthy service.

``_dispatch_to_pool`` is replaced with a sentinel, which makes the *other* half
of the contract testable: a rejected request must be rejected **before** any
work is dispatched. A 400 that still ran a Neo4j query would pass a
status-code-only test.
"""
import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from conftest import run
from vfbquery import ha_api


def _make_app(monkeypatch):
    dispatched = []

    # ``known_params`` is accepted and ignored: the real ``_dispatch_to_pool``
    # grew that keyword after this stub was written, and a stub with the
    # narrower signature turns every call that reaches it into a TypeError the
    # handler reports as a 500 — which reads exactly like the defect these tests
    # exist to catch, so the suite failed while the service was fine.
    async def fake_dispatch(request, cache_key, worker_fn, *args, post_fn=None,
                            known_params=None):
        dispatched.append(cache_key)
        # The html handler parses this body, so it has to look like a result.
        return web.json_response({"html": "<div>tree</div>"})

    monkeypatch.setattr(ha_api, "_dispatch_to_pool", fake_dispatch, raising=True)

    app = web.Application()
    app.router.add_get("/query_connectivity", ha_api.handle_query_connectivity)
    app.router.add_get("/get_hierarchy", ha_api.handle_get_hierarchy)
    app.router.add_get("/get_hierarchy_html", ha_api.handle_get_hierarchy_html)

    async def on_startup(app):
        app["result_cache"] = ha_api.ResultCache(ttl_seconds=300)

    app.on_startup.append(on_startup)
    return app, dispatched


def _get(app, path, params):
    async def go():
        client = TestClient(TestServer(app))
        await client.start_server()
        try:
            response = await client.get(path, params=params)
            return response.status, await response.text()
        finally:
            await client.close()
    return run(go())


# ---------------------------------------------------------------------------
# The three sites that used to 500
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", ["abc", "5.5", "", " ", "1e3", "-", "5,000", "0x10"])
def test_a_non_integer_weight_is_a_400_that_names_the_parameter(monkeypatch, bad):
    """Including the empty string: `?weight=` is a caller who built a URL from an
    unset variable, and the documented default is the right answer for it."""
    app, dispatched = _make_app(monkeypatch)
    status, text = _get(app, "/query_connectivity",
                        {"upstream_type": "Kenyon cell", "weight": bad})
    if bad.strip() == "":
        # Absent-or-blank falls back to the default and runs normally.
        assert status == 200 and dispatched
        assert ":5:" in dispatched[0]       # the documented default weight
        return
    assert status == 400
    assert "weight must be an integer" in text
    assert dispatched == []                # rejected before any work was done


def test_a_unicode_digit_is_accepted_because_it_is_a_number(monkeypatch):
    """`weight=٣` is read as 3, and that is the right answer, not a leak.

    Python's ``int()`` accepts any character with a Unicode decimal property, so
    the Arabic-Indic digit three parses. It would be easy to mistake that for a
    hole in the guard and bolt on an ASCII-only check, but the value *is* the
    number three and the caller who sent it meant three. Recorded here so the
    next person to notice it finds a decision rather than an oversight.
    """
    app, dispatched = _make_app(monkeypatch)
    status, _ = _get(app, "/query_connectivity",
                     {"upstream_type": "Kenyon cell", "weight": "٣"})
    assert status == 200 and ":3:" in dispatched[0]


def test_a_negative_weight_is_refused_rather_than_quietly_floored(monkeypatch):
    """Every synaptic weight is positive, so a threshold below zero cannot mean
    anything; answering it as if it meant zero answers a question nobody put."""
    app, dispatched = _make_app(monkeypatch)
    status, text = _get(app, "/query_connectivity",
                        {"upstream_type": "Kenyon cell", "weight": "-1"})
    assert status == 400 and "at least 0" in text
    assert dispatched == []


@pytest.mark.parametrize("path", ["/get_hierarchy", "/get_hierarchy_html"])
@pytest.mark.parametrize("bad", ["abc", "2.5", "-1"])
def test_a_bad_max_depth_is_a_400_on_both_hierarchy_handlers(monkeypatch, path, bad):
    app, dispatched = _make_app(monkeypatch)
    status, text = _get(app, path, {"id": "FBbt_00005801", "max_depth": bad})
    assert status == 400
    assert "max_depth" in text
    assert dispatched == []


def test_the_html_handler_answers_in_text_and_the_json_one_in_json(monkeypatch):
    """The html handler's caller is a browser rendering the body directly, so its
    errors are plain text — as every other error it already returned was. A JSON
    envelope here would be displayed verbatim to whoever opened the ROI browser.
    """
    app, _ = _make_app(monkeypatch)
    status, text = _get(app, "/get_hierarchy_html",
                        {"id": "FBbt_00005801", "max_depth": "abc"})
    assert status == 400 and text.startswith("Error: max_depth must be an integer")

    app, _ = _make_app(monkeypatch)
    status, text = _get(app, "/get_hierarchy",
                        {"id": "FBbt_00005801", "max_depth": "abc"})
    assert status == 400 and text.lstrip().startswith("{")
    assert "max_depth must be an integer" in text


def test_a_good_value_still_reaches_the_worker(monkeypatch):
    """The guard has to be a guard, not a wall."""
    app, dispatched = _make_app(monkeypatch)
    status, _ = _get(app, "/query_connectivity",
                     {"upstream_type": "Kenyon cell", "weight": "50"})
    assert status == 200 and ":50:" in dispatched[0]

    app, dispatched = _make_app(monkeypatch)
    status, _ = _get(app, "/get_hierarchy",
                     {"id": "FBbt_00005801", "max_depth": "3"})
    assert status == 200 and dispatched[0].endswith(":3")

    # max_depth=0 is a legitimate request for the term on its own.
    app, dispatched = _make_app(monkeypatch)
    status, _ = _get(app, "/get_hierarchy",
                     {"id": "FBbt_00005801", "max_depth": "0"})
    assert status == 200 and dispatched[0].endswith(":0")


# ---------------------------------------------------------------------------
# The parser itself
# ---------------------------------------------------------------------------

class _FakeRequest:
    def __init__(self, **query):
        self.query = query


def test_query_int_bounds_and_messages():
    req = _FakeRequest(n="7")
    assert ha_api._query_int(req, "n", 1) == 7
    assert ha_api._query_int(req, "missing", 42) == 42
    assert ha_api._query_int(_FakeRequest(n=""), "n", 42) == 42

    with pytest.raises(ha_api.BadParam) as exc:
        ha_api._query_int(_FakeRequest(n="x"), "n", 1)
    # The offending value is echoed: with four integer parameters in play, the
    # caller should not have to guess which one their framework mangled.
    assert "n must be an integer" in str(exc.value) and "'x'" in str(exc.value)

    with pytest.raises(ha_api.BadParam):
        ha_api._query_int(req, "n", 1, maximum=5)
    with pytest.raises(ha_api.BadParam):
        ha_api._query_int(req, "n", 1, minimum=8)
    # BadParam is a ValueError, so an un-updated caller still catches it rather
    # than letting it through as a 500.
    assert issubclass(ha_api.BadParam, ValueError)


def test_paging_hints_still_fall_back_rather_than_failing():
    """`offset`/`limit` keep the old lenient behaviour, deliberately.

    A bad paging hint still has an obviously right answer — the first page — but
    silently substituting weight=5 or max_depth=1 would answer a different
    question from the one asked. The two are treated differently on purpose, and
    this records that it is a decision rather than an omission.
    """
    from vfbquery.ha_api import handle_run_query      # noqa: F401  (documented)
    # The lenient parser is a closure inside the handler; its behaviour is
    # asserted through the endpoint elsewhere. What is checkable here is that
    # the strict one is not wired into it.
    import inspect
    # Comments are stripped before the check. The question is what the handler
    # *calls*, and a cross-reference in a comment — "see _query_int" — is not a
    # call. Matching raw source made this fail the moment someone documented the
    # very distinction the test is here to protect.
    src = "\n".join(line.split("#", 1)[0]
                    for line in inspect.getsource(ha_api.handle_run_query).splitlines())
    assert "_int_param" in src and "_query_int" not in src
