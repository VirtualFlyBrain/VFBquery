import importlib.util
import os
import sys
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def _load():
    # vfb_queries imports the whole package; load only what this test needs
    spec = importlib.util.spec_from_file_location("vfb_queries_src", os.path.join(HERE, "..", "vfbquery", "vfb_queries.py"))
    src = open(spec.origin).read()
    ns = {}
    start = src.index("OWLERY_BACKED_FUNCTIONS = frozenset(")
    end = src.index("def term_info_parse_object(")
    exec(src[start:end], ns)
    return ns


class Q:
    def __init__(self, query, function):
        self.query, self.function = query, function


class TestDeprecatedTermQueries(unittest.TestCase):

    def setUp(self):
        ns = _load()
        self.drop = ns["drop_owlery_queries_if_deprecated"]
        self.owlery = ns["OWLERY_BACKED_FUNCTIONS"]

    def test_owlery_queries_removed_on_deprecated_term(self):
        qs = [Q("PartsOf", "get_parts_of"), Q("SubclassesOf", "get_subclasses_of"),
              Q("UpstreamClassConnectivity", "get_class_upstream"), Q("anatScRNAseqQuery", "get_anatomy_scrnaseq")]
        kept = self.drop(qs, ["Entity", "Class", "Anatomy", "Deprecated"])
        self.assertEqual(["UpstreamClassConnectivity"], [q.query for q in kept])

    def test_live_term_untouched(self):
        qs = [Q("PartsOf", "get_parts_of"), Q("SubclassesOf", "get_subclasses_of")]
        self.assertEqual(qs, self.drop(qs, ["Entity", "Class", "Anatomy"]))
        self.assertEqual(qs, self.drop(qs, None))

    def test_set_matches_owlery_callers(self):
        # every run_query function that reaches Owlery must be in the set, and vice versa
        import re
        src = open(os.path.join(HERE, "..", "vfbquery", "vfb_queries.py")).read()
        callers = set()
        for chunk in re.split(r"\n(?=def )", src):
            m = re.match(r"def (get_\w+)\(", chunk)
            if m and re.search(r"oc\.get_subclasses|oc\.get_instances|_owlery_query_to_results\(|_owlery_ids_cached\(", chunk):
                callers.add(m.group(1))
        callers -= {"get_dict_cursor"}
        self.assertEqual(callers, set(self.owlery))


if __name__ == "__main__":
    unittest.main()
