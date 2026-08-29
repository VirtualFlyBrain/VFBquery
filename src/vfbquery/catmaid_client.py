"""
CATMAID pass-through for the VFB-hosted CATMAID instances.

VFB hosts public, read-only CATMAID servers for several connectomics
datasets (FAFB, FANC, L1EM, ...). Their connection details — base URL,
anonymous API token and project list — are published at
https://virtualflybrain.org/data/EM/catmaid.json and are fetched (and
cached) from there at runtime, so new instances appear here without a
code change. The tokens are public by design: they authenticate as
CATMAID's AnonymousUser, whose only permission is ``can_browse``, so
they grant exactly the read access the servers already offer everyone
and the server refuses writes made with them.

What this module adds over calling CATMAID directly:

* A curated, read-only command registry (:data:`CATMAID_COMMANDS`)
  covering the sensible query surface of the CATMAID HTTP API —
  skeletons, connectivity, annotations, connectors, labels, nodes,
  stats — with writes and admin endpoints deliberately absent.
* VFB id handling: anywhere a command takes skeleton ids, callers may
  pass CATMAID skeleton ids (skids), VFB short_form ids (``VFB_xxxxxxxx``)
  or a mixed list. VFB ids are converted to skids through the knowledge
  graph's ``database_cross_reference`` xrefs before the request is made,
  and the response envelope carries the mapping both ways.
* CATMAID neuron ids are not stored in the VFB KB, so commands that
  address a *neuron* (rather than a skeleton) transparently derive the
  neuron id from the skid via CATMAID's ``neurons/from-models``.

By default results come back in a VFB envelope::

    {
      "instance":  "fafb",
      "project_id": 1,
      "command":   "connectivity",
      "xref_db":   "catmaid_fafb",        # KB site used for id conversion
      "id_map":    {"VFB_001011rj": "2856545"},  # input VFB id -> skid
      "unmatched": [],                      # inputs that could not be mapped
      "reverse_map": {"2856545": "VFB_001011rj"},# skids seen in result -> VFB id
      "result":    <untouched CATMAID response>
    }

Pass ``raw=True`` (or ``?raw=true`` over HTTP) to get the untouched
CATMAID response alone.

Only some instances have skid xrefs in the VFB KB (currently the FAFB,
FANC and L1EM projects). On instances without xrefs the pass-through
still works with plain skids; passing a VFB id there raises a clear
error instead of guessing. larva1099 will gain xrefs once its neurons
are loaded into VFB; the remaining instances (abd1.5, iav-robo, iav-tnt,
l3vnc) host mutant specimens, which sit outside VFB's wildtype-based
data model, so they are expected to stay skid-only.
"""

import json
import base64
import logging
import os
import re
import threading
import time
from urllib.parse import urlparse

import requests

from .neo4j_client import Neo4jConnect, dict_cursor

log = logging.getLogger("vfbquery.catmaid")

# ---------------------------------------------------------------------------
# Configuration / constants
# ---------------------------------------------------------------------------

#: Where the public instance registry lives. Override for testing.
CATMAID_JSON_URL = os.getenv(
    "VFBQUERY_CATMAID_JSON_URL",
    "https://virtualflybrain.org/data/EM/catmaid.json")

#: How long the fetched catmaid.json is trusted, seconds. 0 (the default)
#: means for the whole run: instances are added rarely and tokens only ever
#: fail loudly (401), so one fetch per process is enough. Set a positive
#: TTL for a long-lived server that should pick up new instances without a
#: restart, or use get_catmaid_config(force_refresh=True).
CATMAID_CONFIG_TTL = float(os.getenv("VFBQUERY_CATMAID_CONFIG_TTL", "0"))

#: How long the KB-derived (instance, project) -> xref-site map is trusted.
CATMAID_SITES_TTL = float(os.getenv("VFBQUERY_CATMAID_SITES_TTL", "3600"))

#: HTTP timeouts for calls to the CATMAID servers (connect, read).
CATMAID_TIMEOUT = (10.0, float(os.getenv("VFBQUERY_CATMAID_READ_TIMEOUT_S", "120")))

#: Hard cap on how many ids one call may convert / pass through.
MAX_IDS_PER_CALL = int(os.getenv("VFBQUERY_CATMAID_MAX_IDS", "2000"))

#: Cap on how many distinct skid-shaped result keys the reverse lookup
#: will try to map back to VFB ids.
MAX_REVERSE_LOOKUP = int(os.getenv("VFBQUERY_CATMAID_MAX_REVERSE", "2000"))

_VFB_ID_RE = re.compile(r"^VFB_[A-Za-z0-9]{8}$")
_SKID_RE = re.compile(r"^\d+$")

#: Fallback (instance_id, project_id) -> KB Site short_form map, used only
#: if the live KB lookup fails. Derived from the KB on 2026-08-29.
_STATIC_XREF_SITES = {
    ("fafb", 1): "catmaid_fafb",
    ("fanc", 1): "catmaid_fanc",
    ("fanc", 2): "catmaid_fanc_JRC2018VF",
    ("l1em", 1): "catmaid_l1em",
}


# ---------------------------------------------------------------------------
# Command registry — the curated, read-only CATMAID query surface.
#
# Each entry:
#   method   — HTTP verb used against CATMAID.
#   path     — path template; {project_id} always available, plus optional
#              {skeleton_id} / {neuron_id} / other slots.
#   doc      — one-line description (surfaced by list_catmaid_commands()).
#   id_params— mapping of PUBLIC parameter name -> wire template for a
#              *list* of skeleton ids ("skids[{i}]" style indexed arrays).
#              Values accept skids, VFB ids, or a mixed list.
#   id_path  — a single id in the path: {"slot": <path slot>,
#              "kind": "skid" | "neuron_id"}. Public name is always "id".
#              kind "neuron_id" accepts a skid/VFB id and bridges to the
#              CATMAID neuron id via neurons/from-models.
#   returns  — "json" (default), "text" or "bytes".
#
# Anything else the caller passes is forwarded to CATMAID verbatim (use
# CATMAID's own parameter names, including indexed forms like
# "annotated_with[0]" where the API wants arrays), so options that are not
# listed here still work. Write/admin endpoints are deliberately absent —
# the anonymous tokens cannot use them anyway.
# ---------------------------------------------------------------------------

CATMAID_COMMANDS = {
    # -- instance-level -----------------------------------------------------
    "projects": {
        "method": "GET", "path": "/projects/",
        "doc": "List projects visible on this instance.", "project": False},
    "annotations": {
        "method": "GET", "path": "/{project_id}/annotations/",
        "doc": "List annotations in the project."},
    "labels": {
        "method": "GET", "path": "/{project_id}/labels/",
        "doc": "List all (treenode) labels in use."},
    "label_stats": {
        "method": "GET", "path": "/{project_id}/labels/stats",
        "doc": "Label usage statistics."},
    "stats_nodecount": {
        "method": "GET", "path": "/{project_id}/stats/nodecount",
        "doc": "Nodes created per user."},
    "stats_cable_length": {
        "method": "GET", "path": "/{project_id}/stats/cable-length",
        "doc": "Largest skeletons by cable length."},
    "stats_server": {
        "method": "GET", "path": "/{project_id}/stats/server",
        "doc": "Server state information."},
    "origins": {
        "method": "GET", "path": "/{project_id}/origins/",
        "doc": "List available data sources."},
    "interpolatable_sections": {
        "method": "GET", "path": "/{project_id}/interpolatable-sections/",
        "doc": "Broken/interpolatable section locations."},
    "deep_links": {
        "method": "GET", "path": "/{project_id}/links/",
        "doc": "List saved deep links."},
    "landmarks": {
        "method": "GET", "path": "/{project_id}/landmarks/",
        "doc": "List landmarks (with_locations=true for coordinates)."},
    "landmark_groups": {
        "method": "GET", "path": "/{project_id}/landmarks/groups/",
        "doc": "List landmark groups (with_members/with_locations options)."},
    "similarity_configs": {
        "method": "GET", "path": "/{project_id}/similarity/configs/",
        "doc": "List NBLAST similarity configurations."},
    "similarity_queries": {
        "method": "GET", "path": "/{project_id}/similarity/queries/",
        "doc": "List NBLAST similarity tasks."},
    "connector_types": {
        "method": "GET", "path": "/{project_id}/connectors/types/",
        "doc": "List available connector (synapse) link types."},

    # -- finding things -----------------------------------------------------
    "list_skeletons": {
        "method": "GET", "path": "/{project_id}/skeletons/",
        "doc": "List skeleton ids by filter (nodecount_gt=, created_by=, ...)."},
    "list_neurons": {
        "method": "GET", "path": "/{project_id}/neurons/",
        "doc": "List neurons by filter criteria."},
    "annotations_query_targets": {
        "method": "POST", "path": "/{project_id}/annotations/query-targets",
        "doc": "Find neurons/annotations by annotation or name "
               "(name=, annotated_with=, types[0]=neuron, ...)."},
    "find_label_nodes": {
        "method": "POST", "path": "/{project_id}/nodes/find-labels",
        "doc": "Find nodes whose labels match a query (query=)."},
    "nearest_node": {
        "method": "GET", "path": "/{project_id}/nodes/nearest",
        "doc": "Closest node to a location (x=, y=, z=)."},

    # -- skeleton queries (accept skids and/or VFB ids) ---------------------
    "neuron_names": {
        "method": "POST", "path": "/{project_id}/skeleton/neuronnames",
        "doc": "Map skeleton ids to neuron names.",
        "id_params": {"ids": "skids[{i}]"}},
    "skeleton_validity": {
        "method": "POST", "path": "/{project_id}/skeletons/validity",
        "doc": "Which of the given skeleton ids exist in the project.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "skeleton_summary": {
        "method": "POST", "path": "/{project_id}/skeletons/summary",
        "doc": "Summary information (node counts, cable, review) per skeleton.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "cable_length": {
        "method": "POST", "path": "/{project_id}/skeletons/cable-length",
        "doc": "Cable length per skeleton.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "review_status": {
        "method": "POST", "path": "/{project_id}/skeletons/review-status",
        "doc": "Review status per skeleton.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "compact_detail": {
        "method": "POST", "path": "/{project_id}/skeletons/compact-detail",
        "doc": "Compact treenode representation for a set of skeletons "
               "(with_connectors=, with_tags=, ...).",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "annotations_for_skeletons": {
        "method": "POST", "path": "/{project_id}/annotations/forskeletons",
        "doc": "Annotations on each of a set of skeletons.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "connectivity": {
        "method": "POST", "path": "/{project_id}/skeletons/connectivity",
        "doc": "Upstream/downstream synaptic partners "
               "(boolean_op=OR, with_nodes=false, ...).",
        "id_params": {"ids": "source_skeleton_ids[{i}]"}},
    "connectivity_counts": {
        "method": "POST", "path": "/{project_id}/skeletons/connectivity-counts",
        "doc": "Synapse counts by link type per skeleton.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "connectivity_matrix": {
        "method": "POST", "path": "/{project_id}/skeleton/connectivity_matrix",
        "doc": "Sparse connectivity matrix between two skeleton sets.",
        "id_params": {"rows": "rows[{i}]", "columns": "columns[{i}]"}},
    "circles_of_hell": {
        "method": "POST", "path": "/{project_id}/graph/circlesofhell",
        "doc": "Skeletons within n hops of the given set (n_circles=1, ...).",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "connector_links": {
        "method": "POST", "path": "/{project_id}/connectors/links/",
        "doc": "Connector links on a set of skeletons "
               "(relation_type=presynaptic_to|postsynaptic_to|...).",
        "id_params": {"ids": "skeleton_ids[{i}]"}},
    "neuron_ids": {
        "method": "POST", "path": "/{project_id}/neurons/from-models",
        "doc": "CATMAID neuron id for each skeleton id.",
        "id_params": {"ids": "model_ids[{i}]"}},
    "sampler_count": {
        "method": "POST", "path": "/{project_id}/skeletons/sampler-count",
        "doc": "Number of reconstruction samplers per skeleton.",
        "id_params": {"ids": "skeleton_ids[{i}]"}},

    # -- single-skeleton queries (id= accepts one skid or VFB id) -----------
    "swc": {
        "method": "GET", "path": "/{project_id}/skeleton/{skeleton_id}/swc",
        "doc": "Skeleton as SWC text. aligned=<template short_form or label> "
               "returns VFB's copy registered to that template instead of "
               "the original EM-space skeleton (aligned=vfb picks the VFB "
               "copy while there is only one; aligned=original or omitted "
               "is the CATMAID original).",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}, "returns": "text"},
    "eswc": {
        "method": "GET", "path": "/{project_id}/skeleton/{skeleton_id}/eswc",
        "doc": "Skeleton as extended SWC text (creator/edit metadata).",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}, "returns": "text"},
    "neuroglancer_skeleton": {
        "method": "GET",
        "path": "/{project_id}/skeletons/{skeleton_id}/neuroglancer",
        "doc": "Skeleton in neuroglancer precomputed format "
               "(base64 in the JSON envelope).",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}, "returns": "bytes"},
    "skeleton_root": {
        "method": "GET", "path": "/{project_id}/skeletons/{skeleton_id}/root",
        "doc": "Root treenode id and location of a skeleton.",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}},
    "skeleton_cable_length": {
        "method": "GET",
        "path": "/{project_id}/skeletons/{skeleton_id}/cable-length",
        "doc": "Cable length of a single skeleton.",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}},
    "skeleton_compact_detail": {
        "method": "GET",
        "path": "/{project_id}/skeletons/{skeleton_id}/compact-detail",
        "doc": "Compact treenode representation of one skeleton "
               "(with_connectors=, with_tags=, ...).",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}},
    "skeleton_node_overview": {
        "method": "GET",
        "path": "/{project_id}/skeletons/{skeleton_id}/node-overview",
        "doc": "Treenode / review / label overview of one skeleton.",
        "id_path": {"slot": "skeleton_id", "kind": "skid"}},
    "neuron_skeletons": {
        "method": "GET",
        "path": "/{project_id}/neuron/{neuron_id}/get-all-skeletons",
        "doc": "All skeleton ids modelling a neuron. id= accepts a skid or "
               "VFB id; the CATMAID neuron id is derived automatically.",
        "id_path": {"slot": "neuron_id", "kind": "neuron_id"}},

    # -- nodes / treenodes / connectors -------------------------------------
    "node_locations": {
        "method": "POST", "path": "/{project_id}/nodes/location",
        "doc": "Locations for a set of node ids (node_ids[0]=..., raw node "
               "ids, not skeleton ids)."},
    "treenode_info": {
        "method": "GET", "path": "/{project_id}/treenodes/{treenode_id}/info",
        "doc": "Skeleton/neuron information for one treenode "
               "(path id is a raw treenode id).",
        "path_params": ["treenode_id"]},
    "connector_info": {
        "method": "GET", "path": "/{project_id}/connectors/{connector_id}/",
        "doc": "Detailed information on one connector "
               "(path id is a raw connector id).",
        "path_params": ["connector_id"]},
    "node_labels": {
        "method": "GET", "path": "/{project_id}/labels/{node_type}/{node_id}/",
        "doc": "Labels on one node (node_type=treenode|connector, node_id=).",
        "path_params": ["node_type", "node_id"]},

    # -- spatial ------------------------------------------------------------
    "skeletons_in_bounding_box": {
        "method": "POST", "path": "/{project_id}/skeletons/in-bounding-box",
        "doc": "Skeleton ids intersecting a bounding box "
               "(minx=..maxz=, min_nodes=, ...)."},
    "connectors_in_bounding_box": {
        "method": "POST", "path": "/{project_id}/connectors/in-bounding-box",
        "doc": "Connectors in a bounding box (minx=..maxz=, ...)."},
    "skeletons_within_distance": {
        "method": "POST",
        "path": "/{project_id}/skeletons/within-spatial-distance",
        "doc": "Skeletons with nodes within a distance of a location."},
}


# ---------------------------------------------------------------------------
# catmaid.json config cache
# ---------------------------------------------------------------------------

_config_lock = threading.Lock()
_config_cache = {"fetched": 0.0, "data": None}


def _http_session():
    """One requests session per process (connection pooling)."""
    global _SESSION
    try:
        return _SESSION
    except NameError:
        _SESSION = requests.Session()
        return _SESSION


def get_catmaid_config(force_refresh=False):
    """The parsed catmaid.json registry, cached for :data:`CATMAID_CONFIG_TTL`.

    Fails soft: if a refresh fails but a previously fetched copy exists, the
    stale copy is returned (a stale token fails loudly at the CATMAID end;
    an unnecessary hard failure here would take every instance down at once).
    """
    now = time.monotonic()
    with _config_lock:
        if (not force_refresh and _config_cache["data"] is not None
                and (CATMAID_CONFIG_TTL <= 0
                     or now - _config_cache["fetched"] < CATMAID_CONFIG_TTL)):
            return _config_cache["data"]
        try:
            resp = _http_session().get(CATMAID_JSON_URL, timeout=CATMAID_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data.get("instances"), list):
                raise ValueError("catmaid.json has no 'instances' list")
            _config_cache.update(fetched=now, data=data)
            return data
        except Exception as exc:
            if _config_cache["data"] is not None:
                log.warning("catmaid.json refresh failed (%s) — using stale copy",
                            exc)
                return _config_cache["data"]
            raise


def _instances_by_id(config=None):
    config = config or get_catmaid_config()
    return {inst["id"]: inst for inst in config.get("instances", [])
            if inst.get("id")}


# ---------------------------------------------------------------------------
# KB xref-site discovery — which Site node holds skids for which
# (instance, project), derived from the Site link_base URLs.
# ---------------------------------------------------------------------------

_NC = None
_nc_lock = threading.Lock()


def _get_nc():
    """Per-process Neo4jConnect, same rationale as vfb_connectivity._get_nc."""
    global _NC
    with _nc_lock:
        if _NC is None:
            _NC = Neo4jConnect()
        return _NC


_sites_lock = threading.Lock()
_sites_cache = {"fetched": 0.0, "map": None}

_PID_RE = re.compile(r"[?&]pid=(\d+)")


def _xref_site_map(force_refresh=False):
    """{(instance_id, project_id): site_short_form} from the KB.

    Site nodes for the hosted instances carry link_base URLs like
    ``https://fafb.catmaid.virtualflybrain.org/?pid=1&...`` — the host names
    the instance and ``pid`` the project, so the map derives itself and new
    xref sites are picked up without a code change. Falls back to
    :data:`_STATIC_XREF_SITES` if the KB is unreachable.
    """
    now = time.monotonic()
    with _sites_lock:
        if (not force_refresh and _sites_cache["map"] is not None
                and now - _sites_cache["fetched"] < CATMAID_SITES_TTL):
            return _sites_cache["map"]
        query = (
            "MATCH (s:Site) WHERE NOT s:Deprecated "
            "AND ANY(lb IN s.link_base WHERE lb CONTAINS "
            "'catmaid.virtualflybrain.org') "
            "RETURN s.short_form AS site, s.link_base[0] AS link")
        try:
            rows = dict_cursor(_get_nc().commit_list([query]))
            site_map = {}
            for row in rows or []:
                link = row.get("link") or ""
                host = urlparse(link).netloc.lower()
                instance = host.split(".catmaid.")[0]
                pid_match = _PID_RE.search(link)
                if not instance or not pid_match:
                    continue
                site_map[(instance, int(pid_match.group(1)))] = row["site"]
            if not site_map:
                raise ValueError("no CATMAID Site nodes found")
            _sites_cache.update(fetched=now, map=site_map)
            return site_map
        except Exception as exc:
            log.warning("CATMAID xref-site lookup failed (%s) — using static "
                        "fallback map", exc)
            return dict(_STATIC_XREF_SITES)


# ---------------------------------------------------------------------------
# id classification and conversion
# ---------------------------------------------------------------------------

def _as_id_list(value):
    """Normalise an ids argument (scalar, list, or comma-separated string)."""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = list(value)
    elif isinstance(value, str):
        items = [p for p in (s.strip() for s in value.split(",")) if p]
    else:
        items = [value]
    out = []
    for item in items:
        s = str(item).strip()
        if not s:
            continue
        if not (_VFB_ID_RE.match(s) or _SKID_RE.match(s)):
            raise ValueError(
                "'%s' is neither a CATMAID skeleton id nor a VFB id "
                "(VFB_xxxxxxxx)" % s)
        out.append(s)
    if len(out) > MAX_IDS_PER_CALL:
        raise ValueError("Too many ids in one call (%d > %d)"
                         % (len(out), MAX_IDS_PER_CALL))
    return out


def _quote_list(values):
    """Quote validated ids as a Cypher string list literal."""
    return "[" + ", ".join("'%s'" % v for v in values) + "]"


def vfb_ids_to_skids(vfb_ids, site):
    """{vfb_id: skid} for the given VFB ids on one KB xref site."""
    vfb_ids = sorted(set(vfb_ids))
    if not vfb_ids:
        return {}
    query = (
        "MATCH (s:Site {short_form: '%s'})<-[r:database_cross_reference]"
        "-(i:Entity) WHERE i.short_form IN %s "
        "RETURN i.short_form AS vfb_id, r.accession[0] AS acc"
        % (site, _quote_list(vfb_ids)))
    rows = dict_cursor(_get_nc().commit_list([query]))
    return {row["vfb_id"]: str(row["acc"]) for row in rows or []
            if row.get("acc") is not None}


def skids_to_vfb_ids(skids, site):
    """{skid: vfb_id} for the given skids on one KB xref site."""
    skids = sorted({str(s) for s in skids})
    if not skids:
        return {}
    query = (
        "MATCH (s:Site {short_form: '%s'})<-[r:database_cross_reference]"
        "-(i:Entity) WHERE r.accession[0] IN %s "
        "RETURN r.accession[0] AS acc, i.short_form AS vfb_id"
        % (site, _quote_list(skids)))
    rows = dict_cursor(_get_nc().commit_list([query]))
    return {str(row["acc"]): row["vfb_id"] for row in rows or []}


def _truthy(value):
    """Truthiness that also understands HTTP-style string flags."""
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes")
    return bool(value)


def list_aligned_templates(vfb_id):
    """Template registrations of one VFB individual's image.

    :return: list of ``{"template": short_form, "label": label,
        "folder": url}`` — one entry per template space VFB has this
        image registered to. The aligned SWC, where one exists, is
        ``folder + 'volume.swc'``.
    """
    if not _VFB_ID_RE.match(vfb_id or ""):
        raise ValueError("'%s' is not a VFB id" % vfb_id)
    query = (
        "MATCH (n:Individual {short_form: '%s'})<-[:depicts]-(c:Individual)"
        "-[ir:in_register_with]->(tc:Individual)-[:depicts]->(t:Individual) "
        "RETURN t.short_form AS template, t.label AS label, "
        "ir.folder[0] AS folder" % vfb_id)
    rows = dict_cursor(_get_nc().commit_list([query]))
    return [{"template": r["template"], "label": r.get("label"),
             "folder": r["folder"]} for r in rows or [] if r.get("folder")]


def _collect_skid_like_keys(obj, found, limit):
    """Recursively collect dict keys that look like skids (bounded)."""
    if len(found) >= limit:
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(key, (str, int)) and _SKID_RE.match(str(key)):
                found.add(str(key))
                if len(found) >= limit:
                    return
            _collect_skid_like_keys(value, found, limit)
    elif isinstance(obj, list):
        for item in obj[:limit]:
            _collect_skid_like_keys(item, found, limit)


# ---------------------------------------------------------------------------
# The instance client
# ---------------------------------------------------------------------------

class CatmaidInstance:
    """A client for one VFB-hosted CATMAID instance.

    Usually obtained via :func:`catmaid`::

        import vfbquery as vfb
        fafb = vfb.catmaid('fafb')
        fafb.connectivity(ids=['VFB_001011rj', 10603863])
        fafb.swc(id='VFB_001011rj', raw=True)

    Every registry command is callable as a method (or through
    :meth:`call`); extra keyword arguments are forwarded to CATMAID
    verbatim under CATMAID's own parameter names.
    """

    def __init__(self, instance, project=None):
        instances = _instances_by_id()
        if instance not in instances:
            raise ValueError(
                "Unknown CATMAID instance '%s'. Hosted instances: %s"
                % (instance, ", ".join(sorted(instances))))
        self._meta = instances[instance]
        self.instance = instance
        self.base_url = self._meta["url"].rstrip("/")
        self.token = self._meta.get("api_token")
        projects = {int(p["id"]): p for p in self._meta.get("projects", [])}
        if project is None:
            self.project_id = min(projects) if projects else 1
        else:
            project = int(project)
            if projects and project not in projects:
                raise ValueError(
                    "Instance '%s' has no project %d. Projects: %s"
                    % (instance, project,
                       ", ".join("%d (%s)" % (i, p.get("title", ""))
                                 for i, p in sorted(projects.items()))))
            self.project_id = project
        #: {project_id: project dict} — deliberately NOT named ``projects``,
        #: which is the registry command listing the instance's projects.
        self.project_map = projects

    # -- metadata -----------------------------------------------------------

    @property
    def xref_db(self):
        """KB Site short_form holding skid xrefs for this project, or None."""
        return _xref_site_map().get((self.instance, self.project_id))

    def commands(self):
        """{command: doc} for every command this pass-through offers."""
        return {name: spec["doc"] for name, spec in
                sorted(CATMAID_COMMANDS.items())}

    # -- id conversion ------------------------------------------------------

    def resolve_ids(self, ids):
        """Split/convert a mixed id list.

        :return: (skids, id_map, unmatched) — ``skids`` in input order where
            possible, ``id_map`` {vfb_id: skid} for converted inputs,
            ``unmatched`` the VFB ids that had no skid xref here.
        """
        items = _as_id_list(ids)
        vfb_ids = [i for i in items if _VFB_ID_RE.match(i)]
        id_map, unmatched = {}, []
        if vfb_ids:
            site = self.xref_db
            if site is None:
                raise ValueError(
                    "Instance '%s' (project %d) has no VFB skid cross-"
                    "references in the knowledge graph — pass CATMAID "
                    "skeleton ids instead of VFB ids (%s)"
                    % (self.instance, self.project_id, ", ".join(vfb_ids)))
            id_map = vfb_ids_to_skids(vfb_ids, site)
            unmatched = [v for v in vfb_ids if v not in id_map]
        skids = [id_map.get(i, i) for i in items if i not in unmatched]
        return skids, id_map, unmatched

    def _skid_to_neuron_id(self, skid):
        """CATMAID neuron id for one skid, via neurons/from-models."""
        data = self._request(
            "POST", "/%d/neurons/from-models" % self.project_id,
            {"model_ids[0]": skid})
        payload = data["body"]
        if isinstance(payload, dict) and str(skid) in payload:
            return payload[str(skid)]
        raise ValueError("CATMAID has no neuron for skeleton id %s on '%s'"
                         % (skid, self.instance))

    # -- aligned SWC from the VFB image store -------------------------------

    def _aligned_swc(self, id, choice, raw=False, extra=None):
        """VFB's template-registered SWC for one neuron.

        CATMAID serves skeletons in the dataset's own EM space; VFB also
        stores a copy registered to a standard template (``volume.swc`` in
        the image's ``in_register_with`` folder). ``choice`` names the
        template — short_form (``VFB_00101567``) or label
        (``JRC2018Unisex``), case-insensitively — or is one of the generic
        values (``vfb``/``true``), which work only while the image is
        registered to a single template; once a neuron has several
        registrations (e.g. JRC2018U plus a unified brain+VNC space) the
        generic form errors and lists the choices instead of guessing.
        """
        if extra:
            raise ValueError(
                "aligned= takes only id= — unexpected: %s"
                % ", ".join(sorted(extra)))
        items = _as_id_list(id)
        if len(items) != 1:
            raise ValueError("aligned= takes exactly one id")
        item = items[0]
        id_map = {}
        if _VFB_ID_RE.match(item):
            vfb_id = item
        else:
            site = self.xref_db
            if site is None:
                raise ValueError(
                    "Instance '%s' (project %d) has no VFB skid cross-"
                    "references, so an aligned copy cannot be looked up "
                    "from a skeleton id — none exists without a VFB record"
                    % (self.instance, self.project_id))
            mapping = skids_to_vfb_ids([item], site)
            if item not in mapping:
                raise ValueError(
                    "Skeleton id %s has no VFB record on '%s', so VFB "
                    "holds no aligned copy" % (item, self.instance))
            vfb_id = mapping[item]
            id_map = {vfb_id: item}

        registrations = list_aligned_templates(vfb_id)
        if not registrations:
            raise ValueError("VFB holds no template-registered image for %s"
                             % vfb_id)
        available = ", ".join("%s (%s)" % (r["template"], r["label"])
                              for r in registrations)
        generic = (choice is True or
                   str(choice).strip().lower() in ("true", "1", "yes", "vfb"))
        if generic:
            if len(registrations) > 1:
                raise ValueError(
                    "%s is registered to %d templates — pass "
                    "aligned=<template short_form or label>: %s"
                    % (vfb_id, len(registrations), available))
            chosen = registrations
        else:
            want = str(choice).strip().lower()
            chosen = [r for r in registrations
                      if r["template"].lower() == want
                      or (r.get("label") or "").lower() == want]
            if not chosen:
                raise ValueError(
                    "%s is not registered to template '%s'. Available: %s"
                    % (vfb_id, choice, available))
        reg = chosen[0]
        url = reg["folder"].rstrip("/") + "/volume.swc"
        if url.startswith("http://"):
            url = "https://" + url[len("http://"):]
        resp = _http_session().get(url, timeout=CATMAID_TIMEOUT)
        if resp.status_code != 200:
            raise ValueError(
                "No aligned SWC for %s in %s (%s returned %d) — the image "
                "may not have a skeleton representation"
                % (vfb_id, reg["label"], url, resp.status_code))
        swc_text = resp.content.decode("utf-8", "replace")
        if raw:
            return swc_text
        return {
            "instance": self.instance,
            "project_id": self.project_id,
            "command": "swc",
            "aligned": True,
            "template": {"short_form": reg["template"], "label": reg["label"]},
            "xref_db": self.xref_db,
            "id_map": id_map,
            "unmatched": [],
            "reverse_map": {v: k for k, v in id_map.items()},
            "notes": ["aligned SWC served from the VFB image store: %s" % url],
            "result": swc_text,
        }

    # -- HTTP ---------------------------------------------------------------

    def _request(self, method, path, params):
        url = self.base_url + path
        headers = {}
        if self.token:
            headers["X-Authorization"] = "Token %s" % self.token
        if method == "GET":
            resp = _http_session().get(url, params=params, headers=headers,
                                       timeout=CATMAID_TIMEOUT)
        else:
            resp = _http_session().post(url, data=params, headers=headers,
                                        timeout=CATMAID_TIMEOUT)
        content_type = resp.headers.get("Content-Type", "")
        if resp.status_code >= 400:
            detail = resp.text[:500]
            raise RuntimeError(
                "CATMAID %s %s returned %d: %s"
                % (method, path, resp.status_code, detail))
        if "json" in content_type:
            body = resp.json()
            # CATMAID reports many errors as 200 + {"error": ...}
            if isinstance(body, dict) and body.get("error"):
                raise RuntimeError("CATMAID error on %s %s: %s"
                                   % (method, path, body.get("error")))
            return {"body": body, "kind": "json"}
        return {"body": resp.content, "kind": "raw"}

    # -- the pass-through ---------------------------------------------------

    def call(self, command, raw=False, **kwargs):
        """Run one registry command; see the module docstring for the
        envelope. ``raw=True`` returns the untouched CATMAID response."""
        spec = CATMAID_COMMANDS.get(command)
        if spec is None:
            raise ValueError(
                "Unknown CATMAID command '%s'. Available: %s"
                % (command, ", ".join(sorted(CATMAID_COMMANDS))))

        # swc has one option CATMAID itself cannot serve: VFB's template-
        # registered copy of the skeleton, downloaded from the VFB image
        # store instead of CATMAID. aligned= names the template (short_form
        # or label); "original"/"catmaid"/falsy mean the CATMAID original.
        if command == "swc":
            choice = kwargs.pop("aligned", None)
            if choice is not None and not (
                    choice is False or
                    str(choice).strip().lower() in
                    ("", "false", "0", "no", "original", "catmaid")):
                return self._aligned_swc(kwargs.pop("id", None), choice,
                                         raw=raw, extra=kwargs)

        path_slots = {"project_id": self.project_id}
        params = {}
        id_map, unmatched = {}, []
        notes = []

        # Declared skid-list parameters.
        for public, wire in (spec.get("id_params") or {}).items():
            if public not in kwargs:
                raise ValueError("Command '%s' requires '%s' (skeleton ids "
                                 "and/or VFB ids)" % (command, public))
            skids, this_map, this_unmatched = self.resolve_ids(
                kwargs.pop(public))
            id_map.update(this_map)
            unmatched.extend(this_unmatched)
            if not skids:
                raise ValueError(
                    "No usable ids for '%s' after conversion (unmatched: %s)"
                    % (public, ", ".join(unmatched) or "none"))
            for i, skid in enumerate(skids):
                params[wire.format(i=i)] = skid

        # Single path id (skid or neuron id).
        if spec.get("id_path"):
            if "id" not in kwargs:
                raise ValueError("Command '%s' requires 'id' (one skeleton id "
                                 "or VFB id)" % command)
            skids, this_map, this_unmatched = self.resolve_ids(
                kwargs.pop("id"))
            id_map.update(this_map)
            unmatched.extend(this_unmatched)
            if len(skids) != 1:
                raise ValueError(
                    "Command '%s' takes exactly one resolvable id "
                    "(got %d usable; unmatched: %s)"
                    % (command, len(skids), ", ".join(unmatched) or "none"))
            slot, kind = spec["id_path"]["slot"], spec["id_path"]["kind"]
            value = skids[0]
            if kind == "neuron_id":
                neuron_id = self._skid_to_neuron_id(value)
                notes.append("neuron_id %s derived from skeleton id %s"
                             % (neuron_id, value))
                value = neuron_id
            path_slots[slot] = value

        # Other raw path parameters (treenode_id etc.).
        for name in spec.get("path_params") or []:
            if name not in kwargs:
                raise ValueError("Command '%s' requires '%s'" % (command, name))
            path_slots[name] = str(kwargs.pop(name)).strip("/")

        # Everything else goes to CATMAID verbatim.
        for key, value in kwargs.items():
            if isinstance(value, bool):
                value = "true" if value else "false"
            params[str(key)] = value

        path = spec["path"].format(**path_slots)
        response = self._request(spec["method"], path, params)

        returns = spec.get("returns", "json")
        if response["kind"] == "json":
            result = response["body"]
        elif returns == "bytes":
            result = base64.b64encode(response["body"]).decode("ascii")
            notes.append("binary response, base64-encoded")
        else:
            result = response["body"].decode("utf-8", "replace")

        if raw:
            return result

        envelope = {
            "instance": self.instance,
            "project_id": self.project_id,
            "command": command,
            "xref_db": self.xref_db,
            "id_map": id_map,
            "unmatched": sorted(set(unmatched)),
            "result": result,
        }
        if notes:
            envelope["notes"] = notes

        # Reverse-map skid-shaped keys found in the result back to VFB ids —
        # cheap (one batched KB query) and only where xrefs exist at all.
        site = self.xref_db
        if site and isinstance(result, (dict, list)):
            found = set()
            _collect_skid_like_keys(result, found, MAX_REVERSE_LOOKUP)
            found.update(id_map.values())
            if found:
                try:
                    envelope["reverse_map"] = skids_to_vfb_ids(found, site)
                except Exception as exc:
                    log.warning("reverse skid->VFB lookup failed: %s", exc)
                    envelope["reverse_map"] = {
                        v: k for k, v in id_map.items()}
        elif id_map:
            envelope["reverse_map"] = {v: k for k, v in id_map.items()}
        return envelope

    def __getattr__(self, name):
        if name in CATMAID_COMMANDS:
            def _bound(**kwargs):
                return self.call(name, **kwargs)
            _bound.__name__ = name
            _bound.__doc__ = CATMAID_COMMANDS[name]["doc"]
            return _bound
        raise AttributeError(
            "%r object has no attribute %r (not a CATMAID command either — "
            "see .commands())" % (type(self).__name__, name))

    def __dir__(self):
        return sorted(set(list(super().__dir__()) + list(CATMAID_COMMANDS)))


# ---------------------------------------------------------------------------
# Public module-level API
# ---------------------------------------------------------------------------

def catmaid(instance, project=None):
    """A :class:`CatmaidInstance` for one hosted instance (e.g. ``'fafb'``)."""
    return CatmaidInstance(instance, project=project)


def list_catmaid_instances():
    """Metadata for every VFB-hosted CATMAID instance.

    Straight from catmaid.json, with each project annotated with the KB
    xref site (``vfb_xref_db``) used for VFB id <-> skid conversion, or
    None where the KB holds no skid xrefs (skid-only access).
    """
    config = get_catmaid_config()
    try:
        site_map = _xref_site_map()
    except Exception:
        site_map = dict(_STATIC_XREF_SITES)
    instances = []
    for inst in config.get("instances", []):
        entry = {k: inst.get(k) for k in
                 ("id", "name", "description", "url", "api_documentation",
                  "more_information", "api_token")}
        entry["projects"] = [
            dict(p, vfb_xref_db=site_map.get((inst.get("id"), int(p["id"]))))
            for p in inst.get("projects", [])]
        instances.append(entry)
    return {
        "name": config.get("name"),
        "description": config.get("description"),
        "source": CATMAID_JSON_URL,
        "homepage": config.get("homepage"),
        "citation": config.get("citation"),
        "authentication": config.get("authentication"),
        "instances": instances,
    }


def list_catmaid_commands():
    """{command: {method, path, doc, takes}} for the whole registry."""
    out = {}
    for name, spec in sorted(CATMAID_COMMANDS.items()):
        takes = list(spec.get("id_params") or [])
        if spec.get("id_path"):
            takes.append("id")
        takes.extend(spec.get("path_params") or [])
        out[name] = {"method": spec["method"], "path": spec["path"],
                     "doc": spec["doc"], "takes_ids": takes,
                     "returns": spec.get("returns", "json")}
    return out


def run_catmaid_command(instance, command, project=None, raw=False, **kwargs):
    """Module-level convenience (and the ha_api worker entry point)."""
    return CatmaidInstance(instance, project=project).call(
        command, raw=raw, **kwargs)
