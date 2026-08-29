"""Tests for the CATMAID pass-through (catmaid_client + the /catmaid routes).

Unit tests exercise the registry, id handling and request assembly against
mocks; the ``integration``-marked tests at the bottom go to the live hosted
CATMAID instances and the KB, like the rest of this suite does. Skip those
with ``-m 'not integration'``.
"""

import pytest

import vfbquery.catmaid_client as cm
import vfbquery.ha_api as ha_api


# ---------------------------------------------------------------------------
# Registry integrity
# ---------------------------------------------------------------------------

_WRITE_FRAGMENTS = ("rename", "import", "delete", "add", "fork", "revoke",
                    "datastores", "samplers", "project-tokens", "favorite")


def test_registry_is_read_only():
    """No command may point at a CATMAID write or admin endpoint."""
    for name, spec in cm.CATMAID_COMMANDS.items():
        assert spec["method"] in ("GET", "POST"), name
        for fragment in _WRITE_FRAGMENTS:
            assert fragment not in spec["path"], (name, fragment)


def test_registry_paths_format_cleanly():
    slots = {"project_id": 1, "skeleton_id": 2, "neuron_id": 3,
             "treenode_id": 4, "connector_id": 5, "node_type": "treenode",
             "node_id": 6}
    for name, spec in cm.CATMAID_COMMANDS.items():
        if spec.get("local"):        # answered by VFBquery, not CATMAID
            continue
        path = spec["path"].format(**slots)
        assert "{" not in path and "}" not in path, name
        assert path.startswith("/"), name


def test_registry_id_specs_are_well_formed():
    for name, spec in cm.CATMAID_COMMANDS.items():
        for public, wire in (spec.get("id_params") or {}).items():
            assert "{i}" in wire, (name, public)
        if spec.get("id_path"):
            assert spec["id_path"]["kind"] in ("skid", "neuron_id"), name
            if not spec.get("local"):
                assert "{%s}" % spec["id_path"]["slot"] in spec["path"], name
        assert spec.get("returns", "json") in ("json", "text", "bytes"), name


def test_list_catmaid_commands_shape():
    listing = cm.list_catmaid_commands()
    assert listing["connectivity"]["takes_ids"] == ["ids"]
    assert sorted(listing["connectivity_matrix"]["takes_ids"]) == [
        "columns", "rows"]
    assert listing["swc"]["returns"] == "text"
    assert listing["neuron_skeletons"]["takes_ids"] == ["id"]


# ---------------------------------------------------------------------------
# id parsing / classification
# ---------------------------------------------------------------------------

def test_as_id_list_accepts_mixed_forms():
    assert cm._as_id_list("16, 17") == ["16", "17"]
    assert cm._as_id_list(["VFB_00101567", 16]) == ["VFB_00101567", "16"]
    assert cm._as_id_list(16) == ["16"]
    assert cm._as_id_list(None) == []


def test_as_id_list_rejects_junk():
    with pytest.raises(ValueError):
        cm._as_id_list("DROP TABLE")
    with pytest.raises(ValueError):
        cm._as_id_list("VFB_001")          # too short to be a VFB id
    with pytest.raises(ValueError):
        cm._as_id_list("VFB_00101567'")    # quote never reaches Cypher


def test_as_id_list_caps_volume(monkeypatch):
    monkeypatch.setattr(cm, "MAX_IDS_PER_CALL", 3)
    with pytest.raises(ValueError):
        cm._as_id_list(["1", "2", "3", "4"])


def test_collect_skid_like_keys_bounded():
    found = set()
    payload = {"incoming": {str(i): {"x": 1} for i in range(50)},
               "not_a_skid": {"abc": 1}}
    cm._collect_skid_like_keys(payload, found, 10)
    assert len(found) == 10
    assert all(k.isdigit() for k in found)


# ---------------------------------------------------------------------------
# Request assembly against a mocked instance
# ---------------------------------------------------------------------------

_FAKE_CONFIG = {
    "instances": [
        {"id": "fafb", "name": "FAFB",
         "url": "https://fafb.example.org", "api_token": "tok",
         "projects": [{"id": 1, "title": "Adult Brain"}]},
        {"id": "bare", "name": "No xrefs",
         "url": "https://bare.example.org", "api_token": "tok2",
         "projects": [{"id": 2, "title": "Only project"}]},
    ]
}


@pytest.fixture
def fake_instance(monkeypatch):
    """A CatmaidInstance wired to a fake config, fake KB and captured HTTP."""
    calls = []

    monkeypatch.setattr(cm, "get_catmaid_config", lambda **kw: _FAKE_CONFIG)
    monkeypatch.setattr(cm, "_xref_site_map",
                        lambda **kw: {("fafb", 1): "catmaid_fafb"})
    monkeypatch.setattr(
        cm, "vfb_ids_to_skids",
        lambda ids, site: {i: str(100 + n) for n, i in enumerate(sorted(ids))
                           if not i.endswith("zz")})
    monkeypatch.setattr(
        cm, "skids_to_vfb_ids",
        lambda skids, site: {s: "VFB_%08d" % int(s) for s in skids})

    def fake_request(self, method, path, params):
        calls.append((method, path, dict(params)))
        return {"body": {"101": "a neuron"}, "kind": "json"}

    monkeypatch.setattr(cm.CatmaidInstance, "_request", fake_request)
    return cm.catmaid("fafb"), calls


def test_mixed_ids_become_indexed_wire_params(fake_instance):
    fafb, calls = fake_instance
    envelope = fafb.neuron_names(ids=["VFB_0010000a", "555"])
    method, path, params = calls[-1]
    assert (method, path) == ("POST", "/1/skeleton/neuronnames")
    assert params == {"skids[0]": "100", "skids[1]": "555"}
    assert envelope["id_map"] == {"VFB_0010000a": "100"}
    assert envelope["unmatched"] == []
    assert envelope["xref_db"] == "catmaid_fafb"
    assert envelope["reverse_map"]  # populated via skids_to_vfb_ids


def test_unmatched_vfb_ids_are_reported_not_sent(fake_instance):
    fafb, calls = fake_instance
    envelope = fafb.neuron_names(ids=["VFB_001000zz", "555"])
    _, _, params = calls[-1]
    assert params == {"skids[0]": "555"}
    assert envelope["unmatched"] == ["VFB_001000zz"]


def test_two_id_list_params(fake_instance):
    fafb, calls = fake_instance
    fafb.connectivity_matrix(rows=["1"], columns=["2", "3"])
    _, path, params = calls[-1]
    assert path == "/1/skeleton/connectivity_matrix"
    assert params == {"rows[0]": "1", "columns[0]": "2", "columns[1]": "3"}


def test_passthrough_params_forwarded_verbatim(fake_instance):
    fafb, calls = fake_instance
    fafb.connectivity(ids=["555"], boolean_op="OR", with_nodes=False)
    _, _, params = calls[-1]
    assert params["boolean_op"] == "OR"
    assert params["with_nodes"] == "false"


def test_raw_returns_untouched_body(fake_instance):
    fafb, _ = fake_instance
    assert fafb.neuron_names(ids=["555"], raw=True) == {"101": "a neuron"}


def test_vfb_ids_refused_where_no_xref_site(fake_instance):
    _, _ = fake_instance
    bare = cm.catmaid("bare")
    with pytest.raises(ValueError, match="no VFB skid cross-references"):
        bare.neuron_names(ids=["VFB_0010000a"])
    # plain skids still fine
    assert bare.neuron_names(ids=["555"], raw=True) == {"101": "a neuron"}


def test_unknown_instance_and_project_and_command(fake_instance):
    _, _ = fake_instance
    with pytest.raises(ValueError, match="Unknown CATMAID instance"):
        cm.catmaid("nope")
    with pytest.raises(ValueError, match="has no project"):
        cm.catmaid("fafb", project=9)
    fafb = cm.catmaid("fafb")
    with pytest.raises(ValueError, match="Unknown CATMAID command"):
        fafb.call("write_all_the_things")


def test_missing_required_ids(fake_instance):
    fafb, _ = fake_instance
    with pytest.raises(ValueError, match="requires 'ids'"):
        fafb.connectivity()
    with pytest.raises(ValueError, match="requires 'id'"):
        fafb.swc()


def test_neuron_id_bridge(monkeypatch, fake_instance):
    fafb, calls = fake_instance

    def fake_request(self, method, path, params):
        calls.append((method, path, dict(params)))
        if path.endswith("/neurons/from-models"):
            return {"body": {"555": 999}, "kind": "json"}
        return {"body": [555], "kind": "json"}

    monkeypatch.setattr(cm.CatmaidInstance, "_request", fake_request)
    envelope = fafb.neuron_skeletons(id="555")
    assert calls[-2][1] == "/1/neurons/from-models"
    assert calls[-1][1] == "/1/neuron/999/get-all-skeletons"
    assert any("999" in n for n in envelope["notes"])


def test_cypher_id_quoting_only_sees_validated_ids():
    # _quote_list is only ever fed regex-validated ids, but keep it honest.
    assert cm._quote_list(["16", "VFB_00101567"]) == "['16', 'VFB_00101567']"
    for ch in "'\";":
        assert ch not in "".join(
            c for c in cm._quote_list(["123"]) if c not in "[]', ")


# ---------------------------------------------------------------------------
# ha_api plumbing
# ---------------------------------------------------------------------------

def test_catmaid_paths_pass_the_allowlist():
    assert "/catmaid" in ha_api.ALLOWED_PATHS
    assert "/catmaid/fafb/swc".startswith(ha_api.ALLOWED_PATH_PREFIXES)
    assert not "/catmaidx".startswith(ha_api.ALLOWED_PATH_PREFIXES)


def test_catmaid_name_validators():
    assert ha_api._CATMAID_INSTANCE_RE.match("abd1.5")
    assert ha_api._CATMAID_INSTANCE_RE.match("iav-robo")
    assert not ha_api._CATMAID_INSTANCE_RE.match("../etc")
    assert ha_api._CATMAID_COMMAND_RE.match("neuron_names")
    assert not ha_api._CATMAID_COMMAND_RE.match("neuron-names/")


def test_catmaid_raw_view_unwraps_envelope_only():
    envelope = {"command": "swc", "result": "raw text", "id_map": {}}
    assert ha_api._catmaid_raw_view(envelope) == "raw text"
    assert ha_api._catmaid_raw_view({"anything": 1}) == {"anything": 1}
    assert ha_api._catmaid_raw_view("bare") == "bare"


# ---------------------------------------------------------------------------
# Live integration — hosted CATMAID + KB, like the rest of the suite
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_live_instance_listing():
    listing = cm.list_catmaid_instances()
    ids = {i["id"] for i in listing["instances"]}
    assert {"fafb", "l1em", "fanc"} <= ids
    fafb = next(i for i in listing["instances"] if i["id"] == "fafb")
    assert fafb["projects"][0]["vfb_xref_db"] == "catmaid_fafb"
    assert fafb["api_token"]


@pytest.mark.integration
def test_live_site_map_covers_both_fanc_projects():
    site_map = cm._xref_site_map()
    assert site_map.get(("fanc", 1)) == "catmaid_fanc"
    assert site_map.get(("fanc", 2)) == "catmaid_fanc_JRC2018VF"


@pytest.mark.integration
def test_live_round_trip_on_fafb():
    """A KB xref converts to a skid, CATMAID answers, and the reverse map
    points back at the same VFB id."""
    rows = cm.dict_cursor(cm._get_nc().commit_list([
        "MATCH (s:Site {short_form: 'catmaid_fafb'})"
        "<-[r:database_cross_reference]-(i:Entity) "
        "RETURN i.short_form AS vfb_id, r.accession[0] AS skid LIMIT 1"]))
    vfb_id, skid = rows[0]["vfb_id"], str(rows[0]["skid"])

    fafb = cm.catmaid("fafb")
    envelope = fafb.neuron_names(ids=[vfb_id])
    assert envelope["id_map"] == {vfb_id: skid}
    assert envelope["unmatched"] == []
    assert skid in envelope["result"]
    assert envelope["reverse_map"].get(skid) == vfb_id

    raw = fafb.neuron_names(ids=[vfb_id], raw=True)
    assert raw == envelope["result"]


@pytest.mark.integration
def test_live_swc_is_text():
    rows = cm.dict_cursor(cm._get_nc().commit_list([
        "MATCH (s:Site {short_form: 'catmaid_l1em'})"
        "<-[r:database_cross_reference]-(i:Entity) "
        "RETURN i.short_form AS vfb_id LIMIT 1"]))
    l1em = cm.catmaid("l1em")
    envelope = l1em.swc(id=rows[0]["vfb_id"])
    lines = envelope["result"].splitlines()
    assert lines and len(lines[0].split()) == 7   # SWC columns


@pytest.mark.integration
def test_live_skid_only_instance_refuses_vfb_ids():
    l3vnc = cm.catmaid("l3vnc")
    with pytest.raises(ValueError, match="no VFB skid cross-references"):
        l3vnc.neuron_names(ids=["VFB_00101567"])
    projects = l3vnc.projects(raw=True)
    assert isinstance(projects, list) and projects


# ---------------------------------------------------------------------------
# Aligned SWC option
# ---------------------------------------------------------------------------

def test_truthy_understands_http_flags():
    assert cm._truthy(True) and cm._truthy("true") and cm._truthy("1")
    assert not cm._truthy(False) and not cm._truthy("false")
    assert not cm._truthy("") and not cm._truthy(None)


class _FakeResp:
    def __init__(self, status_code=200, content=b"# SWC\n1 0 0 0 0 1 -1\n"):
        self.status_code = status_code
        self.content = content


def test_aligned_swc_from_vfb_store(monkeypatch, fake_instance):
    fafb, _ = fake_instance
    urls = []
    monkeypatch.setattr(cm, "list_aligned_templates", lambda vfb_id: [
        {"template": "VFB_00101567", "label": "JRC2018Unisex",
         "folder": "http://www.virtualflybrain.org/data/VFB/i/0010/000a/"
                   "VFB_00101567/"}])

    class FakeSession:
        def get(self, url, **kw):
            urls.append(url)
            return _FakeResp()

    monkeypatch.setattr(cm, "_http_session", lambda: FakeSession())
    envelope = fafb.swc(id="VFB_0010000a", aligned=True)
    assert envelope["aligned"] is True
    assert envelope["template"]["label"] == "JRC2018Unisex"
    assert envelope["result"].startswith("# SWC")
    assert urls == ["https://www.virtualflybrain.org/data/VFB/i/0010/000a/"
                    "VFB_00101567/volume.swc"]           # https swap + file
    assert fafb.swc(id="VFB_0010000a", aligned="true",
                    raw=True).startswith("# SWC")


def test_aligned_swc_multiple_templates_need_a_choice(monkeypatch,
                                                      fake_instance):
    fafb, _ = fake_instance
    regs = [{"template": "VFB_1", "label": "JRC2018Unisex",
             "folder": "http://x/a/"},
            {"template": "VFB_2", "label": "JRC2018UnifiedCNS",
             "folder": "http://x/b/"}]
    monkeypatch.setattr(cm, "list_aligned_templates", lambda vfb_id: regs)
    # generic "the VFB copy" is ambiguous once there are two registrations
    with pytest.raises(ValueError, match="pass aligned="):
        fafb.swc(id="VFB_0010000a", aligned=True)
    with pytest.raises(ValueError, match="pass aligned="):
        fafb.swc(id="VFB_0010000a", aligned="vfb")

    class FakeSession:
        def get(self, url, **kw):
            assert url == "https://x/b/volume.swc"
            return _FakeResp()

    monkeypatch.setattr(cm, "_http_session", lambda: FakeSession())
    # pick by template short_form or by label, case-insensitively
    envelope = fafb.swc(id="VFB_0010000a", aligned="VFB_2")
    assert envelope["template"]["short_form"] == "VFB_2"
    envelope = fafb.swc(id="VFB_0010000a", aligned="jrc2018unifiedcns")
    assert envelope["template"]["short_form"] == "VFB_2"
    with pytest.raises(ValueError, match="not registered to template"):
        fafb.swc(id="VFB_0010000a", aligned="VFB_9")


def test_aligned_swc_rejects_stray_params_and_id_lists(fake_instance):
    fafb, _ = fake_instance
    with pytest.raises(ValueError, match="takes only id="):
        fafb.swc(id="VFB_0010000a", aligned=True, with_tags=1)
    with pytest.raises(ValueError, match="exactly one id"):
        fafb.swc(id="VFB_0010000a,VFB_0010000b", aligned=True)


def test_aligned_original_means_catmaid(fake_instance):
    fafb, calls = fake_instance
    fafb.swc(id="555", aligned="original", raw=True)
    method, path, _ = calls[-1]
    assert (method, path) == ("GET", "/1/skeleton/555/swc")
    fafb.swc(id="555", aligned="false", raw=True)
    assert calls[-1][1] == "/1/skeleton/555/swc"


def test_catmaid_config_cached_for_whole_run_by_default(monkeypatch):
    fetches = []

    class FakeSession:
        def get(self, url, **kw):
            fetches.append(url)
            resp = _FakeResp()
            resp.raise_for_status = lambda: None
            resp.json = lambda: {"instances": [{"id": "x"}]}
            return resp

    monkeypatch.setattr(cm, "_http_session", lambda: FakeSession())
    monkeypatch.setattr(cm, "CATMAID_CONFIG_TTL", 0.0)
    monkeypatch.setattr(cm, "_config_cache", {"fetched": 0.0, "data": None})
    assert cm.get_catmaid_config()["instances"] == [{"id": "x"}]
    assert cm.get_catmaid_config()["instances"] == [{"id": "x"}]
    assert len(fetches) == 1                     # one fetch per process
    cm.get_catmaid_config(force_refresh=True)
    assert len(fetches) == 2


@pytest.mark.integration
def test_live_aligned_swc_on_fafb():
    fafb = cm.catmaid("fafb")
    envelope = fafb.swc(id="VFB_0010009u", aligned=True)
    assert envelope["aligned"] is True
    assert envelope["template"]["short_form"] == "VFB_00101567"  # JRC2018U
    assert envelope["result"].lstrip().startswith("#")
    original = fafb.swc(id="VFB_0010009u", raw=True)
    assert original[:200] != envelope["result"][:200]   # different space


# ---------------------------------------------------------------------------
# swc_alignments
# ---------------------------------------------------------------------------

def test_swc_alignments_lists_original_plus_vfb(monkeypatch, fake_instance):
    fafb, _ = fake_instance
    monkeypatch.setattr(cm, "list_aligned_templates", lambda vfb_id: [
        {"template": "VFB_1", "label": "JRC2018Unisex",
         "folder": "http://x/a/"}])

    class FakeSession:
        def head(self, url, **kw):
            assert url == "https://x/a/volume.swc"
            return _FakeResp()

    monkeypatch.setattr(cm, "_http_session", lambda: FakeSession())
    envelope = fafb.swc_alignments(id="VFB_0010000a")
    rows = envelope["result"]["alignments"]
    assert rows[0]["aligned"] == "original"
    assert rows[0]["source"] == "catmaid" and rows[0]["swc_available"]
    assert rows[1]["aligned"] == "VFB_1" and rows[1]["source"] == "vfb"
    assert rows[1]["swc_available"] is True
    assert envelope["result"]["skid"] == "100"      # from the fake xref map
    assert envelope["id_map"] == {"VFB_0010000a": "100"}


def test_swc_alignments_skid_without_vfb_record(monkeypatch, fake_instance):
    fafb, _ = fake_instance
    monkeypatch.setattr(cm, "skids_to_vfb_ids", lambda skids, site: {})
    envelope = fafb.swc_alignments(id="555")
    rows = envelope["result"]["alignments"]
    assert [r["aligned"] for r in rows] == ["original"]
    assert envelope["result"]["vfb_id"] is None
    assert any("no VFB record" in n for n in envelope["notes"])


def test_swc_alignments_marks_missing_store_files(monkeypatch, fake_instance):
    fafb, _ = fake_instance
    monkeypatch.setattr(cm, "list_aligned_templates", lambda vfb_id: [
        {"template": "VFB_1", "label": "A", "folder": "http://x/a/"}])

    class FakeSession:
        def head(self, url, **kw):
            return _FakeResp(status_code=404)

    monkeypatch.setattr(cm, "_http_session", lambda: FakeSession())
    rows = fafb.swc_alignments(id="VFB_0010000a", raw=True)["alignments"]
    assert rows[1]["swc_available"] is False


def test_swc_alignments_input_validation(fake_instance):
    fafb, _ = fake_instance
    with pytest.raises(ValueError, match="takes only id="):
        fafb.swc_alignments(id="555", nonsense=1)
    with pytest.raises(ValueError, match="exactly one id"):
        fafb.swc_alignments(id="1,2")


@pytest.mark.integration
def test_live_swc_alignments_on_fafb():
    fafb = cm.catmaid("fafb")
    envelope = fafb.swc_alignments(id="VFB_0010009u")
    rows = envelope["result"]["alignments"]
    assert rows[0]["aligned"] == "original"
    vfb_rows = [r for r in rows if r["source"] == "vfb"]
    assert any(r["template"] == "VFB_00101567" and r["swc_available"]
               for r in vfb_rows)                     # JRC2018U copy exists
    assert envelope["result"]["skid"] == "13146"
