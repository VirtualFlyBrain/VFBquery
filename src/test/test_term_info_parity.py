"""
Term-info parity + robustness tests for the VFBquery -> term-info migration.

Covers the three serialiser gaps reconciled between ``term_info_parse_object``
(``vfb_queries.py``) and the canonical dataclass serialiser
(``term_info_queries.py``), plus the License-term robustness fix:

  A. Class definition references (``def_pubs``) must reach ``Publications``.
  B. Individual-term synonyms (``pub_syn``) must reach ``Synonyms``
     (previously gated Class-only).
  C. Publication-term external content (``pub_specific_content``) must reach
     ``Publications`` -- the SOLR SuperType marker is the lowercase ``pub``.
  D. ``get_term_info`` must not 5xx / hang on any SuperType -- the License
     individual is the regression case (cold-miss cache write must be
     non-blocking).

The parity checks run against ``term_info_parse_object`` on the raw SOLR
``term_info`` doc (a read-only fetch, no per-query count calls), so they are
fast and deterministic. Caching is disabled for the whole module so nothing is
written back to the shared production cache.
"""

import os
os.environ.setdefault("VFBQUERY_CACHE_ENABLED", "false")

import unittest
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vfbquery import vfb_queries as q
from vfbquery.cached_functions import is_valid_term_info_result


class _Results:
    """Minimal stand-in for a pysolr result object."""
    def __init__(self, docs):
        self.docs = docs
        self.hits = len(docs)


def _raw(short_form):
    """Fetch the raw SOLR doc(s) for a term (read-only) and wrap them."""
    return _Results(q.vfb_solr.search('id:' + short_form).docs)


def _fixture_raw(name):
    """Wrap a committed complete term_info fixture as a SOLR-style result, so the
    render code can be tested without live SOLR content. See TESTING.md
    'Fixture vs live (data_health)'."""
    path = os.path.join(os.path.dirname(__file__),
                        "fixtures", "term_info", name + ".json")
    with open(path, encoding="utf-8") as f:
        return _Results([{"term_info": [json.dumps(json.load(f))]}])


class TermInfoParityTest(unittest.TestCase):

    def _parse(self, short_form):
        ti = q.term_info_parse_object(_raw(short_form), short_form)
        self.assertIsNotNone(ti, f"parse returned None for {short_form}")
        return ti

    def _parse_fixture(self, name):
        """Parse a committed complete fixture through the render code — the
        deterministic, PR-blocking counterpart of :meth:`_parse`. See TESTING.md
        'Fixture vs live (data_health)'."""
        results = _fixture_raw(name)
        sf = json.loads(results.docs[0]["term_info"][0])["term"]["core"]["short_form"]
        ti = q.term_info_parse_object(results, sf)
        self.assertIsNotNone(ti, f"parse returned None for fixture {name}")
        return ti

    # --- Gap A: class definition references (def_pubs) -> inline in description
    # The legacy panel appends def_pubs as microref links to the definition
    # (VFBProcessTermInfoCachedJson.java:937), so parity is an inline render in
    # Meta.Description, not a separate Publications entry.
    def test_class_def_pubs_inline_in_description(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_class_def_pubs_inline_in_description(
            self._parse_fixture("class_FBbt_00003748_medulla"))

    @pytest.mark.data_health
    def test_class_def_pubs_inline_in_description_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_class_def_pubs_inline_in_description(self._parse("FBbt_00003748"))

    def _check_class_def_pubs_inline_in_description(self, ti):
        desc = ti.get("Meta", {}).get("Description", "")
        self.assertIn("FBrf0231227", desc, "def_pub FBrf0231227 missing from description")
        self.assertIn("FBrf0224194", desc, "def_pub FBrf0224194 missing from description")

    def test_kenyon_def_pubs_all_inline(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_kenyon_def_pubs_all_inline(
            self._parse_fixture("class_FBbt_00003686_kenyon"))

    @pytest.mark.data_health
    def test_kenyon_def_pubs_all_inline_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_kenyon_def_pubs_all_inline(self._parse("FBbt_00003686"))

    def _check_kenyon_def_pubs_all_inline(self, ti):
        desc = ti.get("Meta", {}).get("Description", "")
        for ref in ("FBrf0092568", "FBrf0214059", "FBrf0205263"):
            self.assertIn(ref, desc, f"def_pub {ref} missing from description")

    # --- Gap B: Individual synonyms (pub_syn) -> Synonyms -------------------
    def test_individual_synonyms_present(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_individual_synonyms_present(
            self._parse_fixture("individual_VFB_00101385_MEon"))

    @pytest.mark.data_health
    def test_individual_synonyms_present_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_individual_synonyms_present(self._parse("VFB_00101385"))

    def _check_individual_synonyms_present(self, ti):
        labels = {s.get("label") for s in ti.get("Synonyms", [])}
        self.assertIn("MEon JRC_FlyEM_Hemibrain", labels,
                      "Individual pub_syn dropped from Synonyms")

    def test_class_synonyms_not_regressed(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_class_synonyms_not_regressed(
            self._parse_fixture("gene_FBgn0010339_128up"))

    @pytest.mark.data_health
    def test_class_synonyms_not_regressed_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_class_synonyms_not_regressed(self._parse("FBgn0010339"))

    def _check_class_synonyms_not_regressed(self, ti):
        self.assertGreaterEqual(len(ti.get("Synonyms", [])), 7,
                                "class synonyms regressed")

    # --- Gap C: publication external content (pub_specific_content) ---------
    def test_publication_external_content_present(self):
        self._check_pub_external_content(
            q.term_info_parse_object(_fixture_raw("pub_FBrf0242477"), "FBrf0242477"))

    @pytest.mark.data_health
    def test_publication_external_content_present_live(self):
        """Data-health (scheduled only): the same parity check against the live SOLR document, so
        an incomplete production pub document is caught. Deselected on PRs via
        ``-m 'not data_health'``."""
        self._check_pub_external_content(self._parse("FBrf0242477"))

    def _check_pub_external_content(self, ti):
        pubs = ti.get("Publications", [])
        self.assertTrue(pubs, "pub_specific_content dropped: Publications empty")
        pub = pubs[0]
        self.assertTrue(pub.get("title"), "pub title missing")
        refs = " ".join(pub.get("refs", []))
        self.assertIn("31112130", refs, "PubMed id missing")
        self.assertIn("FBrf0242477", refs, "FlyBase ref missing")
        self.assertIn("10.7554/eLife.43079", refs, "DOI missing")

    # --- Coverage: external xref links (genes, anatomy) --------------------
    def test_xrefs_surface_as_links(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_xrefs_surface_as_links(
            self._parse_fixture("class_FBbt_00003748_medulla"))

    @pytest.mark.data_health
    def test_xrefs_surface_as_links_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_xrefs_surface_as_links(self._parse("FBbt_00003748"))

    def _check_xrefs_surface_as_links(self, ti):
        xr = ti.get("Xrefs") or []
        self.assertTrue(xr, "Xrefs dropped for medulla")
        ibdb = [x for x in xr if x.get("label") == "Insect Brain DB"]
        self.assertTrue(ibdb, "Insect Brain DB xref missing")
        self.assertIn("insectbraindb.org/app/structures/38", ibdb[0].get("link", ""))

    def test_gene_xref_flybase(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_gene_xref_flybase(self._parse_fixture("gene_FBgn0051882"))

    @pytest.mark.data_health
    def test_gene_xref_flybase_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_gene_xref_flybase(self._parse("FBgn0051882"))

    def _check_gene_xref_flybase(self, ti):
        links = " ".join(x.get("link", "") for x in (ti.get("Xrefs") or []))
        self.assertIn("flybase.org/reports/FBgn0051882", links, "gene FlyBase xref missing")

    # --- Coverage: related_individuals -------------------------------------
    # NB `related_individuals` is a MISNOMER: it is populated only from the
    # `term_replaced_by` edge, so it is really the replacement pointer of a
    # *deprecated* term (target is usually a Class, not an Individual). A
    # deprecated term is therefore REQUIRED to exercise this path — hence the
    # obsolete FBbt_00000058, which was replaced by FBbt_00000057. See the
    # field/render notes in term_info_queries.py / vfb_queries.py. Do not "fix"
    # this to a current term: it would render nothing and the test would break.
    def test_related_individuals_surface(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_related_individuals_surface(
            self._parse_fixture("class_FBbt_00000058_related_individuals"))

    @pytest.mark.data_health
    def test_related_individuals_surface_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_related_individuals_surface(self._parse("FBbt_00000058"))

    def _check_related_individuals_surface(self, ti):
        ri = ti.get("Meta", {}).get("RelatedIndividuals", "")
        self.assertTrue(ri, "related_individuals dropped")
        self.assertIn("FBbt_00000057", ri, "term_replaced_by target id missing")

    # --- Coverage: DataSet external link -----------------------------------
    def test_dataset_link_present(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_dataset_link_present(self._parse_fixture("dataset_Ito2013"))

    @pytest.mark.data_health
    def test_dataset_link_present_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_dataset_link_present(self._parse("Ito2013"))

    def _check_dataset_link_present(self, ti):
        link = ti.get("Meta", {}).get("Link", "")
        self.assertIn("flybase.org/reports/FBrf0221438", link, "DataSet link dropped")

    # --- Targeting queries (splits<->neurons) as live query types ----------
    def test_neuron_class_offers_splits_targeting(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_neuron_class_offers_splits_targeting(
            self._parse_fixture("neuron_class_FBbt_00100243_MBON"))

    @pytest.mark.data_health
    def test_neuron_class_offers_splits_targeting_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_neuron_class_offers_splits_targeting(self._parse("FBbt_00100243"))

    def _check_neuron_class_offers_splits_targeting(self, ti):
        self.assertTrue(any(x.get("query") == "SplitsTargeting" for x in ti.get("Queries", [])),
                        "SplitsTargeting not offered on neuron class")

    def test_split_class_offers_target_neurons(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_split_class_offers_target_neurons(
            self._parse_fixture("split_VFBexp_FBtp0129935FBtp0129968"))

    @pytest.mark.data_health
    def test_split_class_offers_target_neurons_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_split_class_offers_target_neurons(
            self._parse("VFBexp_FBtp0129935FBtp0129968"))

    def _check_split_class_offers_target_neurons(self, ti):
        self.assertTrue(any(x.get("query") == "TargetNeurons" for x in ti.get("Queries", [])),
                        "TargetNeurons not offered on split class")

    def test_splits_targeting_returns_count_and_rows(self):
        r = q.get_splits_targeting("FBbt_00100243", return_dataframe=False, limit=5)
        self.assertIsInstance(r, dict)
        self.assertGreater(r.get("count", 0), 0, "expected splits targeting MBON")
        self.assertTrue(r.get("rows"), "no preview rows")
        self.assertTrue(all(k in r["rows"][0]
                            for k in ("id", "label", "tags", "template", "technique", "thumbnail")))
        # Template_Space / Imaging_Technique columns must actually be populated
        # (the query declares them; they were previously always blank).
        self.assertTrue(any(row.get("template") for row in r["rows"]),
                        "Template column empty for all splits")
        self.assertTrue(any(row.get("technique") for row in r["rows"]),
                        "Imaging Technique column empty for all splits")

    def test_neurons_targeted_by_split_returns_count(self):
        r = q.get_neurons_targeted_by_split("VFBexp_FBtp0129935FBtp0129968", return_dataframe=False, limit=5)
        self.assertGreater(r.get("count", 0), 0, "expected neurons targeted by split")

    # --- Gap D: License term must not 5xx / return None --------------------
    def test_license_term_info_does_not_5xx(self):
        # preview=False avoids the per-query count calls; License has no
        # queries anyway. The point is that a valid dict comes back rather
        # than None or a raised exception.
        result = q.get_term_info("VFBlicense_CC_BY_SA_4_0", preview=False)
        self.assertIsInstance(result, dict, "License term_info did not return a dict")
        self.assertTrue(is_valid_term_info_result(result),
                        "License term_info failed validity check")
        self.assertIn("License", result.get("SuperTypes", []))

    # --- Gap E: a term's own licence (`license`) must reach Licenses{} -----
    # DataSet term info returns has_license on the term itself as `license`
    # (QueryLibrary.dataset_term_info), not as `dataset_license`. The
    # serialiser only read `dataset_license`, so every dataset page rendered
    # without a License row even though the edge was in the KB.
    def test_dataset_own_license_reaches_licenses(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_dataset_own_license_reaches_licenses(
            self._parse_fixture("dataset_Cachero2010"))

    @pytest.mark.data_health
    def test_dataset_own_license_reaches_licenses_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_dataset_own_license_reaches_licenses(self._parse("Cachero2010"))

    def _check_dataset_own_license_reaches_licenses(self, ti):
        licenses = ti.get("Licenses", {})
        self.assertTrue(licenses, "DataSet own licence dropped from Licenses{}")
        lic = licenses[0]
        self.assertTrue(lic.get("short_form", "").startswith("VFBlicense"),
                        f"unexpected licence short_form: {lic.get('short_form')}")
        self.assertTrue(lic.get("label"), "licence label missing")
        self.assertTrue(lic.get("iri"), "licence iri missing")

    def test_dataset_own_license_has_no_self_source(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_dataset_own_license_has_no_self_source(
            self._parse_fixture("dataset_Cachero2010"))

    @pytest.mark.data_health
    def test_dataset_own_license_has_no_self_source_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_dataset_own_license_has_no_self_source(self._parse("Cachero2010"))

    def _check_dataset_own_license_has_no_self_source(self, ti):
        # The dataset is its own source, so leave source empty rather than
        # rendering a Source row that links back to the same page.
        lic = ti.get("Licenses", {})[0]
        self.assertEqual("", lic.get("source", ""))
        self.assertEqual("", lic.get("source_iri", ""))

    def test_dataset_license_still_attributes_source_on_images(self):
        """Render code (PR-blocking): assert against a complete fixture, deterministically.
        See TESTING.md 'Fixture vs live (data_health)'."""
        self._check_dataset_license_still_attributes_source_on_images(
            self._parse_fixture("template_VFB_00101567_JRC2018U"))

    @pytest.mark.data_health
    def test_dataset_license_still_attributes_source_on_images_live(self):
        """Data-health (scheduled only): the same assertions against live SOLR."""
        self._check_dataset_license_still_attributes_source_on_images(
            self._parse("VFB_00101567"))

    def _check_dataset_license_still_attributes_source_on_images(self, ti):
        # The dataset_license path is unchanged: an image/template still gets
        # its licence via the dataset it came from, with that dataset as source.
        licenses = ti.get("Licenses", {})
        self.assertTrue(licenses, "template lost its inherited licence")
        self.assertTrue(licenses[0].get("source"), "inherited licence lost its source")


if __name__ == "__main__":
    unittest.main()
