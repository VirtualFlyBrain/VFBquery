"""The interactive API docs stay in step with the server they describe."""

import json

import vfbquery.api_docs as api_docs
import vfbquery.ha_api as ha_api


def _spec():
    from vfbquery.catmaid_client import list_catmaid_commands
    return api_docs.build_docs_spec(
        "0.0.0-test", query_types=list(ha_api.QUERY_TYPE_MAP),
        catmaid_commands=list_catmaid_commands())


def _endpoint_paths(spec):
    return [endpoint["path"] for group in spec["groups"]
            for endpoint in group["endpoints"]]


def test_every_public_path_is_documented():
    """A path the allowlist serves but the docs omit is invisible to users."""
    documented = set(_endpoint_paths(_spec()))
    # Templated docs entries cover the /catmaid/... dynamic routes.
    documented_prefixes = tuple(path.split("{")[0] for path in documented
                                if "{" in path)
    for path in ha_api.ALLOWED_PATHS:
        if path in ("/", "/docs.json"):
            continue                      # the docs page itself
        assert (path in documented
                or path.startswith(documented_prefixes)), path


def test_every_documented_path_is_actually_served():
    for path in _endpoint_paths(_spec()):
        if "{" in path:
            assert path.split("{")[0].startswith(ha_api.ALLOWED_PATH_PREFIXES + ("/catmaid",))
        else:
            assert path in ha_api.ALLOWED_PATHS, path


def test_required_params_carry_runnable_examples():
    """The page promises pre-filled runnable examples — a required parameter
    with no example renders a Run button that can only fail."""
    for group in _spec()["groups"]:
        for endpoint in group["endpoints"]:
            for param in (endpoint.get("params") or []) + (
                    endpoint.get("path_params") or []):
                if param.get("required"):
                    assert param.get("example"), (endpoint["path"],
                                                  param["name"])


def test_spec_is_json_serialisable_with_vocabularies():
    spec = _spec()
    payload = json.loads(json.dumps(spec))
    assert payload["vocabularies"]["query_types"], "query_types empty"
    assert payload["vocabularies"]["catmaid_commands"], "catmaid registry empty"
    assert "swc_alignments" in payload["vocabularies"]["catmaid_commands"]


def test_html_is_self_contained():
    html = api_docs.DOCS_HTML
    assert "docs.json" in html
    assert "Virtual Fly Brain" in html
    # the CATMAID group expands into one runnable card per registry command
    assert "renderCatmaidCommands" in html
    assert "ep-catmaid-commands" in html
    assert "catmaidCommandEndpoint" in html
    # Self-contained: no external scripts, styles or images.
    assert 'src="http' not in html and "src='http" not in html
    assert '<link' not in html
    assert html.lstrip().startswith("<!DOCTYPE html>")


def test_docs_spec_cache_builds_once():
    first = ha_api._docs_spec()
    assert first is ha_api._docs_spec()
    assert first["version"] == ha_api.VFBQUERY_VERSION
