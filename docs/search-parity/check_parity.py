#!/usr/bin/env python3
"""Prove that search_config.py orders results identically to the live website JS.

The website's ranking is a ~370-line comparator that is *not* a consistent total
order (several rules mix label length with substring position, so a<b<c<a is
possible). Both V8's Array#sort and CPython's list.sort are TimSort, but with an
inconsistent comparator that only means they *tend* to agree — it is not a
guarantee. So parity has to be measured, not assumed, and re-measured whenever
either side changes.

This fetches real Solr docs once per query and feeds the *same* docs to both
implementations, so it isolates refine+sort from any query-construction
difference.

Usage:
    git clone https://github.com/VirtualFlyBrain/geppetto-vfb /tmp/gvfb
    GEPPETTO_VFB=/tmp/gvfb python3 docs/search-parity/check_parity.py [--fuzz 60]

Exits non-zero on any ordering mismatch.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
NODE_SCRIPT = HERE / "sort_under_node.js"

# Hand-picked cases, each chosen because it discriminates between plausible
# implementations rather than because it is typical.
CASES = [
    "MBON-a2",        # exact match is an L1EM *individual*, not the class
    "MBON-a2-b",      # JS replace() is first-occurrence-only: -> "MBON a2-b"
    "1734350908",     # bare hemibrain bodyId, single doc, two refined rows
    "DA1 lPN",        # multi-token; exercises the space/token overlap rules
    "kenyon cell",    # many synonym rows collide on the same class
    "neuron",         # 500 docs -> 1370 rows; exact term falls outside rows
    "adult neuron",   # largest refined set; worst-case sort cost
    "fan-shaped body",  # hyphen normalisation plus exact-label hit
    "FBbt_00003982",  # search specifies a type: class preference suppressed
    "VFB_00101567",   # ditto for an individual
    "medulla",        # big, mixed class/individual
    "JRC2018Unisex",  # template/dataset naming
    "y5B'2a",         # apostrophe; exercises label_manipulation
    "mushroom body",
    "L1EM",           # dataset accession prefix shared by many individuals
    "Ito2013",        # publication
    "",               # empty input
    "  double  space ",  # empty OR-group; NOT inert (3 hits vs 0 without it)
    "x{y}",           # brace escaping
    'quote"here',     # quote escaping in the phrase boost
    "MBON_a2",        # underscore normalisation
    "-lead",          # leading hyphen
]


def load_search_config():
    path = REPO / "src" / "vfbquery" / "search_config.py"
    spec = importlib.util.spec_from_file_location("search_config", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # imported directly: the package __init__ pulls in pysolr
    return module


def fuzz_queries(session, sc, n, seed=20260722):
    """Draw queries from real labels, synonyms and short_forms."""
    random.seed(seed)
    response = session.get(sc.SOLR_ONTOLOGY_URL, params={
        "q": "*:*", "rows": "3000", "wt": "json",
        "fl": "label,synonym,short_form", "sort": "short_form asc",
    }, timeout=60).json()
    pool = []
    for doc in response["response"]["docs"]:
        if doc.get("label"):
            pool.append(doc["label"])
        for syn in (doc.get("synonym") or [])[:1]:
            pool.append(syn)
        pool.append(doc["short_form"])
    return random.sample(pool, min(n, len(pool)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuzz", type=int, default=0,
                        help="additionally check N random real labels/synonyms")
    parser.add_argument("--rows", type=int, default=500)
    args = parser.parse_args()

    import requests

    sc = load_search_config()
    session = requests.Session()
    gvfb = os.environ.get("GEPPETTO_VFB", "/tmp/gvfb")
    if not (Path(gvfb) / "components/configuration/VFBMain/searchConfiguration.js").exists():
        print(f"geppetto-vfb checkout not found at {gvfb}; set GEPPETTO_VFB", file=sys.stderr)
        return 2

    queries = list(CASES)
    if args.fuzz:
        queries += fuzz_queries(session, sc, args.fuzz)

    env = dict(os.environ, GEPPETTO_VFB=gvfb)
    failures = []
    started = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        payload_path = Path(tmp) / "docs.json"
        for query in queries:
            try:
                docs = sc.solr_query(query, rows=args.rows, timeout=60, session=session)
            except Exception as exc:  # noqa: BLE001 - report and continue
                failures.append((query, f"solr error: {type(exc).__name__}: {exc}"))
                continue

            payload_path.write_text(json.dumps({"query": query, "docs": docs}))
            proc = subprocess.run(
                ["node", str(NODE_SCRIPT), str(payload_path)],
                capture_output=True, text=True, env=env, check=False,
            )
            if proc.returncode != 0:
                failures.append((query, "node failed: " + proc.stderr.strip()[:300]))
                continue

            js_rows = json.loads(proc.stdout)["rows"]
            py_rows = [[r.get("short_form"), r.get("label")] for r in
                       sc.sort_results(sc.refine_results([dict(d) for d in docs]), query)]

            if py_rows == js_rows:
                print(f"  ok   {query!r:<24} docs={len(docs):>3} rows={len(py_rows)}")
                continue

            same_multiset = sorted(map(tuple, py_rows)) == sorted(map(tuple, js_rows))
            first = next((i for i in range(min(len(py_rows), len(js_rows)))
                          if py_rows[i] != js_rows[i]), None)
            detail = (f"first diff at {first}: js={js_rows[first][1]!r} py={py_rows[first][1]!r}"
                      if first is not None else
                      f"lengths differ js={len(js_rows)} py={len(py_rows)}")
            failures.append((query, f"same_multiset={same_multiset}; {detail}"))
            print(f"  FAIL {query!r:<24} {detail}")

    print(f"\n{len(queries)} queries in {time.time() - started:.0f}s")
    if failures:
        print(f"{len(failures)} mismatch(es):")
        for query, why in failures:
            print(f"  {query!r}: {why}")
        return 1
    print("all orderings identical to the website JS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
