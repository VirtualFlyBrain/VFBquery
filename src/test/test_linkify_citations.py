"""Unit tests for _linkify_citations (definition/description citation linking).

Regression guard for the dropped-`)` bug: the linkifier's `\\)?` used to consume
the closing paren of a `(Author, 2020)` citation without putting it back, so
definitions rendered as `(Author, 2020.` — see the LPT-neuron description. Pure,
offline tests (no backend).
"""
import re
import unittest

from vfbquery.vfb_queries import _linkify_citations

PUB_MAP = {
    "Wei et al., 2020": "FBrf_WEI",
    "Nern et al., 2025": "FBrf_NERN",
    "Ito and Awasaki, 2015": "FBrf_ITO",
}


def _displayed(markdown):
    """Strip `[label](id)` markdown to the label, i.e. what a reader sees."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", markdown)


class LinkifyCitationsTest(unittest.TestCase):

    def test_parenthesised_citation_keeps_its_closing_paren(self):
        out = _linkify_citations("It is cholinergic (Wei et al., 2020).", PUB_MAP)
        self.assertEqual(_displayed(out), "It is cholinergic (Wei et al., 2020).")
        self.assertIn("[Wei et al., 2020](FBrf_WEI)", out)

    def test_author_year_paren_form_is_normalised(self):
        # "Author (2020)" -> the citation's own parens are folded into the link.
        out = _linkify_citations("as shown by Wei et al. (2020) here.", PUB_MAP)
        self.assertIn("[Wei et al., 2020](FBrf_WEI)", out)
        self.assertEqual(_displayed(out), "as shown by Wei et al., 2020 here.")

    def test_multiple_citations_in_one_paren_group(self):
        out = _linkify_citations("mixed synapses (Wei et al., 2020; Nern et al., 2025).", PUB_MAP)
        self.assertEqual(
            _displayed(out),
            "mixed synapses (Wei et al., 2020; Nern et al., 2025).")
        self.assertIn("[Wei et al., 2020](FBrf_WEI)", out)
        self.assertIn("[Nern et al., 2025](FBrf_NERN)", out)

    def test_non_citation_parentheticals_untouched(self):
        text = "innervates the lobula plate (LOP) layers 1 and 3 (IPS)."
        self.assertEqual(_linkify_citations(text, PUB_MAP), text)

    def test_already_linked_citation_not_double_wrapped(self):
        text = "see [Wei et al., 2020](FBrf_WEI) for detail."
        self.assertEqual(_linkify_citations(text, PUB_MAP), text)

    def test_trailing_citation_at_end_of_text(self):
        out = _linkify_citations("one per hemisphere (Wei et al., 2020)", PUB_MAP)
        self.assertEqual(_displayed(out), "one per hemisphere (Wei et al., 2020)")

    def test_the_full_lpt_description_loses_no_parens(self):
        # The description from the reported screenshot (abbreviated), every
        # citation parenthesised — none should lose its ')'.
        text = ("posterior slope (IPS) (Wei et al., 2020). Its ventral branch has "
                "mixed pre- and post-synapses (Wei et al., 2020; Nern et al., 2025). "
                "It innervates around 30 columns (Nern et al., 2025). It is "
                "cholinergic (Wei et al., 2020). There is one per hemisphere "
                "(Nern et al., 2025).")
        disp = _displayed(_linkify_citations(text, PUB_MAP))
        self.assertEqual(disp, text)
        self.assertEqual(disp.count("("), disp.count(")"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
