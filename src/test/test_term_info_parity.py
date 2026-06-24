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


class TermInfoParityTest(unittest.TestCase):

    def _parse(self, short_form):
        ti = q.term_info_parse_object(_raw(short_form), short_form)
        self.assertIsNotNone(ti, f"parse returned None for {short_form}")
        return ti

    # --- Gap A: class definition references (def_pubs) -> inline in description
    # The legacy panel appends def_pubs as microref links to the definition
    # (VFBProcessTermInfoCachedJson.java:937), so parity is an inline render in
    # Meta.Description, not a separate Publications entry.
    def test_class_def_pubs_inline_in_description(self):
        ti = self._parse("FBbt_00003748")  # medulla
        desc = ti.get("Meta", {}).get("Description", "")
        self.assertIn("FBrf0231227", desc, "def_pub FBrf0231227 missing from description")
        self.assertIn("FBrf0224194", desc, "def_pub FBrf0224194 missing from description")

    def test_kenyon_def_pubs_all_inline(self):
        ti = self._parse("FBbt_00003686")  # Kenyon cell
        desc = ti.get("Meta", {}).get("Description", "")
        for ref in ("FBrf0092568", "FBrf0214059", "FBrf0205263"):
            self.assertIn(ref, desc, f"def_pub {ref} missing from description")

    # --- Gap B: Individual synonyms (pub_syn) -> Synonyms -------------------
    def test_individual_synonyms_present(self):
        ti = self._parse("VFB_00101385")  # individual image (MEon)
        labels = {s.get("label") for s in ti.get("Synonyms", [])}
        self.assertIn("MEon JRC_FlyEM_Hemibrain", labels,
                      "Individual pub_syn dropped from Synonyms")

    def test_class_synonyms_not_regressed(self):
        ti = self._parse("FBgn0010339")  # gene 128up: 7 synonyms
        self.assertGreaterEqual(len(ti.get("Synonyms", [])), 7,
                                "class synonyms regressed")

    # --- Gap C: publication external content (pub_specific_content) ---------
    def test_publication_external_content_present(self):
        ti = self._parse("FBrf0242477")  # Dolan et al., 2019
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
        ti = self._parse("FBbt_00003748")  # medulla -> Insect Brain DB
        xr = ti.get("Xrefs") or []
        self.assertTrue(xr, "Xrefs dropped for medulla")
        ibdb = [x for x in xr if x.get("label") == "Insect Brain DB"]
        self.assertTrue(ibdb, "Insect Brain DB xref missing")
        self.assertIn("insectbraindb.org/app/structures/38", ibdb[0].get("link", ""))

    def test_gene_xref_flybase(self):
        ti = self._parse("FBgn0051882")  # a gene with a FlyBase xref
        links = " ".join(x.get("link", "") for x in (ti.get("Xrefs") or []))
        self.assertIn("flybase.org/reports/FBgn0051882", links, "gene FlyBase xref missing")

    # --- Coverage: related_individuals -------------------------------------
    def test_related_individuals_surface(self):
        ti = self._parse("FBbt_00000058")  # FBbt class carrying related_individuals
        ri = ti.get("Meta", {}).get("RelatedIndividuals", "")
        self.assertTrue(ri, "related_individuals dropped")
        self.assertIn("FBbt_00000057", ri, "related individual target id missing")

    # --- Coverage: DataSet external link -----------------------------------
    def test_dataset_link_present(self):
        ti = self._parse("Ito2013")
        link = ti.get("Meta", {}).get("Link", "")
        self.assertIn("flybase.org/reports/FBrf0221438", link, "DataSet link dropped")

    # --- Targeting queries (splits<->neurons) as live query types ----------
    def test_neuron_class_offers_splits_targeting(self):
        ti = self._parse("FBbt_00100243")  # MBON neuron class with split drivers
        self.assertTrue(any(x.get("query") == "SplitsTargeting" for x in ti.get("Queries", [])),
                        "SplitsTargeting not offered on neuron class")

    def test_split_class_offers_target_neurons(self):
        ti = self._parse("VFBexp_FBtp0129935FBtp0129968")  # a split class
        self.assertTrue(any(x.get("query") == "TargetNeurons" for x in ti.get("Queries", [])),
                        "TargetNeurons not offered on split class")

    def test_splits_targeting_returns_count_and_rows(self):
        r = q.get_splits_targeting("FBbt_00100243", return_dataframe=False, limit=5)
        self.assertIsInstance(r, dict)
        self.assertGreater(r.get("count", 0), 0, "expected splits targeting MBON")
        self.assertTrue(r.get("rows"), "no preview rows")
        self.assertTrue(all(k in r["rows"][0] for k in ("id", "label", "tags", "thumbnail")))

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


if __name__ == "__main__":
    unittest.main()
