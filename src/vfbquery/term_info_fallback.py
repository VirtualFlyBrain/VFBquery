"""Build a missing ``term_info`` SOLR document on demand.

``get_term_info`` reads a pre-built ``term_info`` document out of the
``vfb_json`` SOLR collection. Those documents are written in bulk by
`VFB_json_schema_indexer <https://github.com/VirtualFlyBrain/VFB_json_schema_indexer>`_,
driven by the ``precompute live query results`` Jenkins job. A record that
reaches the PDB after the last successful run of that job therefore has no
document at all, and every VFBquery call for it returns ``None`` until the
job next completes — which is not a matter of hours: build #71 started on
2026-09-04, #70 (2026-09-02) was aborted, and the last success before that
was #66 on 2026-06-22.

``VFB_00107fob`` ("ME_R on JRC2018Unisex") is the case that surfaced this.
It is a perfectly good painted domain — its ``in_register_with`` edge, its
images and its parent class are all in the PDB — but with no SOLR document
it is invisible to term info, and it silently vanished from the medulla
class page as well.

This module closes that window. On a miss we run *the indexer's own query*
for the node's type, hand the row to the same deserialiser ``get_term_info``
already uses, and write the result back so the next caller gets it from
SOLR. Nothing here re-implements the schema: the queries, the document
shape and the SOLR write are all imported from the indexer, which is cloned
into the image by the Dockerfile exactly as the Jenkins job clones it. If a
term_info query changes upstream, this follows it on the next image build.

The write is deliberately conservative:

* only when the id genuinely has no document — an existing one is never
  overwritten, and the indexer's own atomic-update shape (``{"term_info":
  {"set": ...}}``) means the sibling precomputed fields on the document
  (``anat_query``, ``anat_2_ep_query``, ``ep_2_anat_query``) are untouched
  either way;
* never when the SOLR cache is disabled, so a test run against live data
  cannot write into the shared production collection. That has bitten VFB
  before: a fixture written into the production cache namespace poisoned
  JRC2018U term info for five days.

If the indexer is not importable — a plain ``pip install vfbquery`` has no
reason to carry it — every entry point here degrades to "no fallback" and
``get_term_info`` behaves exactly as it did before.
"""

import contextlib
import json
import os
import sys
import threading

# --------------------------------------------------------------------------
# Optional import of the indexer. Present in the Docker image (see Dockerfile,
# which clones VFB_json_schema_indexer and copies VFB_json_schema into its
# src/vfb, mirroring the Jenkins job); absent from a plain pip install.
# --------------------------------------------------------------------------

_IMPORT_ERROR = None
_INDEXERS = None
_send_solr_docs = None
_import_lock = threading.Lock()


def _pin_schema_version():
    """Stop ``query_roller.get_version_tag`` shelling out to git.

    It runs ``git rev-parse --short HEAD`` against the *process* working
    directory on every query build and raises ``CalledProcessError`` when
    that is not a git repository — which it never is for a running
    VFBquery container. The value only lands in the document's ``version``
    field, so serve the SHA the image was built from instead.
    """
    try:
        from src.vfb.vfb_query_builder import query_roller
    except ImportError:
        return
    query_roller.get_version_tag = lambda: schema_version()


#: Written by the Dockerfile after it resolves the two clones, so a rebuilt
#: document records which schema produced it even when the build tracked a
#: branch rather than a pinned SHA.
VERSIONS_FILE = os.getenv("VFB_VERSIONS_FILE", "/opt/vfb_versions.env")


def schema_version():
    """The VFB_json_schema commit this image was built from.

    Environment first (so a deployment can override), then the file the
    Dockerfile writes, then a marker that is obviously not a SHA.
    """
    from_env = os.getenv("VFB_JSON_SCHEMA_SHA")
    if from_env:
        return from_env
    try:
        with open(VERSIONS_FILE) as f:
            for line in f:
                key, _, value = line.strip().partition("=")
                if key == "VFB_JSON_SCHEMA_SHA" and value:
                    return value
    except OSError:
        pass
    return "unpinned"


def _seed_indexer_env():
    """Point the indexer's Neo4j connection at the one VFBquery already uses.

    ``BaseQueryIndexer.__init__`` reads PDBserver/PDBuser/PDBpassword from the
    environment and builds its own connection. Rather than run the fallback
    against a different database than the rest of the process, fill those in
    from VFBquery's own client when the deployment has not set them. Anything
    already in the environment wins.
    """
    from .vfb_queries import vc
    nc = vc.nc
    defaults = {
        "PDBserver": getattr(nc, "base_uri", None),
        "PDBuser": getattr(nc, "usr", None),
        "PDBpassword": getattr(nc, "pwd", None),
    }
    for key, value in defaults.items():
        if value and not os.getenv(key):
            os.environ[key] = value


#: Where the Dockerfile puts the indexer checkout.
INDEXER_ROOT = os.getenv("VFB_INDEXER_ROOT", "/opt/vfb_indexer")


@contextlib.contextmanager
def _indexer_importable():
    """Make ``src`` mean the indexer's package for the duration of an import.

    The indexer's top-level package is literally called ``src``, and so is
    VFBquery's own source directory -- which carries an ``__init__.py``
    (``from vfbquery import *``) and so is a *regular* package. Whichever
    comes first on ``sys.path`` wins outright and the running process always
    finds its own first, so ``import src.indexers`` fails with
    ModuleNotFoundError even with the indexer on PYTHONPATH. This is not
    hypothetical: it is what the first build of this module did.

    Put the indexer root first and evict any ``src`` already imported, then
    put both back. Safe because nothing in VFBquery imports ``src`` by name,
    and because every ``from src...`` in the indexer is module-level: they
    all resolve while this context is open, so restoring afterwards cannot
    strand a later lookup.
    """
    saved = {name: mod for name, mod in sys.modules.items()
             if name == "src" or name.startswith("src.")}
    for name in saved:
        del sys.modules[name]
    sys.path.insert(0, INDEXER_ROOT)
    try:
        yield
    finally:
        try:
            sys.path.remove(INDEXER_ROOT)
        except ValueError:
            pass
        for name in [n for n in sys.modules
                     if n == "src" or n.startswith("src.")]:
            del sys.modules[name]
        sys.modules.update(saved)


def _load_indexers():
    """Import the indexer classes once, or record why we could not."""
    global _INDEXERS, _send_solr_docs, _IMPORT_ERROR
    if _INDEXERS is not None or _IMPORT_ERROR is not None:
        return
    with _import_lock:
        if _INDEXERS is not None or _IMPORT_ERROR is not None:
            return
        try:
            _seed_indexer_env()
            with _indexer_importable():
                _pin_schema_version()
                from src.indexers.term_info.anatomical_ind_term_info_indexer import (
                    AnatomicalIndTermInfoQueryIndexer)
                from src.indexers.term_info.class_term_info_indexer import (
                    ClassTermInfoQueryIndexer)
                from src.indexers.term_info.cluster_term_info_indexer import (
                    ClusterTermInfoQueryIndexer)
                from src.indexers.term_info.dataset_term_info_indexer import (
                    DatasetTermInfoQueryIndexer)
                from src.indexers.term_info.license_term_info_indexer import (
                    LicenseTermInfoQueryIndexer)
                from src.indexers.term_info.neuron_class_term_info_indexer import (
                    NeuronClassTermInfoQueryIndexer)
                from src.indexers.term_info.pub_term_info_indexer import (
                    PubTermInfoQueryIndexer)
                from src.indexers.term_info.split_class_term_info_indexer import (
                    SplitClassTermInfoQueryIndexer)
                from src.indexers.term_info.template_term_info_indexer import (
                    TemplateTermInfoQueryIndexer)
                from src.solr_client import send_solr_docs
        except Exception as e:            # ImportError, or a missing env var
            _IMPORT_ERROR = e
            return
        _INDEXERS = {
            "template": TemplateTermInfoQueryIndexer,
            "license": LicenseTermInfoQueryIndexer,
            "dataset": DatasetTermInfoQueryIndexer,
            "pub": PubTermInfoQueryIndexer,
            "cluster": ClusterTermInfoQueryIndexer,
            "anatomical_ind": AnatomicalIndTermInfoQueryIndexer,
            "neuron_class": NeuronClassTermInfoQueryIndexer,
            "split_class": SplitClassTermInfoQueryIndexer,
            "class": ClassTermInfoQueryIndexer,
        }
        _send_solr_docs = send_solr_docs


def fallback_available():
    """True when the indexer imported and a document can be built."""
    _load_indexers()
    return _INDEXERS is not None


_warned_unavailable = False


def _warn_unavailable_once():
    """Say once why no document can be built, so an operator can tell
    "the indexer is not in this image" from "the build was attempted and
    failed". Once, not per request: a container without the indexer would
    otherwise log this on every miss."""
    global _warned_unavailable
    if _warned_unavailable:
        return
    _warned_unavailable = True
    print("term_info fallback unavailable, missing documents will not be "
          "rebuilt (%s)" % fallback_unavailable_reason())


def fallback_unavailable_reason():
    """Why :func:`fallback_available` is False, for logging. None if it is True."""
    _load_indexers()
    if _INDEXERS is not None:
        return None
    return "%s: %s" % (type(_IMPORT_ERROR).__name__, _IMPORT_ERROR)


# --------------------------------------------------------------------------
# Type dispatch
# --------------------------------------------------------------------------

#: Ids the indexer's parameter queries exclude, so we exclude them too rather
#: than writing a document the bulk job would never have written.
EXCLUDED_ID_PREFIXES = ("VFBc_", "FBlc", "SAMN", "VFB_internal")


def choose_indexer(labels):
    """Pick the indexer whose population this node belongs to.

    Mirrors, per node, the ``get_parameters_query`` predicates that each
    indexer applies across the whole graph. Order matters: the anatomical
    individual query is the one that excludes all the other Individual
    types, so it is tried after them.

    :param labels: the node's neo4j labels
    :return: key into the indexer table, or None if no indexer covers it
    """
    labels = set(labels or ())
    if "Template" in labels:
        return "template"
    if "License" in labels:
        return "license"
    if "DataSet" in labels:
        return "dataset"
    if "pub" in labels and "Individual" in labels:
        return "pub"
    if "Cluster" in labels and "Individual" in labels:
        return "cluster"
    if "Individual" in labels:
        return "anatomical_ind"
    if "Class" in labels:
        if "Neuron" in labels:
            return "neuron_class"
        if "Split" in labels:
            return "split_class"
        return "class"
    return None


def _node_labels(short_form, neo):
    """Labels for one node, or None if the PDB does not have it either."""
    from .vfb_queries import get_dict_cursor
    rows = get_dict_cursor()(neo.commit_list([
        "MATCH (n) WHERE n.short_form = '%s' RETURN labels(n) AS labels"
        % short_form.replace("'", "\\'")
    ]))
    if not rows:
        return None
    return rows[0].get("labels") or []


# --------------------------------------------------------------------------
# Build / write
# --------------------------------------------------------------------------

def build_term_info(short_form, neo=None):
    """Build one term's ``term_info`` payload live from the PDB.

    :param short_form: the term's short_form
    :param neo: a Neo4jConnect; defaults to VFBquery's own connection
    :return: ``(payload_json, solr_doc)``, or ``(None, None)``
    """
    if not fallback_available():
        _warn_unavailable_once()
        return None, None
    if short_form.startswith(EXCLUDED_ID_PREFIXES):
        print("term_info fallback: %s is excluded from the term_info index"
              % short_form)
        return None, None

    from .vfb_queries import vc, get_dict_cursor
    neo = neo or vc.nc

    labels = _node_labels(short_form, neo)
    if labels is None:
        print("term_info fallback: %s is not in the PDB either" % short_form)
        return None, None
    key = choose_indexer(labels)
    if key is None:
        print("term_info fallback: no term_info indexer covers labels %s (%s)"
              % (sorted(labels), short_form))
        return None, None

    indexer = _INDEXERS[key]()
    rows = get_dict_cursor()(neo.commit_list([
        indexer.get_vfb_json_query([short_form])]))
    if not rows:
        print("term_info fallback: %s query returned no rows for %s"
              % (key, short_form))
        return None, None

    result = rows[0]
    # The indexer's own document shape, including its atomic-update wrapper.
    solr_doc = indexer.generate_solr_doc(result, request=[short_form])
    return json.dumps(result), solr_doc


def write_term_info(solr_doc):
    """Write one document with the indexer's retry-hardened SOLR client.

    :return: True when SOLR accepted it
    """
    if not fallback_available():
        return False
    from .solr_result_cache import solr_caching_disabled
    if solr_caching_disabled():
        print("term_info fallback: cache disabled, not writing %s to SOLR"
              % solr_doc.get("id"))
        return False
    try:
        return bool(_send_solr_docs([solr_doc], "term_info"))
    except Exception as e:
        print("term_info fallback: SOLR write failed for %s: %s"
              % (solr_doc.get("id"), e))
        return False


def backfill_term_info(short_form):
    """Build a missing document, write it back, and return the payload.

    Called by ``get_term_info`` when SOLR has no document for the id. The
    caller has already established the miss, so the write cannot overwrite
    anything.

    :return: the ``term_info`` payload as a JSON string, or None
    """
    payload, solr_doc = build_term_info(short_form)
    if payload is None:
        return None
    if write_term_info(solr_doc):
        print("term_info fallback: built and indexed %s" % short_form)
    else:
        print("term_info fallback: built %s but did not index it" % short_form)
    return payload
