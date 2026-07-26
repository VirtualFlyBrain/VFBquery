"""Canonical VFB free-text search — the single source of truth (plan C1).

This module is a faithful Python port of what the **website** actually sends and
does, so that ``/search`` and every client can share one config instead of the
five divergent copies documented in ``docs/search-config-comparison.md``.

Ported from, and kept in step with, two files:

* ``VirtualFlyBrain/geppetto-vfb`` @ master —
  ``components/configuration/VFBMain/searchConfiguration.js``
  (``datasourceConfiguration.query_settings`` and the ``sorter``)
* ``openworm/geppetto-client`` @ tag ``VFBv2.3.8.1`` —
  ``geppetto-ui/src/search/datasources/SOLRclient.tsx``
  (``getResultsSOLR`` builds the ``q`` and the runtime phrase boost;
  ``refineResults`` explodes synonyms into rows)

The search is three stages, and *all three* are needed to reproduce what a user
sees on virtualflybrain.org:

1. **Query build** (`build_params`) — the tokenised ``q``, the ``fq`` pair, and
   the config ``bq`` **plus a runtime exact-phrase boost**. The phrase boost is
   easy to miss because it is added in the client library, not in the config
   file.
2. **Refine** (`refine_results`) — one row per synonym, relabelled
   ``"synonym (label)"``, plus the canonical row relabelled
   ``"label (short_form)"``.  So the row count out is larger than Solr's.
3. **Sort** (`sort_results`) — a ~370-line comparator. Solr's own ordering is
   *never* what the website shows, so serving raw Solr order is not "matching
   the website".

There is exactly one deviation from the JavaScript, and it is cosmetic:
``label_manipulation`` (stripping a stray backslash before a quote) is applied
**after** sorting, exactly as the website does — it sorts on raw labels and
manipulates only for display — so ordering is unaffected.

Everything else is intentionally bug-compatible, including the JS
``String.replace(str, str)`` **first-occurrence-only** semantics (hence the
``count=1`` calls below) and the empty OR-group a double space produces.

Verified: on 78 queries (16 hand-picked discriminating cases plus a 62-query
fuzz sample drawn from real labels, synonyms and short_forms, including empty
input, double spaces, braces and quotes) this module's refine+sort output is
*byte-identical in order* to running the real ``sorter`` and ``refineResults``
under Node on the same Solr docs. That matters because the comparator is not a
consistent total order, so identical ordering is a measured result, not
something the port could guarantee by construction. Re-run the harness in
``docs/`` after touching anything in section 3 or 4.
"""
from __future__ import annotations

import functools
import re
from typing import Any, Dict, Iterable, List, Optional

import requests

# --------------------------------------------------------------------------- #
# 1. Query configuration — verbatim from searchConfiguration.js @ master
# --------------------------------------------------------------------------- #

#: Free-text search runs against the *ontology* core: the ``*_autosuggest``
#: fields exist only here. ``vfb_json`` is the content store (term_info,
#: cached query results, images) and is keyed by id, not searchable this way.
SOLR_ONTOLOGY_URL = "https://solr.virtualflybrain.org/solr/ontology/select"

QF = "label^110 synonym^100 label_autosuggest synonym_autosuggest shortform_autosuggest"
MM = "45%"
#: NB not ``pf=true``. That was a long-standing bug — Solr's ``pf`` takes a
#: field list, so ``true`` was parsed as a field name and the phrase boost did
#: nothing. Fixed upstream on 2026-07-16; a checkout older than that still has
#: the broken value.
PF = "label^250 synonym^120"
PS = "0"
FL = "short_form,label,synonym,id,facets_annotation,unique_facets"

FQ_BASE = ("(short_form:VFB* OR short_form:FB* OR facets_annotation:DataSet "
           "OR facets_annotation:pub) AND NOT short_form:VFBc_*")
#: The website *hard-excludes* deprecated terms. The MCP ``search_terms`` only
#: demotes them via ``bq^0.001``, which is why a bare hemibrain bodyId resolved
#: to the wrong neuron there — the competitor was a Deprecated term.
FQ_NOT_DEPRECATED = "NOT facets_annotation:Deprecated"

#: Floats types over individuals (``Class^200``, ``FBbt*^150`` vs ``VFB*^50``)
#: and floats datasets/publications hard. This is a deliberate editorial choice
#: to lead with types, not an accident.
BQ_BASE = ("short_form:VFBexp*^10.0 short_form:VFB*^50.0 facets_annotation:Class^200.0 "
           "short_form:FBbt*^150.0 short_form:FBbt_00003982^2 "
           "facets_annotation:Deprecated^0.001 facets_annotation:DataSet^500.0 "
           "facets_annotation:pub^100.0")

DEFAULT_ROWS = 500
MAX_ROWS = 1000

#: The website's own filter chips use these weights (``filter_positive`` /
#: ``filter_negative`` in searchConfiguration.js) rather than a hard ``fq``.
FILTER_POSITIVE = "^100"
FILTER_NEGATIVE = "^0.001"


# --------------------------------------------------------------------------- #
# 2. Query build — from getResultsSOLR (SOLRclient.tsx)
# --------------------------------------------------------------------------- #

def escape_braces(search_string: str) -> str:
    """``{`` / ``}`` are Solr local-param syntax; the client escapes them first.

    Note this happens *before* normalisation, and the escaped string — not the
    normalised one — is what the sorter compares against (``window.spotlightString``).
    """
    return search_string.replace("{", "\\{").replace("}", "\\}")


def normalise_search_term(search_string: str) -> str:
    """``- + _`` to spaces, then trim.

    Bug-compatible with JS ``String.prototype.replace(string, string)``, which
    replaces only the **first** occurrence — hence ``count=1``. So
    ``"MBON-a2-b"`` normalises to ``"MBON a2-b"``, keeping the second hyphen.
    That quirk is load-bearing: it is what the live site does, and the tokens it
    produces are what the ranking was tuned against.
    """
    return (search_string
            .replace("-", " ", 1)
            .replace("+", " ", 1)
            .replace("_", " ", 1)
            .strip())


def build_q(search_string: str) -> str:
    """AND one wildcard OR-group per token.

    ``"DA1 lPN"`` -> ``"(DA1 OR DA1* OR *DA1 OR *DA1*) AND (lPN OR lPN* OR *lPN OR *lPN*)"``

    Every token must match as prefix, suffix or infix, rather than ``mm=45%``
    deciding how many words need to hit. Measurably more precise than treating
    the whole input as one phrase (``DA1 lPN``: 51 candidates vs 718).

    Empty tokens (from a double space) are kept, producing ``"( OR * OR * OR **)"``
    just as the JS ``for (let key in ...split(" "))`` loop does. That looks like a
    bug but is not a Solr error and is not inert: ``"  double  space "`` returns 3
    hits with the empty group and 0 without it, because the group degenerates to
    match-all and relaxes the conjunction. Dropping it would silently make
    ``/search`` disagree with the website.
    """
    term = normalise_search_term(escape_braces(search_string))
    groups = [f"({t} OR {t}* OR *{t} OR *{t}*)" for t in term.split(" ")]
    return " AND ".join(groups) or search_string


def build_phrase_boost(search_string: str) -> str:
    """Exact-phrase boost appended to ``bq`` at request time.

    Lives in the client library, not the config file, so it is invisible if you
    only read searchConfiguration.js. It exists because the wildcard expansion
    in ``build_q`` defeats edismax's ``pf`` phrase boost: a short exact label
    ("adult neuron") would otherwise score below longer wildcard matches and
    fall past ``rows``. Boosting the phrase in ``bq`` gets it *retrieved*; the
    sorter then lifts it to the top.

    The phrase is the **normalised** term, so a search for ``MBON-a2`` boosts
    ``label:"MBON a2"``.
    """
    term = normalise_search_term(escape_braces(search_string))
    if not term:
        return ""
    phrase = term.replace("\\", "\\\\").replace('"', '\\"')
    return f' label:"{phrase}"^3000 synonym:"{phrase}"^1500'


def build_params(query: str, rows: int = DEFAULT_ROWS,
                 filter_types: Optional[Iterable[str]] = None,
                 exclude_types: Optional[Iterable[str]] = None,
                 boost_types: Optional[Iterable[str]] = None,
                 demote_types: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """Full edismax parameter set for one search.

    ``filter_types`` / ``exclude_types`` are hard ``fq`` constraints (the
    semantics the MCP ``search_terms`` tool already exposes).
    ``boost_types`` / ``demote_types`` are soft ``bq`` weights, matching the
    website's own filter chips (``^100`` / ``^0.001``).
    """
    fq = [FQ_BASE, FQ_NOT_DEPRECATED]
    for ft in filter_types or []:
        fq.append(f"facets_annotation:{ft}")
    if exclude_types:
        fq.append("NOT (" + " OR ".join(
            f"facets_annotation:{et}" for et in exclude_types) + ")")

    bq = BQ_BASE
    for bt in boost_types or []:
        bq += f" facets_annotation:{bt}{FILTER_POSITIVE}"
    for dt in demote_types or []:
        bq += f" facets_annotation:{dt}{FILTER_NEGATIVE}"
    bq += build_phrase_boost(query)

    return {
        "q": build_q(query),
        "q.op": "OR",
        "defType": "edismax",
        "mm": MM,
        "qf": QF,
        "pf": PF,
        "ps": PS,
        "bq": bq,
        "fl": FL,
        "start": "0",
        "rows": str(max(1, min(int(rows), MAX_ROWS))),
        "wt": "json",
        "fq": fq,
    }


# --------------------------------------------------------------------------- #
# 3. Refine — from refineResults (SOLRclient.tsx)
# --------------------------------------------------------------------------- #

def _record_key(record: Dict[str, Any]) -> str:
    """Dedup key: every field, keys sorted, list values sorted and pipe-joined."""
    parts = []
    for key in sorted(record):
        value = record[key]
        if isinstance(value, list):
            value = "|".join(sorted(str(v) for v in value))
        parts.append(f"{key}:{value}")
    return "||".join(parts)


def refine_results(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Explode each Solr doc into one row per synonym plus a canonical row.

    * synonym rows  -> ``label = "<synonym> (<original label>)"``
    * canonical row -> ``label = "<original label> (<short_form>)"``

    The ``synonym`` key is **dropped** from every emitted row. That is why the
    sorter's ``getSynonymIndex`` block and its synonym-occurrence branch never
    fire in practice — they are dead code against real input. Ported anyway, so
    the comparator stays line-for-line checkable against the JS.

    ``original_label`` is added here (not in the JS) purely so API consumers can
    recover the unrefined label; it is excluded from the dedup key so it cannot
    change which rows survive.
    """
    refined: List[Dict[str, Any]] = []
    seen = set()

    def push_unique(record: Dict[str, Any], original_label: Any) -> None:
        key = _record_key(record)
        if key not in seen:
            seen.add(key)
            record["original_label"] = original_label
            refined.append(record)

    for item in docs:
        label = item.get("label")
        short_form = item.get("short_form")
        synonyms = item.get("synonym")
        if isinstance(synonyms, str):      # defensive: Solr field is multiValued
            synonyms = [synonyms]

        if synonyms:
            for syn in synonyms:
                if syn != label:
                    record = {k: v for k, v in item.items() if k != "synonym"}
                    record["label"] = f"{syn} ({label})"
                    push_unique(record, label)
            record = {k: v for k, v in item.items() if k != "synonym"}
            record["label"] = f"{label} ({short_form})"
            push_unique(record, label)
        else:
            record = {k: v for k, v in item.items() if k != "synonym"}
            record["label"] = f"{label} ({short_form})"
            push_unique(record, label)

    return refined


# --------------------------------------------------------------------------- #
# 4. Sort — from searchConfiguration.js `sorter`
# --------------------------------------------------------------------------- #

# JS \W is ASCII-only ([^A-Za-z0-9_]); Python's \W is Unicode-aware, so spell it
# out to keep tokenisation identical.
_NONWORD = re.compile(r"[^A-Za-z0-9_]+")


def _nw(s: str) -> str:
    """JS ``s.split(/\\W+/).join(' ')`` — collapse non-word runs to spaces."""
    return " ".join(_NONWORD.split(s))


def _overlap(needles: List[str], haystack: List[str]) -> int:
    """JS ``a1.filter(v => a2.includes(v)).length`` — duplicates in a1 count."""
    return sum(1 for v in needles if v in haystack)


def _main_part(label: str) -> str:
    """The label before the first ``' ('`` — i.e. before the appended context."""
    return label.split(" (")[0]


def _count_term_occurrences(item: Dict[str, Any], input_lc: str) -> int:
    """Website's "official symbol" heuristic: 2+ hits => likely the real name.

    Counts the search term in the refined label's main part and in its
    parenthetical part. The third branch (the ``synonym`` field) is dead after
    :func:`refine_results` strips that key; kept for line-for-line fidelity.
    """
    label = item.get("label")
    if not label:
        return 0
    label_lc = label.lower()
    paren_index = label_lc.find(" (")
    if paren_index > -1:
        main_part = label_lc[:paren_index]
        paren_part = label_lc[paren_index + 2:len(label_lc) - 1]
    else:
        main_part = label_lc
        paren_part = ""

    count = 0
    if input_lc in main_part:
        count += 1
    if paren_part and input_lc in paren_part:
        count += 1
    syns = item.get("synonym")
    if syns:
        if not isinstance(syns, list):
            syns = [syns]
        for syn in syns:
            if syn and input_lc in syn.lower():
                count += 1
    return count


def _synonym_index(synonym_field: Any, input_lc: str) -> int:
    """Position of an exact synonym match. Dead in practice (see refine_results)."""
    if not synonym_field:
        return -1
    if isinstance(synonym_field, list):
        syns = synonym_field
    elif isinstance(synonym_field, str):
        syns = [s.strip() for s in synonym_field.split(";")]
    else:
        syns = []
    for i, syn in enumerate(syns):
        if syn.lower() == input_lc:
            return i
    return -1


def make_comparator(input_string: str):
    """Build the website's comparator for a given search string.

    ``input_string`` is the brace-escaped raw input, trimmed — i.e.
    ``window.spotlightString``, *not* the normalised token string. Case and
    hyphens are preserved here on purpose; several rules test exact case.
    """
    inp = escape_braces(input_string).strip()
    inp_lc = inp.lower()
    inp_nw = _nw(inp_lc)
    inp_nw_us = inp_nw.replace("_", " ", 1)   # JS replace(): first occurrence only
    inp_has_space = " " in inp_lc
    inp_multi_token = len(_NONWORD.split(inp)) > 1
    inp_tokens_space = inp_lc.split(" ")
    inp_tokens_nw = _NONWORD.split(inp_lc)
    search_specifies_type = (inp.startswith("VFB")
                            or inp.startswith("FBbt")
                            or inp.startswith("FBgn"))

    def cmp(a: Dict[str, Any], b: Dict[str, Any]) -> int:
        a_label = a.get("label")
        b_label = b.get("label")
        if a_label is None:
            return 1
        if b_label is None:
            return -1

        a_id = a.get("id") or ""
        b_id = b.get("id") or ""
        a_is_class = ("FBbt" in a_id) or ("FBgn" in a_id)
        b_is_class = ("FBbt" in b_id) or ("FBgn" in b_id)

        a_short = _main_part(a_label)
        b_short = _main_part(b_label)
        a_short_lc = a_short.lower()
        b_short_lc = b_short.lower()

        # Exact label match wins outright, decided BEFORE the occurrence-count
        # heuristic: otherwise a longer subtype whose label *and* synonyms both
        # contain the term outranks the exact hit ("neuron" vs "gnathal
        # ganglion neuron").
        a_exact_lc = inp_lc == a_short_lc
        b_exact_lc = inp_lc == b_short_lc
        if a_exact_lc and not b_exact_lc:
            return -1
        if b_exact_lc and not a_exact_lc:
            return 1
        if a_exact_lc and b_exact_lc and not search_specifies_type:
            if a_is_class and not b_is_class:
                return -1
            if b_is_class and not a_is_class:
                return 1

        a_count = _count_term_occurrences(a, inp_lc)
        b_count = _count_term_occurrences(b, inp_lc)
        a_official = a_count >= 2
        b_official = b_count >= 2

        # Synonym-position ordering (dead after refine_results strips `synonym`).
        a_syn_i = _synonym_index(a.get("synonym"), inp_lc)
        b_syn_i = _synonym_index(b.get("synonym"), inp_lc)
        if (a_syn_i >= 0 or b_syn_i >= 0) and a_syn_i != b_syn_i:
            if a_syn_i >= 0 and b_syn_i < 0:
                return -1
            if b_syn_i >= 0 and a_syn_i < 0:
                return 1
            if a_syn_i >= 0 and b_syn_i >= 0:
                return a_syn_i - b_syn_i

        # Priority 0: official-symbol match.
        if a_official or b_official:
            if a_official and not b_official:
                return -1
            if b_official and not a_official:
                return 1
            if a_official and b_official and not search_specifies_type:
                if a_is_class and not b_is_class:
                    return -1
                if b_is_class and not a_is_class:
                    return 1
            # Case-insensitive official-symbol match: same predicate in the JS,
            # so once both are official this is a no-op. Kept for fidelity.

        # Priority 1: exact (case-sensitive) short-form match.
        a_exact_short = inp == a_short
        b_exact_short = inp == b_short
        if a_exact_short or b_exact_short:
            if a_exact_short and not b_exact_short:
                return -1
            if b_exact_short and not a_exact_short:
                return 1
            if a_exact_short and b_exact_short and not search_specifies_type:
                if a_is_class and not b_is_class:
                    return -1
                if b_is_class and not a_is_class:
                    return 1

        # Priority 2: case-insensitive short-form match. (Already handled by the
        # exact-label rule above, which the 2026-07-16 change hoisted to the
        # front; retained so the chain matches the JS.)
        if a_exact_lc or b_exact_lc:
            if a_exact_lc and not b_exact_lc:
                return -1
            if b_exact_lc and not a_exact_lc:
                return 1
            if a_exact_lc and b_exact_lc and not search_specifies_type:
                if a_is_class and not b_is_class:
                    return -1
                if b_is_class and not a_is_class:
                    return 1

        # Exact full-label match to the top.
        if inp == a_label:
            return -1
        if inp == b_label:
            return 1
        if inp_lc == a_label.lower():
            return -1
        if inp_lc == b_label.lower():
            return 1

        a_label_lc = a_label.lower()
        b_label_lc = b_label.lower()
        a_nw = _nw(a_label_lc)
        b_nw = _nw(b_label_lc)

        # Match ignoring non-word joiners.
        if inp_nw == a_nw:
            return -1
        if inp_nw == b_nw:
            return 1

        # Match against the id (an IRI, so this only fires on a pasted IRI).
        if inp_lc == a_id.lower():
            return -1
        if inp_lc == b_id.lower():
            return 1

        # Substring match on the non-word-normalised label, tie-broken by the
        # shorter main label.
        a_find = a_nw.find(inp_nw)
        b_find = b_nw.find(inp_nw)
        if a_find > -1 and (len(a_short) < len(b_short) or a_find < 0):
            return -1
        if b_find > -1 and (len(a_short) > len(b_short) or a_find < 0):
            return 1

        # Same again with the first underscore ignored.
        a_nw_us = a_nw.replace("_", " ", 1)
        b_nw_us = b_nw.replace("_", " ", 1)
        a_find_us = a_nw_us.find(inp_nw_us)
        b_find_us = b_nw_us.find(inp_nw_us)
        if (len(a_short) < len(b_short) or b_find_us < 0) and a_find_us > -1:
            return -1
        if (len(a_short) > len(b_short) or a_find_us < 0) and b_find_us > -1:
            return 1

        # Space-token overlap.
        if inp_has_space:
            c_a = _overlap(inp_tokens_space, a_label_lc.split(" "))
            c_b = _overlap(inp_tokens_space, b_label_lc.split(" "))
            if c_a > 0 or c_b > 0:
                if c_a > c_b:
                    return -1
                if c_a < c_b:
                    return 1

        # Non-word-token overlap.
        if inp_multi_token:
            c_a = _overlap(inp_tokens_nw, _NONWORD.split(a_label_lc))
            c_b = _overlap(inp_tokens_nw, _NONWORD.split(b_label_lc))
            if c_a > 0 or c_b > 0:
                if c_a > c_b:
                    return -1
                if c_a < c_b:
                    return 1

            # Same overlap but against the primary label only (drop the last
            # parenthetical chunk), so a match in the appended context does not
            # count as a match in the name. A label with no " (" yields the
            # empty string here, exactly as the JS pop()+join() does — do not
            # "helpfully" fall back to the whole label, that changes ordering.
            a_primary = " (".join(a_label.split(" (")[:-1])
            b_primary = " (".join(b_label.split(" (")[:-1])
            c_a = _overlap(inp_tokens_nw, _NONWORD.split(a_primary.lower()))
            c_b = _overlap(inp_tokens_nw, _NONWORD.split(b_primary.lower()))
            if c_a > 0 or c_b > 0:
                if c_a > c_b:
                    return -1
                if c_a < c_b:
                    return 1

        # Plain substring: found in one but not the other.
        a_pos = a_label_lc.find(inp_lc)
        b_pos = b_label_lc.find(inp_lc)
        if a_pos < 0 and b_pos > -1:
            return 1
        if b_pos < 0 and a_pos > -1:
            return -1

        # Earlier match position wins.
        if a_pos > -1 and a_pos < b_pos:
            return -1
        if b_pos > -1 and b_pos < a_pos:
            return 1

        # Types (FBbt) above individuals (VFB_).
        if ("FBbt" in a_id) and ("FBbt" not in b_id):
            return -1
        if ("FBbt" in b_id) and ("FBbt" not in a_id):
            return 1

        # Expression patterns up.
        if ("VFBexp" in a_id) and ("VFBexp" not in b_id):
            return -1
        if ("VFBexp" in b_id) and ("VFBexp" not in a_id):
            return 1

        # Earlier match position in the id.
        a_id_pos = a_id.lower().find(inp_lc)
        b_id_pos = b_id.lower().find(inp_lc)
        if a_id_pos > -1 and a_id_pos < b_id_pos:
            return -1
        if b_id_pos > -1 and b_id_pos < a_id_pos:
            return 1

        # Finally: alphabetical, which in practice floats shorter synonyms up.
        if a_label < b_label:
            return -1
        if a_label > b_label:
            return 1
        return 0

    return cmp


def sort_results(rows: List[Dict[str, Any]], input_string: str) -> List[Dict[str, Any]]:
    """Apply the website comparator. Stable, like ``Array.prototype.sort``."""
    return sorted(rows, key=functools.cmp_to_key(make_comparator(input_string)))


# --------------------------------------------------------------------------- #
# 5. Display fix-up — `label_manipulation` in searchConfiguration.js
# --------------------------------------------------------------------------- #

_STRAY_ESCAPE = re.compile(r"\\(['\"])")


def clean_label(label: Any) -> Any:
    """Strip a backslash before a quote/apostrophe.

    Some source data is over-escaped (``y5B\\'2a`` for ``y5B'2a``). A backslash
    is never legitimate before a quote in a VFB label, so this is safe and
    idempotent. Applied after sorting, as the website does.
    """
    if isinstance(label, str):
        return _STRAY_ESCAPE.sub(r"\1", label)
    return label


# --------------------------------------------------------------------------- #
# 6. One-call search
# --------------------------------------------------------------------------- #

def params_as_pairs(params: Dict[str, Any]) -> List[tuple]:
    """Flatten to ``(key, value)`` pairs, repeating multi-valued keys.

    ``requests`` takes list values directly; ``aiohttp`` does not, and ``fq`` is
    multi-valued, so the server side needs this form.
    """
    pairs: List[tuple] = []
    for key, value in params.items():
        if isinstance(value, (list, tuple)):
            pairs.extend((key, str(v)) for v in value)
        else:
            pairs.append((key, str(value)))
    return pairs


def solr_query(query: str, rows: int = DEFAULT_ROWS, timeout: int = 30,
               session: Optional[requests.Session] = None,
               **kwargs) -> List[Dict[str, Any]]:
    """Issue the canonical query and return raw Solr docs (unrefined, unsorted)."""
    params = build_params(query, rows=rows, **kwargs)
    get = session.get if session is not None else requests.get
    response = get(SOLR_ONTOLOGY_URL, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json().get("response", {}).get("docs", [])


def search(query: str, rows: int = DEFAULT_ROWS, limit: Optional[int] = None,
           timeout: int = 30, session: Optional[requests.Session] = None,
           **kwargs) -> List[Dict[str, Any]]:
    """Website-equivalent search: query, refine, sort, clean.

    ``rows`` is how many docs to ask Solr for (ranking quality depends on a wide
    candidate set — the website uses 500). ``limit`` truncates the *ranked*
    output, so a caller wanting one answer still gets it ranked against the full
    candidate set. Returns a list of dicts with ``short_form``, refined
    ``label``, ``original_label``, ``id``, ``facets_annotation`` and
    ``unique_facets``.
    """
    docs = solr_query(query, rows=rows, timeout=timeout, session=session, **kwargs)
    ranked = sort_results(refine_results(docs), query)
    if limit is not None:
        ranked = ranked[:max(0, int(limit))]
    for row in ranked:
        row["label"] = clean_label(row.get("label"))
        row["original_label"] = clean_label(row.get("original_label"))
    return ranked
