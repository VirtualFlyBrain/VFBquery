"""Unit tests for the link-preview page (get_preview / get_preview_image)."""

import html
import re

import pytest

from vfbquery import link_preview


def _neuron():
    return {
        "Id": "VFB_jrchjrch",
        "Name": "5-HTPLP01_R",
        "IsIndividual": True,
        "IsClass": False,
        "Meta": {
            "Description": "",
            "Comment": "tracing status-Roughly traced, cropped-False",
            "Types": "[adult glutamatergic neuron](FBbt_00058220);[adult serotonergic PLP neuron](FBbt_00110925)",
        },
        "Technique": ["Hemibrain-Reconstruction"],
        "Tags": ["Adult", "Nervous_system"],
        "Images": {
            "VFB_00101567": [
                {"id": "VFB_00101384", "thumbnail": "https://www.virtualflybrain.org/data/VFB/i/jrch/jrch/VFB_00101384/thumbnail.png"},
                {"id": "VFB_00101385", "thumbnail": "https://x/second.png"},
            ]
        },
    }


def _class_with_example():
    return {
        "Id": "FBbt_00003748",
        "Name": "medulla",
        "IsClass": True,
        "IsIndividual": False,
        "Meta": {"Description": "The second optic neuropil, [see](FBbt_00003701) *the* lobula."},
        "Images": {},
        "Examples": {"VFB_00017894": [{"id": "VFB_00030624", "thumbnail": "https://x/medulla.png"}]},
    }


# --- id validation -----------------------------------------------------------

@pytest.mark.parametrize("value", [
    # underscored ontology ids
    "FBbt_00003748", "VFB_jrchjrch", "VFBexp_FBtp0000001", "GO_0001872",
    "GENO_0000346", "FBdv_00007133", "FBbi_00000537",
    # FlyBase ids -- no underscore at all
    "FBgn0038978", "FBtp0106402", "FBti0004391", "FBrf0247641", "FBal0331598",
    # dataset / publication names
    "Court2017", "Chiang2010", "Robie2017",
])
def test_is_term_id_accepts_every_shape_get_term_info_resolves(value):
    assert link_preview.is_term_id(value)


@pytest.mark.parametrize("value", [
    "", None, "<script>", "../x", "VFB jrch", "_leading", "x",
    # FlyBase links VFB thumbnails by label rather than id; that must not be
    # mistaken for a term.
    "P{VT057232-GAL4} expression pattern in adult VNS on Virtual Fly Brain",
    "VFB_00101384/thumbnail.png",
])
def test_is_term_id_rejects_junk(value):
    assert not link_preview.is_term_id(value)


# --- text helpers (mirror pageMetadata.js) -----------------------------------

def test_strip_markdown_keeps_link_labels_and_collapses_space():
    assert link_preview.strip_markdown("[medulla](FBbt_1) is *big*   and `odd`") == "medulla is big and odd"


def test_truncate_breaks_on_a_word_and_adds_ellipsis():
    out = link_preview.truncate("word " * 100, 50)
    assert len(out) <= 50
    assert out.endswith("…")
    assert not out[:-1].endswith(" ")


def test_truncate_leaves_short_text_alone():
    assert link_preview.truncate("short", 50) == "short"


# --- thumbnail selection -----------------------------------------------------

def test_first_thumbnail_prefers_images_over_examples():
    info = _neuron()
    info["Examples"] = {"T": [{"thumbnail": "https://x/example.png"}]}
    assert link_preview.first_thumbnail(info).endswith("VFB_00101384/thumbnail.png")


def test_first_thumbnail_falls_back_to_examples_for_a_class():
    assert link_preview.first_thumbnail(_class_with_example()) == "https://x/medulla.png"


def test_first_thumbnail_none_when_nothing_has_one():
    assert link_preview.first_thumbnail({"Images": {"T": [{"id": "x"}]}, "Examples": {}}) is None


# --- title / description -----------------------------------------------------

def test_title_has_name_id_and_site():
    assert link_preview.build_title(_neuron()) == "5-HTPLP01_R [VFB_jrchjrch] - Virtual Fly Brain"


def test_description_for_individual_without_description_uses_types_comment_technique():
    d = link_preview.build_description(_neuron())
    assert d.startswith("5-HTPLP01_R is an instance of adult glutamatergic neuron, adult serotonergic PLP neuron.")
    assert "tracing status-Roughly traced, cropped-False." in d
    assert "Imaged by Hemibrain-Reconstruction." in d
    assert d.endswith("for this image on Virtual Fly Brain.")


def test_description_for_class_uses_description_only():
    d = link_preview.build_description(_class_with_example())
    assert d == "The second optic neuropil, see the lobula."


def test_description_never_exceeds_limit():
    info = _class_with_example()
    info["Meta"]["Description"] = "long words " * 100
    assert len(link_preview.build_description(info)) <= link_preview.MAX_DESCRIPTION


# --- metadata / page ---------------------------------------------------------

def test_metadata_urls_are_reports_canonical_and_viewer_target():
    m = link_preview.preview_metadata(_neuron())
    assert m["url"] == "https://virtualflybrain.org/reports/VFB_jrchjrch"
    assert m["viewer_url"] == "https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_jrchjrch"
    assert m["image"].endswith("VFB_00101384/thumbnail.png")


def test_metadata_image_defaults_to_logo():
    info = _class_with_example()
    info["Examples"] = {}
    assert link_preview.preview_metadata(info)["image"] == link_preview.DEFAULT_IMAGE


def _tags(page):
    return dict(re.findall(r'<meta (?:property|name)="([^"]+)" content="([^"]*)"', page))


def test_page_carries_every_tag_an_unfurler_reads():
    page = link_preview.render_preview_html(_neuron())
    tags = _tags(page)
    for key in ("og:title", "og:description", "og:url", "og:image", "twitter:card", "twitter:image", "description"):
        assert key in tags, key
    assert tags["twitter:card"] == "summary_large_image"
    assert tags["og:image"] == tags["twitter:image"]
    assert 'rel="canonical" href="https://virtualflybrain.org/reports/VFB_jrchjrch"' in page
    assert 'http-equiv="refresh" content="0; url=https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=VFB_jrchjrch"' in page


def test_page_qualifies_for_pinterest_article_rich_pin():
    # Pinterest's Rich Pin validator requires og:type to be exactly "article"
    # or "blog" -- "website" (what this used to send) is never eligible, so
    # every VFB term page silently failed Pinterest's Rich Pin check even
    # though the ordinary og:/twitter: preview worked fine everywhere else.
    # og:site_name is "strongly suggested" by the same docs and was already
    # present; article:section is optional but free to provide here.
    page = link_preview.render_preview_html(_neuron())
    tags = _tags(page)
    assert tags["og:type"] == "article"
    assert tags["og:site_name"] == link_preview.SITE_NAME
    assert "article:section" in tags


def test_page_escapes_hostile_ontology_text():
    info = _class_with_example()
    info["Name"] = 'x"><script>alert(1)</script>'
    info["Meta"]["Description"] = "a & b < c"
    page = link_preview.render_preview_html(info)
    assert "<script>alert" not in page
    assert html.escape(info["Name"], quote=True) in page
    assert "a &amp; b &lt; c" in page
