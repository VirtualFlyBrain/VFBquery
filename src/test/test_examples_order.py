"""Available Images order: a template's own domain image leads."""
import unittest

from vfbquery.vfb_queries import order_template_examples


class OrderTemplateExamplesTest(unittest.TestCase):

    def test_indexed_image_first_then_newest_id(self):
        # FBbt_00003748 on JRC2018U: the painted domain VFB_00102107 has the
        # oldest id but is the only image indexed to the template.
        records = [
            {"id": "VFB_00107fo8"},
            {"id": "VFB_00102107", "index": 3},
            {"id": "VFB_001091st"},
            {"id": "VFB_00108iwp"},
        ]
        self.assertEqual(
            [r["id"] for r in order_template_examples(records)],
            ["VFB_00102107", "VFB_001091st", "VFB_00108iwp", "VFB_00107fo8"])

    def test_several_indexed_images_ascend_by_index(self):
        records = [
            {"id": "VFB_0000000a", "index": 7},
            {"id": "VFB_0000000b"},
            {"id": "VFB_0000000c", "index": 0},
            {"id": "VFB_0000000d", "index": 2},
        ]
        self.assertEqual(
            [r["id"] for r in order_template_examples(records)],
            ["VFB_0000000c", "VFB_0000000d", "VFB_0000000a", "VFB_0000000b"])

    def test_no_index_keeps_id_descending(self):
        records = [{"id": "VFB_00000001"}, {"id": "VFB_00000003"}, {"id": "VFB_00000002"}]
        self.assertEqual(
            [r["id"] for r in order_template_examples(records)],
            ["VFB_00000003", "VFB_00000002", "VFB_00000001"])


if __name__ == "__main__":
    unittest.main()
