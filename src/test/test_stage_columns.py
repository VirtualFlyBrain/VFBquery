"""Stage and tissue columns of the scRNAseq cluster and clustering tables.

Offline: `_add_stage_columns` turns the queries' raw columns into the markdown ones.
Live: the hand-built cluster tables return exactly their headers' columns; a
cluster's own stage shows; FBdv stages resolve their substage_of ancestors.
"""
import unittest

import pandas as pd

from vfbquery import vfb_queries as vfb
from .scrnaseq_fixtures import (anatomy_with_clusters, dataset_with_cluster_stage,
                                dataset_with_clusters, gene_with_clusters)

ADULT = "FBdv_00005369"
ANCESTORS = {
    "D5": {"D5": ("day 5 of adulthood", 0), ADULT: ("adult stage", 1)},
    "D30": {"D30": ("day 30 of adulthood", 0), ADULT: ("adult stage", 1)},
    "E17": {"E17": ("embryonic stage 17", 0), "FBdv_00005289": ("embryonic stage", 1)},
}
PER_CLUSTERING = {
    "CL1": ([{"short_form": "D5", "label": "day 5 of adulthood"}], [("T1", "adult head")]),
    "CL2": ([{"short_form": "D30", "label": "day 30 of adulthood"}], [("T2", "adult thorax")]),
}


class AddStageColumnsTest(unittest.TestCase):
    """`_add_stage_columns`, with the two pdb lookups stubbed."""

    def setUp(self):
        self._saved = vfb._stage_ancestors, vfb._clustering_samples_stage_tissue
        vfb._stage_ancestors = lambda ids: {i: ANCESTORS[i] for i in ids if i in ANCESTORS}
        vfb._clustering_samples_stage_tissue = lambda cls: {c: PER_CLUSTERING[c] for c in cls if c in PER_CLUSTERING}

    def tearDown(self):
        vfb._stage_ancestors, vfb._clustering_samples_stage_tissue = self._saved

    def test_raw_columns_become_markdown_columns(self):
        df = pd.DataFrame({
            "id": ["a", "b", "c"],
            "cluster_stage_raw": [[{"short_form": "E17", "label": "embryonic stage 17"}], [], []],
            "clusterings_raw": [["CL1"], ["CL1", "CL2"], []],
        })
        out = vfb._add_stage_columns(df)
        self.assertNotIn("cluster_stage_raw", out.columns)
        self.assertNotIn("clusterings_raw", out.columns)
        self.assertEqual(list(out["cluster_stage"]), ["[embryonic stage 17](E17)", "", ""])
        # one Clustering: its Samples' stage as is; two: the union, collapsed
        self.assertEqual(list(out["sample_stages"]),
                         ["[day 5 of adulthood](D5)", f"[adult stage]({ADULT})", ""])
        self.assertEqual(list(out["sample_tissues"]),
                         ["[adult head](T1)", "[adult head](T1), [adult thorax](T2)", ""])

    def test_clustering_rows_without_a_cluster_stage(self):
        df = pd.DataFrame({"id": ["CL2"], "clusterings_raw": [["CL2"]]})
        out = vfb._add_stage_columns(df)
        self.assertEqual(list(out.columns), ["id", "sample_stages", "sample_tissues"])
        self.assertEqual(out["sample_stages"][0], "[day 30 of adulthood](D30)")

    def test_empty_and_raw_free_tables_unchanged(self):
        empty = pd.DataFrame()
        self.assertTrue(vfb._add_stage_columns(empty).empty)
        plain = pd.DataFrame({"id": ["x"], "name": ["y"]})
        self.assertEqual(list(vfb._add_stage_columns(plain).columns), ["id", "name"])


class LiveStageColumnsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ANATOMY_ID = anatomy_with_clusters("FBbt_00003686")   # Kenyon cell
        cls.GENE_ID = gene_with_clusters("FBgn0000490")            # dpp
        cls.DATASET_ID = dataset_with_clusters("VFBseq_00001468")
        cls.STAGED_DATASET_ID = dataset_with_cluster_stage("VFBseq_00002863")   # Calderon 2022

    def test_rows_match_headers(self):
        # these three build their rows by hand: a header the Cypher doesn't return
        # would fail here, not on the site
        for func, arg in [("get_anatomy_scrnaseq", self.ANATOMY_ID),
                          ("get_expression_cluster", self.GENE_ID),
                          ("get_scrnaseq_dataset_data", self.DATASET_ID)]:
            with self.subTest(func=func):
                result = getattr(vfb, func)(arg, return_dataframe=False, limit=5)
                self.assertTrue(result["rows"], f"{func}({arg}) found nothing")
                for col in vfb._STAGE_COLUMNS:
                    self.assertIn(col, result["headers"])
                for row in result["rows"]:
                    self.assertEqual(set(row), set(result["headers"]))

    def test_cluster_own_stage_shows(self):
        result = vfb.get_scrnaseq_dataset_data(self.STAGED_DATASET_ID, return_dataframe=False)
        staged = [r for r in result["rows"] if r["cluster_stage"]]
        self.assertTrue(staged, f"no cluster stage shown for {self.STAGED_DATASET_ID}")
        self.assertTrue(all("FBdv_" in r["cluster_stage"] for r in staged))
        self.assertTrue(all(r["sample_stages"] for r in staged))

    def test_fbdv_ancestors_resolve(self):
        # day 5 of adulthood -> adult stage along substage_of (by edge type: a
        # relabelled substage_of would empty this and stop stages collapsing)
        anc = vfb._stage_ancestors(["FBdv_00007080"])["FBdv_00007080"]
        self.assertEqual(anc["FBdv_00007080"][1], 0)
        self.assertIn(ADULT, anc)
        self.assertEqual(anc[ADULT][0], "adult stage")


if __name__ == "__main__":
    unittest.main()
