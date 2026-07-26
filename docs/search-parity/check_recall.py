"""Measure exact-label recall: if you type a term's label, do you get that term?

Why this exists separately from ``check_parity.py``: the parity harness feeds the
*same* Solr response to the JS sorter and the Python port, which is exactly what
makes it a clean ranking test — and exactly why it is blind to this bug. Nothing
here is a ranking problem. The sorter promotes exact matches correctly whenever it
is given them. The failure is upstream, in *retrieval*: a term that scores below
``rows`` never reaches the sorter at all, so no amount of comparator work can save
it. A retrieval change is therefore invisible to the parity gate and needs its own
measurement.

What it reports, per variant:

* **recall** — how many corpus labels retrieve their own term at all.
* **rank 0** — how many put it top, which is what a user actually needs.
* **churn** — how far the top 10 moves on queries that are *not* about exact
  matching. A variant that fixes ``neuron`` by reshuffling everything else has not
  fixed anything; it has traded a visible bug for an invisible one.

    python3 docs/search-parity/check_recall.py
    python3 docs/search-parity/check_recall.py --variant rows1000
"""
import argparse
import json
import random
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from vfbquery import search_config as sc     # noqa: E402

B = sc.SOLR_ONTOLOGY_URL

# Queries used only for churn: ordinary searches with no exact-label intent, so any
# movement in their top 10 is collateral damage from the variant.
CHURN_QUERIES = ["DA1 lPN", "kenyon", "MBON-a2", "lobula plate", "L1EM",
                 "dopaminergic", "PN", "glia", "adult brain", "T4"]

_ID_LIKE = ("FBbt", "FBgn", "FBal", "VFB_", "VFBexp", "CL_", "GO_", "UBERON")


def solr(params, rows):
    p = dict(params)
    p["rows"] = str(rows)
    r = requests.get(B, params=sc.params_as_pairs(p), timeout=90)
    r.raise_for_status()
    return r.json()["response"]


def build_corpus(n_per_bucket=12, seed=7):
    """Sample real labels, weighted to the short ones where the boost stops working."""
    random.seed(seed)
    # Exclude deprecated terms from the corpus. The website hard-excludes them via
    # `fq`, so they *should* be unfindable; counting them as recall misses would
    # invent a bug and then flatter any variant that appears to fix it.
    r = requests.get(B, params={"q": "facets_annotation:Class AND short_form:FBbt*"
                                     " AND NOT facets_annotation:Deprecated",
                                "defType": "lucene", "fl": "short_form,label",
                                "rows": "4000", "wt": "json"}, timeout=90)
    r.raise_for_status()
    buckets = {}
    for d in r.json()["response"]["docs"]:
        lab = d.get("label")
        # Some docs carry the short_form in `label`; those resolve via
        # shortform_autosuggest and would flatter any variant we test.
        if not lab or lab.startswith(_ID_LIKE):
            continue
        buckets.setdefault(len(lab.split()), []).append(lab)
    corpus = []
    for n in (1, 2, 3):
        pool = buckets.get(n, [])
        corpus += random.sample(pool, min(n_per_bucket, len(pool)))
    # The cases already known to be interesting, kept in deliberately.
    corpus += ["neuron", "medulla", "Kenyon cell", "mushroom body",
               "antennal lobe", "fan-shaped body", "adult brain"]
    return list(dict.fromkeys(corpus))


# --------------------------------------------------------------------------- #
# Variants. Each returns (ranked_rows, n_solr_requests).
# --------------------------------------------------------------------------- #

def variant_baseline(query, rows=sc.DEFAULT_ROWS):
    """Current shipped behaviour."""
    docs = solr(sc.build_params(query, rows=rows), rows)["docs"]
    return sc.sort_results(sc.refine_results(docs), query), 1


def variant_rows1000(query):
    """Same scoring, twice the candidate depth (MAX_ROWS)."""
    return variant_baseline(query, rows=1000)[0], 1


def _case_variants(term):
    """label_str is a case-sensitive `strings` docValues copy, so an exact lookup
    has to guess capitalisation. VFB labels are mostly lowercase with proper nouns
    title-cased ('Kenyon cell'), so these four cover the realistic space."""
    out = [term, term.lower(), term.capitalize(), term.title()]
    return list(dict.fromkeys(out))


#: Only short inputs need augmenting. The label/synonym halves of the phrase boost
#: are additive, so a competitor carrying the query token in *both* its label and a
#: synonym outscores a term whose label *is* the query but which has no such
#: synonym — and that only bites when the query is one or two common tokens. By
#: three tokens the phrase is rare enough that few competitors match it at all.
#: Gating on this keeps the extra Solr request off the majority of searches —
#: measured below as the request multiplier.
AUGMENT_MAX_TOKENS = 2


def variant_augment(query, max_tokens=None):
    """Retrieval augmentation: a second, selective exact lookup merged into the
    candidate set. Perturbs no score — it only guarantees the sorter is *given*
    the exact match, which it already knows how to promote."""
    docs = solr(sc.build_params(query, rows=sc.DEFAULT_ROWS), sc.DEFAULT_ROWS)["docs"]
    term = sc.normalise_search_term(sc.escape_braces(query))
    extra = []
    if max_tokens is not None and len(term.split()) > max_tokens:
        return sc.sort_results(sc.refine_results(docs), query), 1
    if term:
        clause = " OR ".join('label_str:"%s"' % v.replace('"', r'\"')
                             for v in _case_variants(term))
        found = solr({"q": clause, "defType": "lucene", "fl": sc.FL,
                      "fq": [sc.FQ_BASE, sc.FQ_NOT_DEPRECATED], "wt": "json"}, 5)
        have = {d.get("short_form") for d in docs}
        extra = [d for d in found["docs"] if d.get("short_form") not in have]
    return sc.sort_results(sc.refine_results(docs + extra), query), 2


def variant_augment_short(query):
    """Augment, but only for the short queries that actually need it."""
    return variant_augment(query, max_tokens=AUGMENT_MAX_TOKENS)


#: Weight for the exact-label clause. Has to beat the *combined* label+synonym
#: phrase boost (3000 + 1500), because that combination is precisely what the
#: exact term loses to: a competitor whose label AND one of whose synonyms both
#: contain the query token collects both halves, while a term whose label *is*
#: the query but which has no redundant synonym collects only the label half.
EXACT_LABEL_BOOST = 6000


def _exact_label_clause(term):
    """`label_str` is a case-sensitive `strings` docValues copy of `label`, so an
    exact clause has to enumerate plausible capitalisations. VFB labels are
    lowercase except proper nouns ('Kenyon cell'), so these cover the space."""
    variants = list(dict.fromkeys([term, term.lower(), term.capitalize(),
                                   term.title()]))
    return " ".join('label_str:"%s"^%d' % (v.replace('"', r'\"'), EXACT_LABEL_BOOST)
                    for v in variants)


def variant_exact_boost(query):
    """Add a selective exact-label clause to `bq`.

    Unlike the label/synonym phrase halves, this one cannot be earned by a longer
    label that merely *contains* the query — `label_str` matches the whole field —
    so it lifts the exact term and nothing else. One Solr request, no extra depth.
    """
    params = sc.build_params(query, rows=sc.DEFAULT_ROWS)
    term = sc.normalise_search_term(sc.escape_braces(query))
    if term:
        params["bq"] = params["bq"] + " " + _exact_label_clause(term)
    docs = solr(params, sc.DEFAULT_ROWS)["docs"]
    return sc.sort_results(sc.refine_results(docs), query), 1


VARIANTS = {"baseline": variant_baseline, "rows1000": variant_rows1000,
            "augment": variant_augment, "augment_short": variant_augment_short,
            "exact_boost": variant_exact_boost}


def rank_of_exact(rows, label):
    want = label.lower()
    for i, d in enumerate(rows):
        if str(d.get("original_label", d.get("label", ""))).lower() == want:
            return i
    return None


def top10(rows):
    return [d.get("short_form") for d in rows[:10]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", action="append", choices=sorted(VARIANTS),
                    help="repeatable; default is baseline plus every variant")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    names = args.variant or ["baseline", "rows1000", "augment", "augment_short",
                             "exact_boost"]

    corpus = build_corpus()
    print(f"corpus: {len(corpus)} exact labels sampled from the live index "
          f"({sum(1 for c in corpus if len(c.split()) == 1)} single-token)\n")

    base_top10 = {}
    summary = {}
    for name in names:
        fn = VARIANTS[name]
        ranks, reqs = [], 0
        for label in corpus:
            rows, n = fn(label)
            reqs += n
            ranks.append((label, rank_of_exact(rows, label), len(rows)))
        found = [r for _, r, _ in ranks if r is not None]
        at0 = [r for r in found if r == 0]

        churn = []
        for q in CHURN_QUERIES:
            rows, n = fn(q)
            reqs += n
            t = top10(rows)
            if name == "baseline":
                base_top10[q] = t
            else:
                b = base_top10.get(q)
                if b is not None:
                    moved = sum(1 for a, c in zip(b, t) if a != c)
                    churn.append((q, moved))

        watched = {l: r for l, r, _ in ranks
                   if l in ("neuron", "medulla", "Kenyon cell", "mushroom body")}

        summary[name] = dict(
            recall=len(found), at0=len(at0), n=len(corpus),
            worst=max(found) if found else None, reqs=reqs,
            churn=churn, watched=watched)

        print(f"== {name}")
        print(f"   retrieves its own term : {len(found)}/{len(corpus)}")
        print(f"   at rank 0              : {len(at0)}/{len(corpus)}")
        if found:
            print(f"   worst rank when found  : {max(found)}")
        print(f"   solr requests          : {reqs}")
        print("   known cases            : " + ", ".join(
            f"{k}={'miss' if v is None else v}" for k, v in watched.items()))
        if churn:
            tot = sum(m for _, m in churn)
            print(f"   top-10 churn vs baseline: {tot} positions moved across "
                  f"{len(churn)} queries")
            for q, m in churn:
                if m:
                    print(f"       {q:16s} {m}/10 changed")
        misses = [(l, r) for l, r, _ in ranks if r is None]
        if misses and args.verbose:
            print("   misses:", [l for l, _ in misses][:12])
        elif misses:
            print(f"   misses ({len(misses)}):", [l for l, _ in misses][:6],
                  "..." if len(misses) > 6 else "")
        print()

    if "baseline" in summary and len(summary) > 1:
        b = summary["baseline"]
        print("Verdict")
        for name, s in summary.items():
            if name == "baseline":
                continue
            d_recall = s["recall"] - b["recall"]
            d_at0 = s["at0"] - b["at0"]
            ch = sum(m for _, m in s["churn"])
            print(f"  {name:9s} recall {d_recall:+3d}  rank0 {d_at0:+3d}  "
                  f"churn {ch:3d} positions  cost {s['reqs'] / b['reqs']:.1f}x requests")


if __name__ == "__main__":
    main()
