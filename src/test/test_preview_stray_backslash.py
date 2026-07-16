import unittest

import pandas as pd

from vfbquery.vfb_queries import encode_markdown_links


class PreviewStrayBackslashTest(unittest.TestCase):
    """Query preview rows are assembled in vfb_queries.py from raw Neo4j labels
    (via apoc.text.format), NOT through term_info_queries.clean_label. So the
    stray backslash-before-quote artifact that PR #80 stripped from a term's own
    labels still reached the ``name`` / ``thumbnail`` markdown cells of query
    previews when an embedded neuron label contained an apostrophe (e.g. the
    NBLAST 'similar neurons' preview showing ``MBON01(y5B\\'2a)_R``).

    encode_markdown_links is the shared 'prepare a markdown cell for display'
    pass for those columns, so the escape stripping lives there. These tests are
    network-free: they exercise the encoder directly on production-shaped
    (object-dtype) frames.
    """

    def _obj_df(self, data):
        # Match the dtype the live pipeline produces (pd.DataFrame.from_records
        # of dict rows yields object columns). A str/StringDtype column would be
        # skipped by the encoder's ``dtype != object`` guard.
        return pd.DataFrame({k: pd.Series(v, dtype=object) for k, v in data.items()})

    def test_link_cell_stray_backslash_stripped(self):
        raw = "[MBON01(y5B\\'2a)_R (FlyEM-HB:612371421)](VFB_jrchk0e2)"
        df = self._obj_df({"name": [raw]})
        out = encode_markdown_links(df, ["name"])
        val = out["name"].iloc[0]
        self.assertNotIn("\\", val)
        self.assertEqual(
            "[MBON01(y5B'2a)_R (FlyEM-HB:612371421)](VFB_jrchk0e2)", val
        )

    def test_image_cell_stray_backslash_stripped(self):
        # https URL (as produced by the Cypher REPLACE) so the only thing that
        # should change is the removal of the stray backslashes in alt + title.
        raw = (
            "[![MBON01(y5B\\'2a)_R aligned to JRCFIB2018Fum]"
            "(https://www.virtualflybrain.org/data/x/thumbnail.png "
            "'MBON01(y5B\\'2a)_R aligned to JRCFIB2018Fum')](t,VFB_jrchk0e2)"
        )
        df = self._obj_df({"thumbnail": [raw]})
        out = encode_markdown_links(df, ["thumbnail"])
        val = out["thumbnail"].iloc[0]
        self.assertNotIn("\\", val)
        self.assertIn("MBON01(y5B'2a)_R", val)

    def test_clean_cells_untouched(self):
        raw = "[MBON01_L](VFB_00000001)"
        df = self._obj_df({"name": [raw]})
        out = encode_markdown_links(df, ["name"])
        self.assertEqual(raw, out["name"].iloc[0])

    def test_null_cells_preserved(self):
        df = self._obj_df({"name": [None, "[a\\'b](x)"]})
        out = encode_markdown_links(df, ["name"])
        self.assertTrue(pd.isna(out["name"].iloc[0]))
        self.assertNotIn("\\", out["name"].iloc[1])


if __name__ == "__main__":
    unittest.main()
