"""Compare the MCP ``search_terms`` search with the website's main search.

Both hit the same Solr ``ontology`` core with edismax. They differ in ``q``
construction (one phrase+wildcards vs a per-token AND of wildcard groups), in
``fq`` (hard-exclude Deprecated or only demote it), in ``bq`` boosts (the website
floats Class/DataSet/pub), and — the part no config file shows — in a runtime
exact-phrase boost the website's client appends to ``bq``.

Two things this script is careful about, because earlier revisions of it were not:

1. **Raw Solr order is not what a user sees.** The website runs every hit through
   ``refineResults`` (synonym explosion) and a ~370-line comparator before
   display. Comparing Solr's ``docs[0]`` between two configs compares something
   nobody experiences. So the website column here is ranked with the real ported
   sorter (``vfbquery.search_config``), and the unranked order is printed
   alongside, labelled as candidates.
2. **``pf`` explains nothing.** The MCP config's ``pf=true`` is a silent no-op
   (Solr reads ``pf`` as a field list, so ``true`` is a field name that does not
   exist), and a *correct* ``pf`` field list still never fires against the
   website's wildcard OR-group ``q`` because no contiguous phrase survives the
   expansion. ``--check-pf`` measures both, so the claim stays falsifiable rather
   than becoming folklore.

The website side is imported from ``vfbquery.search_config`` on purpose: that
module is now the single canonical copy (see docs/search-config-comparison.md §4),
and a hand-transcribed second copy here would be one more thing to drift.

Read-only GETs against public Solr.

    python3 docs/compare_search_configs.py
    python3 docs/compare_search_configs.py --check-pf
"""
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from vfbquery import search_config as sc     # noqa: E402  (after sys.path)

U = sc.SOLR_ONTOLOGY_URL

# ---- the MCP search_terms config, transcribed verbatim (warts included) ---- #
# `pf="true"` is kept because that is what the tool really sends; see --check-pf
# for what it does (nothing).
MCP_COMMON = dict(**{"q.op": "OR"}, defType="edismax", mm=sc.MM, qf=sc.QF,
                  pf="true", fl="short_form,label", wt="json")
BQ_MCP = ("short_form:VFBexp*^10.0 short_form:VFB*^100.0 short_form:FBbt*^100.0 "
          "short_form:FBbt_00003982^2 facets_annotation:Deprecated^0.001")
# No `NOT facets_annotation:Deprecated` — the MCP only demotes deprecated terms.
FQ_MCP = [sc.FQ_BASE]


def get(params, rows):
    p = dict(params)
    p["rows"] = str(rows)
    r = requests.get(U, params=sc.params_as_pairs(p), timeout=40)
    r.raise_for_status()
    # VFB's Solr answers wt=json with Content-Type text/plain, so go via .json()
    # on the text rather than trusting the header.
    return r.json()["response"]


def mcp_params(term):
    p = dict(MCP_COMMON)
    p["q"] = f"{term} OR {term}* OR *{term}*"
    p["bq"] = BQ_MCP
    p["fq"] = FQ_MCP
    return p


def show(label, docs, num_found, ranked=None):
    print(f"\n== {label}  numFound={num_found}")
    listing = ranked if ranked is not None else docs
    for doc in listing[:6]:
        print("   ", doc.get("short_form"), "|", doc.get("label"))


for term in ["DA1 lPN", "kenyon cell", "MBON-a2", "neuron", "medulla"]:
    print("\n############", term)

    d = get(mcp_params(term), 10)
    show("MCP search_terms (Solr order — the MCP shows this as-is)",
         d["docs"], d["numFound"])

    # The website asks for 500 candidates precisely because ranking, not Solr,
    # decides the top — so fetch its real depth even though we print 6.
    wp = sc.build_params(term, rows=sc.DEFAULT_ROWS)
    d = get(wp, sc.DEFAULT_ROWS)
    show("website — Solr candidate order (NOT what a user sees)",
         d["docs"], d["numFound"])
    ranked = sc.sort_results(sc.refine_results(d["docs"]), term)
    show("website — after refine + sort (what a user sees)",
         d["docs"], d["numFound"], ranked=ranked)


print("\n\n===== RECALL CHECK =====")
print("numFound is what each config can *retrieve*; rank is where the exact")
print("match lands once the website's sorter has run. A term can be findable and")
print("still unreachable if it falls past rows=500 — see comparison.md §5.\n")


def rank_of(ranked, needle):
    needle = needle.lower()
    for i, doc in enumerate(ranked):
        if str(doc.get("original_label", doc.get("label", ""))).lower() == needle:
            return i
    return None


for term in ["DA1", "lPN", "kenyoncell", "fan-shaped body", "MB247",
             "VFB_jrchjtdb", "1734350908", "neuron", "medulla"]:
    a = get(mcp_params(term), 1)
    wp = sc.build_params(term, rows=sc.DEFAULT_ROWS)
    b = get(wp, sc.DEFAULT_ROWS)
    ranked = sc.sort_results(sc.refine_results(b["docs"]), term)
    top = ranked[0].get("label", "-") if ranked else "-"
    r = rank_of(ranked, term)
    # "no exact label" covers two very different cases and the numFound column
    # tells them apart: a term nobody labelled this way (DA1 is only ever a
    # synonym) versus one that exists and still did not make the ranked set
    # (`neuron`, absent from all 1370 rows — the recall bug in §5).
    where = ("label match @%s" % r if r is not None
             else "no exact label in %d ranked" % len(ranked))
    print(f"{term:20s} MCP {a['numFound']:6d} | WEB {b['numFound']:6d} "
          f"top={str(top)[:34]:36s} {where}")


if "--check-pf" in sys.argv:
    print("\n\n===== pf MEASUREMENT =====")
    print("Claim: pf is inert in every VFB config. Two ways to show it.\n")

    def score(params):
        p = dict(params)
        p["fl"] = "short_form,label,score"
        d = get(p, 1)
        return d["docs"][0]["score"] if d["docs"] else float("nan")

    # (a) On a plain phrase q, a real pf field list *does* change the score — so
    #     the parameter works, and `pf=true` failing to change it proves `true`
    #     is being read as a nonexistent field name rather than as "on".
    base = dict(MCP_COMMON)
    base["q"] = "kenyon cell"
    base["bq"] = ""
    base["fq"] = FQ_MCP
    for pf in ["true", None, "label^250 synonym^120"]:
        p = dict(base)
        if pf is None:
            p.pop("pf")
        else:
            p["pf"] = pf
        print(f"  plain q, pf={str(pf):22s} -> score {score(p):9.1f}")

    # (b) On the website's wildcard OR-group q, even a real pf field list makes
    #     no difference at all: the expansion leaves no contiguous phrase for the
    #     phrase boost to match.
    print()
    for pf in ["true", None, "label^250 synonym^120"]:
        p = sc.build_params("kenyon cell", rows=1)
        p["bq"] = ""                      # isolate pf from the runtime bq boost
        if pf is None:
            p.pop("pf")
        else:
            p["pf"] = pf
        print(f"  website q, pf={str(pf):20s} -> score {score(p):9.1f}")
    print("\n  Identical scores in the second block = pf never fires. The phrase")
    print("  boost that does the work is build_phrase_boost(), appended to bq.")
