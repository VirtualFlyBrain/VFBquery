#!/usr/bin/env python3
"""Capture / refresh committed term_info render-test fixtures from live SOLR.

The term_info serialization, parity and expression-pattern render tests split
into a **fixture** variant (PR-blocking, deterministic) and a ``_live`` /
``data_health`` variant (scheduled, live). The fixture variants read a committed
complete ``vfb_json`` term_info document out of ``src/test/fixtures/term_info/``.
This script (re)captures those documents so they stay regenerable rather than
hand-authored. See ``TESTING.md`` -> "Fixture vs live (data_health)".

A fixture is the raw term_info dict as ``vfb_queries._load_term_info_dict``
returns it — the exact shape every ``_load_fixture`` / ``_fixture_raw`` /
``_fixture_term_info`` helper consumes.

Usage::

    python scripts/capture_term_info_fixtures.py            # capture all in FIXTURES
    python scripts/capture_term_info_fixtures.py <name>...  # only these fixtures
    python scripts/capture_term_info_fixtures.py --check    # verify, don't write

``--check`` fetches each id and reports whether the live document looks complete
(non-empty label/title etc.), without writing — a quick way to see, before a
scheduled run does, which production ``vfb_json`` documents are currently thin.

IMPORTANT: this reads live SOLR, so run it only when the backend is healthy, and
eyeball the diff before committing — a fixture captured during an outage or an
incomplete indexer run would bake the wrong "correct" answer into a PR gate.
Some documents (title-less pubs, split classes missing their ``Expression_pattern``
type) are known-incomplete in production; those fixtures are hand-completed from
the PDB and are marked ``hand_edited`` below so this script leaves them alone
unless explicitly named.
"""
import argparse
import json
import os
import sys

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "..", "src", "test",
                           "fixtures", "term_info")

#: fixture file name (without .json) -> the term whose term_info it holds.
#: Keep in sync with the fixtures the render tests load. ``hand_edited`` fixtures
#: are completed from the PDB because production SOLR serves them incomplete;
#: this script skips them unless named explicitly (so a bulk recapture during an
#: outage cannot silently hollow them out).
FIXTURES = {
    # pub / split — known-incomplete in production, completed from the PDB.
    "pub_FBrf0243986":                  {"id": "FBrf0243986",                    "hand_edited": True},
    "pub_FBrf0242477":                  {"id": "FBrf0242477",                    "hand_edited": True},
    "split_VFBexp_FBtp0124468FBtp0133404": {"id": "VFBexp_FBtp0124468FBtp0133404", "hand_edited": True},
    "split_VFBexp_FBtp0129935FBtp0129968": {"id": "VFBexp_FBtp0129935FBtp0129968", "hand_edited": True},

    # term_info_queries_test.py — serialization render tests.
    "class_FBbt_00048514_taste_mechanosensory": {"id": "FBbt_00048514"},
    "individual_VFB_00010001_fru":      {"id": "VFB_00010001"},
    "class_FBbt_00048531":              {"id": "FBbt_00048531"},
    "neuron_class_FBbt_00048999":       {"id": "FBbt_00048999"},
    "neuron_class_FBbt_00047030_EPG":   {"id": "FBbt_00047030"},
    "dataset_Ito2013":                  {"id": "Ito2013"},
    "license_CC_BY_NC_3_0":             {"id": "VFBlicense_CC_BY_NC_3_0"},
    "template_VFB_00200000":            {"id": "VFB_00200000"},

    # test_term_info_parity.py — parity / coverage render tests.
    "class_FBbt_00003748_medulla":      {"id": "FBbt_00003748"},
    "class_FBbt_00003686_kenyon":       {"id": "FBbt_00003686"},
    "individual_VFB_00101385_MEon":     {"id": "VFB_00101385"},
    "gene_FBgn0010339_128up":           {"id": "FBgn0010339"},
    "gene_FBgn0051882":                 {"id": "FBgn0051882"},
    "class_FBbt_00000058_related_individuals": {"id": "FBbt_00000058"},
    "dataset_Cachero2010":              {"id": "Cachero2010"},
    "template_VFB_00101567_JRC2018U":   {"id": "VFB_00101567"},
    "neuron_class_FBbt_00100243_MBON":  {"id": "FBbt_00100243"},

    # test_expression_pattern_individual_queries.py — menu / stock render tests.
    "ep_class_VFBexp_FBtp0060056":      {"id": "VFBexp_FBtp0060056"},
    "ep_individual_VFB_00020530":       {"id": "VFB_00020530"},
    "split_individual_VFB_00070031":    {"id": "VFB_00070031"},
}


def _load(short_form):
    from vfbquery.vfb_queries import _load_term_info_dict
    return _load_term_info_dict(short_form)


def _looks_complete(doc):
    """Cheap completeness heuristic for --check: a real label, and for pubs a
    non-empty title. Not exhaustive — the tests are the real check."""
    if not doc:
        return False, "no term_info document"
    core = (doc.get("term") or {}).get("core") or {}
    label, sf = core.get("label") or "", core.get("short_form") or ""
    if not label or label == sf:
        return False, "label is empty or just the id"
    if "pub" in (core.get("types") or []):
        if not ((doc.get("pub_specific_content") or {}).get("title") or "").strip():
            return False, "pub has no title"
    return True, "ok"


def capture(names, check):
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    rc = 0
    for name in names:
        entry = FIXTURES[name]
        sf = entry["id"]
        doc = _load(sf)
        ok, why = _looks_complete(doc)
        path = os.path.join(FIXTURE_DIR, name + ".json")
        if check:
            print(f"[{'ok' if ok else 'INCOMPLETE'}] {name} ({sf}): {why}")
            if not ok:
                rc = 1
            continue
        if not ok:
            print(f"SKIP {name} ({sf}): live document {why} — not overwriting. "
                  f"Recapture when the backend is healthy, or hand-complete it.")
            rc = 1
            continue
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=1, ensure_ascii=False)
        print(f"wrote {os.path.relpath(path)} ({sf})")
    return rc


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="*", help="fixture names to capture (default: all "
                    "non-hand-edited)")
    ap.add_argument("--check", action="store_true",
                    help="report completeness of the live documents; do not write")
    ap.add_argument("--include-hand-edited", action="store_true",
                    help="also (re)capture fixtures marked hand_edited — use only "
                         "when you intend to rebuild them from live data")
    args = ap.parse_args()

    if args.names:
        unknown = [n for n in args.names if n not in FIXTURES]
        if unknown:
            ap.error("unknown fixture name(s): %s\nknown: %s"
                     % (", ".join(unknown), ", ".join(sorted(FIXTURES))))
        names = args.names
    else:
        names = [n for n, e in FIXTURES.items()
                 if args.include_hand_edited or not e.get("hand_edited")]
        if not names and not args.include_hand_edited:
            print("All registered fixtures are hand_edited; nothing to capture "
                  "automatically. Pass names explicitly or --include-hand-edited.")
            return 0

    return capture(names, args.check)


if __name__ == "__main__":
    sys.exit(main())
