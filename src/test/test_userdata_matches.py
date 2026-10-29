"""Offline tests for the parser behind SimilarMorphologyToUserData (no Solr, no PDB)."""
import json
import unittest

from vfbquery.vfb_queries import _userdata_matches, _VFB_UPLOAD_ID_RE


LEGACY_ROW = {"term": {"core": {"short_form": "VFB_00000001", "label": "fru-M-200266"}},
              "score": 0.73, "channel_images": [], "parents": []}


class UserDataMatchesTest(unittest.TestCase):

    def test_solr_list_of_one_legacy_string(self):
        # what Solr returns for the uploads written by the Jenkins pipeline (2023-2026)
        raw = [json.dumps({"rows": [LEGACY_ROW, dict(LEGACY_ROW, score=0.5,
                                                    term={"core": {"short_form": "VFB_00000233"}})]})]
        self.assertEqual(_userdata_matches(raw), [("VFB_00000001", 0.73), ("VFB_00000233", 0.5)])

    def test_flat_rows_string_and_dict(self):
        flat = [{"id": "VFB_jrchk0tq", "score": "0.70"}, {"id": "VFB_fw046498", "score": 0.81}]
        want = [("VFB_fw046498", 0.81), ("VFB_jrchk0tq", 0.7)]
        self.assertEqual(_userdata_matches(json.dumps(flat)), want)
        self.assertEqual(_userdata_matches([json.dumps({"rows": flat})]), want)

    def test_best_score_per_id(self):
        flat = [{"id": "VFB_jrchk0tq", "score": 0.4}, {"id": "VFB_jrchk0tq", "score": 0.6}]
        self.assertEqual(_userdata_matches(json.dumps(flat)), [("VFB_jrchk0tq", 0.6)])

    def test_rejects_unsafe_ids_and_junk(self):
        flat = [{"id": "VFB_x' OR 1=1", "score": 1}, {"id": "VFB_ok", "score": "n/a"}, "junk", None]
        self.assertEqual(_userdata_matches(json.dumps(flat)), [])
        self.assertEqual(_userdata_matches("not json"), [])
        self.assertEqual(_userdata_matches([]), [])
        self.assertEqual(_userdata_matches({"rows": []}), [])

    def test_upload_id_pattern(self):
        self.assertTrue(_VFB_UPLOAD_ID_RE.match("VFBu_8uvHb4t6"))
        self.assertTrue(_VFB_UPLOAD_ID_RE.match("VFBu_a-b_c123"))   # nanoid alphabet
        self.assertFalse(_VFB_UPLOAD_ID_RE.match("VFBu_x' OR 1=1"))
        self.assertFalse(_VFB_UPLOAD_ID_RE.match("VFB_00000001"))


if __name__ == "__main__":
    unittest.main()
