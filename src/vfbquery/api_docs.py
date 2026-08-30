"""
Interactive API documentation for the VFBquery HA server.

Two artefacts, both served by :mod:`vfbquery.ha_api`:

* :func:`build_docs_spec` — the machine-readable endpoint catalogue
  (``GET /docs.json``). The static endpoint descriptions live here in
  :data:`ENDPOINT_GROUPS`; the caller injects the vocabularies that belong
  to other modules (the ``run_query`` query types, the CATMAID command
  registry) so this module imports neither.
* :data:`DOCS_HTML` — a self-contained page (``GET /``) in the style of the
  VFB-hosted CATMAID ``/apis/`` pages and virtualflybrain.org (the
  vfb-nova palette): every endpoint with its parameters, pre-filled
  runnable examples, and live results fetched from the same origin.

Keeping the HTML as a module string (rather than package data) means the
page survives every packaging route — wheel, sdist, Docker COPY — without
a ``MANIFEST.in`` entry to forget.
"""

# ---------------------------------------------------------------------------
# Endpoint catalogue
#
# Parameter fields: name, doc, required (default False), example (pre-filled
# in the form), enum (renders a dropdown; "dynamic:<key>" pulls the list
# injected by build_docs_spec).
# ---------------------------------------------------------------------------

ENDPOINT_GROUPS = [
    {
        "group": "Term information",
        "endpoints": [
            {
                "path": "/get_term_info",
                "summary": "Full term report for one VFB/FBbt id",
                "description": (
                    "The report behind the website's term information panel: "
                    "metadata, synonyms, relationships, aligned images, "
                    "cross-references, and the list of queries that can be "
                    "run from the term."),
                "params": [
                    {"name": "id", "required": True,
                     "doc": "Ontology class or individual short_form",
                     "example": "FBbt_00003748"},
                    {"name": "force_refresh",
                     "doc": "true bypasses the result cache",
                     "example": ""},
                ],
            },
            {
                "path": "/run_query",
                "summary": "Run one of a term's named queries",
                "description": (
                    "Executes one of the query types listed in a term's "
                    "Queries section (see /get_term_info). Results are the "
                    "website's own row format; offset/limit page them."),
                "params": [
                    {"name": "id", "required": True,
                     "doc": "Term the query starts from",
                     "example": "FBbt_00003748"},
                    {"name": "query_type", "required": True,
                     "doc": "One of the named query types",
                     "example": "ListAllAvailableImages",
                     "enum": "dynamic:query_types"},
                    {"name": "offset", "doc": "First row to return",
                     "example": ""},
                    {"name": "limit", "doc": "Maximum rows to return",
                     "example": ""},
                    {"name": "include_graph",
                     "doc": "true adds a graph rendering of the rows",
                     "example": ""},
                    {"name": "force_refresh",
                     "doc": "true bypasses the result cache", "example": ""},
                ],
            },
            {
                "path": "/get_hierarchy",
                "summary": "Partonomy / subclass tree around a term",
                "description": (
                    "The hierarchy browser's tree: follow one relationship "
                    "from a term, upward, downward or both."),
                "params": [
                    {"name": "id", "required": True, "doc": "Root term",
                     "example": "FBbt_00005801"},
                    {"name": "relationship",
                     "doc": "part_of (default) or subclass_of",
                     "example": "part_of"},
                    {"name": "direction",
                     "doc": "up, down or both", "example": "both"},
                    {"name": "max_depth", "doc": "Levels to expand",
                     "example": "1"},
                ],
            },
        ],
    },
    {
        "group": "Search and identifiers",
        "endpoints": [
            {
                "path": "/search",
                "summary": "Website-equivalent free-text search",
                "description": (
                    "The canonical ranked search the site uses. filter/"
                    "exclude/boost/demote take type names — GET /facets "
                    "lists every accepted name."),
                "params": [
                    {"name": "query", "required": True,
                     "doc": "Free text", "example": "medulla"},
                    {"name": "limit", "doc": "Rows to return", "example": "10"},
                    {"name": "filter_types",
                     "doc": "Only these types (comma-separated)",
                     "example": ""},
                    {"name": "exclude_types", "doc": "Drop these types",
                     "example": ""},
                    {"name": "boost_types", "doc": "Rank these types higher",
                     "example": ""},
                    {"name": "demote_types", "doc": "Rank these types lower",
                     "example": ""},
                ],
            },
            {
                "path": "/facets",
                "summary": "Type names /search accepts",
                "description": ("The vocabulary for /search's four type "
                                "parameters."),
                "params": [
                    {"name": "contains",
                     "doc": "Only names containing this text",
                     "example": ""},
                ],
            },
            {
                "path": "/xref",
                "summary": "VFB id ↔ external accession",
                "description": (
                    "Both directions of the cross-reference mapping. Give "
                    "id= for VFB → external, or accession= (optionally with "
                    "db=) for external → VFB."),
                "params": [
                    {"name": "id",
                     "doc": "VFB id (forward direction)",
                     "example": "VFB_001011rj"},
                    {"name": "accession",
                     "doc": "External id (reverse direction)", "example": ""},
                    {"name": "db",
                     "doc": "Restrict to one site (name, symbol or nickname)",
                     "example": ""},
                ],
            },
            {
                "path": "/combine",
                "summary": "Set algebra over query results",
                "description": (
                    "Combine two or more named queries with OR/AND/NOT/XOR "
                    "(and friends), compared on term id. Name each operand "
                    "as its own parameter, then reference the names in "
                    "expr. The response traces every step."),
                "params": [
                    {"name": "expr", "required": True,
                     "doc": "Boolean expression over the operand names",
                     "example": "calyx AND lh"},
                    {"name": "calyx",
                     "doc": "Example operand (any name works)",
                     "example": "NeuronsPartHere:FBbt_00007401"},
                    {"name": "lh", "doc": "Example operand",
                     "example": "NeuronsPartHere:FBbt_00007053"},
                ],
            },
        ],
    },
    {
        "group": "Connectivity",
        "endpoints": [
            {
                "path": "/list_connectome_datasets",
                "summary": "Connectome datasets in the knowledge graph",
                "description": ("The datasets /query_connectivity can draw "
                                "on, with their labels and symbols."),
                "params": [],
            },
            {
                "path": "/query_connectivity",
                "summary": "Synaptic connectivity between neuron types",
                "description": (
                    "Connections from one neuron type (or any subclass) to "
                    "another, summed across the connectomes. Types are "
                    "labels, synonyms or FBbt ids."),
                "params": [
                    {"name": "upstream_type", "required": True,
                     "doc": "Presynaptic type (label, synonym or FBbt id)",
                     "example": "LPLC2"},
                    {"name": "downstream_type", "required": True,
                     "doc": "Postsynaptic type",
                     "example": "giant fiber neuron"},
                    {"name": "weight",
                     "doc": "Minimum synapse count per connection",
                     "example": ""},
                    {"name": "group_by_class",
                     "doc": "true groups rows by neuron class",
                     "example": ""},
                    {"name": "exclude_dbs",
                     "doc": "Datasets to leave out (comma-separated)",
                     "example": ""},
                    {"name": "include_graph",
                     "doc": "true adds a graph rendering", "example": ""},
                ],
            },
        ],
    },
    {
        "group": "FlyBase stocks and combinations",
        "endpoints": [
            {
                "path": "/resolve_entity",
                "summary": "Resolve a gene/allele/transgene name",
                "description": ("Free-text resolver for FlyBase features; "
                                "returns candidate ids for /find_stocks."),
                "params": [
                    {"name": "query", "required": True,
                     "doc": "Name, symbol or FlyBase id", "example": "dpp"},
                ],
            },
            {
                "path": "/find_stocks",
                "summary": "Stocks carrying a FlyBase feature",
                "description": ("Stock-centre holdings for a resolved "
                                "feature id."),
                "params": [
                    {"name": "id", "required": True,
                     "doc": "FlyBase feature id from /resolve_entity",
                     "example": "FBgn0000490"},
                    {"name": "collection",
                     "doc": "Restrict to one stock collection",
                     "example": ""},
                ],
            },
            {
                "path": "/resolve_combination",
                "summary": "Resolve a split-GAL4 combination",
                "description": ("Resolver for hemidriver combinations "
                                "(FBco ids)."),
                "params": [
                    {"name": "query", "required": True,
                     "doc": "Combination name or synonym",
                     "example": "GMR37H08-ZpGAL4DBD in attP2"},
                ],
            },
            {
                "path": "/find_combo_publications",
                "summary": "Publications for a combination",
                "description": ("Publications using a resolved FBco "
                                "combination."),
                "params": [
                    {"name": "id", "required": True,
                     "doc": "FBco id from /resolve_combination",
                     "example": "FBco0000052"},
                ],
            },
        ],
    },
    {
        "group": "CATMAID pass-through",
        "endpoints": [
            {
                "path": "/catmaid",
                "summary": "The VFB-hosted CATMAID instances",
                "description": (
                    "Every hosted instance with its metadata, projects, "
                    "anonymous read-only token, and the knowledge-graph "
                    "cross-reference site used for VFB id ↔ skeleton id "
                    "conversion."),
                "params": [],
            },
            {
                "path": "/catmaid/{instance}",
                "summary": "One instance's metadata and commands",
                "description": ("Instance details plus the full command "
                                "registry with per-command documentation."),
                "path_params": [
                    {"name": "instance", "required": True,
                     "doc": "Instance id (see /catmaid)",
                     "example": "fafb", "enum": "dynamic:catmaid_instances"},
                ],
                "params": [],
            },
            {
                "path": "/catmaid/{instance}/{command}",
                "summary": "Run a read-only CATMAID command",
                "description": (
                    "The curated CATMAID query surface. Commands taking "
                    "skeleton ids accept CATMAID skids, VFB ids, or a mixed "
                    "comma-separated list — VFB ids are converted through "
                    "the knowledge graph before the request is made, and "
                    "the response envelope maps ids both ways. raw=true "
                    "returns the untouched CATMAID payload. Unrecognised "
                    "parameters are forwarded to CATMAID verbatim. For swc, "
                    "aligned= names a template space for VFB's registered "
                    "copy, and the swc_alignments command lists the spaces "
                    "available."),
                "path_params": [
                    {"name": "instance", "required": True,
                     "doc": "Instance id (see /catmaid)",
                     "example": "fafb", "enum": "dynamic:catmaid_instances"},
                    {"name": "command", "required": True,
                     "doc": "Command name (see the registry below)",
                     "example": "neuron_names",
                     "enum": "dynamic:catmaid_commands"},
                ],
                "params": [
                    {"name": "ids",
                     "doc": "Skeleton ids and/or VFB ids, comma-separated "
                            "(list commands)",
                     "example": "VFB_001011rj,10603863"},
                    {"name": "id",
                     "doc": "One skeleton id or VFB id (single-id commands)",
                     "example": ""},
                    {"name": "project",
                     "doc": "CATMAID project id (defaults to the "
                            "instance's first project)", "example": ""},
                    {"name": "raw",
                     "doc": "true returns the untouched CATMAID response",
                     "example": ""},
                ],
            },
        ],
    },
    {
        "group": "Service",
        "endpoints": [
            {
                "path": "/health",
                "summary": "Liveness and running version",
                "description": "",
                "params": [],
            },
            {
                "path": "/status",
                "summary": "Queue depth, cache stats, worker utilisation",
                "description": "",
                "params": [],
            },
        ],
    },
]


def build_docs_spec(version, query_types=None, catmaid_commands=None):
    """The ``/docs.json`` payload.

    :param version: running package version (shown in the page header).
    :param query_types: sorted /run_query query_type vocabulary.
    :param catmaid_commands: ``{command: {method, path, doc, ...}}`` from
        :func:`vfbquery.catmaid_client.list_catmaid_commands`.
    """
    return {
        "name": "VFBquery API",
        "version": version,
        "description": (
            "Query services for Virtual Fly Brain — term information, "
            "search, connectivity, cross-references, FlyBase stocks and the "
            "hosted-CATMAID pass-through. All endpoints are read-only GETs "
            "returning JSON."),
        "documentation": "https://vfbquery.readthedocs.io",
        "source": "https://github.com/VirtualFlyBrain/VFBquery",
        "groups": ENDPOINT_GROUPS,
        "vocabularies": {
            "query_types": sorted(query_types or []),
            "catmaid_commands": catmaid_commands or {},
        },
    }


DOCS_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VFBquery API</title>
<style>
:root{
  --bg:#f6f8fc; --surface:#ffffff; --surface-2:#eef2f9;
  --text:#0b1220; --text-dim:#3d4c66; --muted:#5d6d8b;
  --line:rgba(11,18,32,.12); --line-soft:rgba(11,18,32,.07);
  --brand:#4c8dff; --brand-ink:#1d5fd6; --cyan:#35e7e0; --violet:#a46bff;
  --ok:#1a9e6c; --err:#d64545;
  --grad-brand:linear-gradient(115deg,var(--violet) 0%,var(--brand) 45%,var(--cyan) 100%);
  --font-body:"Inter var",Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
  --font-display:"Space Grotesk var","Space Grotesk",ui-sans-serif,system-ui,sans-serif;
  --font-mono:"JetBrains Mono var",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#05070e; --surface:#0b1120; --surface-2:#121a2e;
    --text:#e8edf7; --text-dim:#aeb9cf; --muted:#7f8fad;
    --line:rgba(255,255,255,.10); --line-soft:rgba(255,255,255,.06);
    --brand-ink:#7fb0ff; --ok:#3fd095; --err:#ff7b7b;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font-body);font-size:15px;line-height:1.55}
a{color:var(--brand-ink);text-decoration:none}
a:hover{text-decoration:underline}
code,pre,input,select{font-family:var(--font-mono)}
header{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--line);padding:0 20px}
.nav{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:14px;height:64px}
.mark{width:34px;height:34px;border-radius:9px;background:var(--grad-brand);display:inline-flex;align-items:center;justify-content:center;color:#fff;font-family:var(--font-display);font-weight:700;font-size:15px}
.brand{display:flex;flex-direction:column;line-height:1.15}
.brand b{font-family:var(--font-display);font-size:16px}
.brand span{font-size:12px;color:var(--muted)}
.nav .links{margin-left:auto;display:flex;gap:16px;font-size:13.5px}
.wrap{max-width:1200px;margin:0 auto;padding:26px 20px;display:grid;grid-template-columns:230px 1fr;gap:30px}
@media (max-width:860px){.wrap{grid-template-columns:1fr}.toc{display:none}}
.toc{position:sticky;top:84px;align-self:start;font-size:13.5px}
.toc h4{margin:14px 0 6px;font-family:var(--font-display);font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
.toc a{display:block;padding:2px 0;color:var(--text-dim)}
.lede{margin:0 0 6px;font-family:var(--font-display);font-size:28px}
.lede small{font-size:14px;color:var(--muted);font-family:var(--font-body);font-weight:400}
.sub{color:var(--text-dim);max-width:72ch;margin-top:4px}
h2.group{font-family:var(--font-display);font-size:19px;margin:34px 0 4px;padding-top:10px;border-top:1px solid var(--line-soft)}
.ep{background:var(--surface);border:1px solid var(--line);border-radius:12px;margin:14px 0;overflow:hidden}
.ep summary{list-style:none;cursor:pointer;display:flex;align-items:baseline;gap:12px;padding:12px 16px}
.ep summary::-webkit-details-marker{display:none}
.ep summary:hover{background:var(--surface-2)}
.method{font-family:var(--font-mono);font-size:11px;font-weight:700;color:#fff;background:var(--brand);border-radius:5px;padding:2px 7px}
.path{font-family:var(--font-mono);font-size:14px;font-weight:600}
.summ{color:var(--muted);font-size:13.5px;margin-left:auto;text-align:right}
.ep .body{padding:4px 16px 16px;border-top:1px solid var(--line-soft)}
.desc{color:var(--text-dim);max-width:78ch}
table.params{border-collapse:collapse;width:100%;margin:10px 0;font-size:13.5px}
table.params th{text-align:left;color:var(--muted);font-weight:600;padding:4px 10px 4px 0;border-bottom:1px solid var(--line-soft)}
table.params td{padding:5px 10px 5px 0;border-bottom:1px solid var(--line-soft);vertical-align:middle}
table.params input,table.params select{width:100%;max-width:340px;background:var(--bg);color:var(--text);border:1px solid var(--line);border-radius:7px;padding:5px 8px;font-size:13px}
.req{color:var(--err);font-size:11px;margin-left:4px}
.runrow{display:flex;align-items:center;gap:12px;margin-top:10px;flex-wrap:wrap}
button.run{background:var(--grad-brand);color:#fff;border:0;border-radius:8px;padding:8px 22px;font-family:var(--font-display);font-weight:600;font-size:14px;cursor:pointer}
button.run:hover{filter:brightness(1.08)}
.url{font-family:var(--font-mono);font-size:12px;color:var(--muted);word-break:break-all}
.meta{font-size:12.5px;color:var(--muted)}
.meta .ok{color:var(--ok);font-weight:600}
.meta .bad{color:var(--err);font-weight:600}
pre.result{background:var(--surface-2);border:1px solid var(--line-soft);border-radius:9px;padding:12px;max-height:440px;overflow:auto;font-size:12.5px;white-space:pre-wrap;word-break:break-word}
.cmds{font-size:13px;margin-top:8px}
.cmds td{padding:3px 12px 3px 0;border-bottom:1px solid var(--line-soft);vertical-align:top}
.cmds code{color:var(--brand-ink)}
footer{border-top:1px solid var(--line);margin-top:40px;padding:22px 20px;color:var(--muted);font-size:13px;text-align:center}
</style>
</head>
<body>
<header><div class="nav">
  <span class="mark">VFB</span>
  <span class="brand"><b>Virtual Fly Brain</b><span>VFBquery API</span></span>
  <nav class="links">
    <a href="https://vfbquery.readthedocs.io">Documentation</a>
    <a href="https://github.com/VirtualFlyBrain/VFBquery">Source</a>
    <a href="https://virtualflybrain.org">virtualflybrain.org</a>
  </nav>
</div></header>

<div class="wrap">
  <nav class="toc" id="toc"></nav>
  <main>
    <h1 class="lede">VFBquery API <small id="version"></small></h1>
    <p class="sub" id="lede-desc">Loading endpoint catalogue…</p>
    <p class="sub">Edit the pre-filled parameters and press <b>Run</b> to
      call this server and see the live result. The machine-readable
      catalogue is at <a href="docs.json"><code>/docs.json</code></a>.</p>
    <div id="groups"></div>
  </main>
</div>

<footer>
  <a href="https://virtualflybrain.org">Virtual Fly Brain</a> ·
  served by <span id="footer-version">vfbquery</span> ·
  please cite <a href="https://doi.org/10.3389/fphys.2023.1076533">Court et al. (2023)</a>
</footer>

<script>
"use strict";
let SPEC = null;

function el(tag, attrs, ...children){
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})){
    if (key === "text") node.textContent = value;
    else node.setAttribute(key, value);
  }
  for (const child of children) if (child) node.append(child);
  return node;
}

function slug(path){ return "ep" + path.replace(/[^a-z0-9]+/gi, "-"); }

function optionList(select, values, chosen){
  select.append(el("option", {value: "", text: ""}));
  for (const value of values){
    const opt = el("option", {value: value, text: value});
    if (value === chosen) opt.selected = true;
    select.append(opt);
  }
}

function paramRow(param, kind){
  const vocab = SPEC.vocabularies || {};
  let input;
  if (param.enum && String(param.enum).startsWith("dynamic:")){
    const key = param.enum.split(":")[1];
    let values = [];
    if (key === "query_types") values = vocab.query_types || [];
    if (key === "catmaid_commands") values = Object.keys(vocab.catmaid_commands || {});
    input = el("select", {"data-name": param.name, "data-kind": kind});
    optionList(input, values, param.example || "");
    if (key === "catmaid_instances"){   // filled lazily from /catmaid
      input.dataset.lazy = "catmaid_instances";
      if (param.example) optionList(input, [param.example], param.example);
    }
  } else {
    input = el("input", {"data-name": param.name, "data-kind": kind,
                         value: param.example || "", spellcheck: "false"});
  }
  return el("tr", null,
    el("td", null, el("code", {text: param.name}),
       param.required ? el("span", {class: "req", text: "required"}) : null),
    el("td", {class: "desc", text: param.doc || ""}),
    el("td", null, input));
}

function buildUrl(root, endpoint){
  let path = endpoint.path;
  const query = new URLSearchParams();
  for (const input of root.querySelectorAll("[data-name]")){
    const value = input.value.trim();
    if (input.dataset.kind === "path"){
      if (!value) return {error: input.dataset.name + " is required"};
      path = path.replace("{" + input.dataset.name + "}", encodeURIComponent(value));
    } else if (input.dataset.kind === "extra" && value){
      for (const pair of value.split("&")){
        const eq = pair.indexOf("=");
        if (eq > 0) query.append(pair.slice(0, eq), pair.slice(eq + 1));
      }
    } else if (value){
      query.append(input.dataset.name, value);
    }
  }
  const qs = query.toString();
  return {url: path + (qs ? "?" + qs : "")};
}

async function run(root, endpoint){
  const urlBox = root.querySelector(".url");
  const meta = root.querySelector(".meta");
  const out = root.querySelector("pre.result");
  const built = buildUrl(root, endpoint);
  if (built.error){ meta.innerHTML = '<span class="bad">' + built.error + "</span>"; return; }
  urlBox.textContent = new URL(built.url, window.location.href).href;
  meta.textContent = "running…";
  out.hidden = false;
  out.textContent = "";
  const started = performance.now();
  try {
    const resp = await fetch(built.url, {headers: {Accept: "application/json"}});
    const ms = Math.round(performance.now() - started);
    const text = await resp.text();
    let shown = text;
    try { shown = JSON.stringify(JSON.parse(text), null, 2); } catch (e) {}
    if (shown.length > 400000) shown = shown.slice(0, 400000) + "\n… (truncated for display)";
    meta.innerHTML = 'HTTP <span class="' + (resp.ok ? "ok" : "bad") + '">' +
      resp.status + "</span> · " + ms + " ms · " + text.length.toLocaleString() + " bytes";
    out.textContent = shown;
  } catch (err) {
    meta.innerHTML = '<span class="bad">request failed: ' + err + "</span>";
  }
}

function catmaidCommandTable(commands){
  const table = el("table", {class: "cmds"});
  for (const [name, info] of Object.entries(commands)){
    table.append(el("tr", null,
      el("td", null, el("code", {text: name})),
      el("td", {text: (info.local ? "(VFBquery) " : info.method + " " + info.path)}),
      el("td", {class: "desc", text: info.doc || ""})));
  }
  const details = el("details", null,
    el("summary", {text: "Command registry (" + Object.keys(commands).length + " commands)",
                   style: "cursor:pointer;color:var(--brand-ink);font-size:13.5px;margin-top:8px"}),
    table);
  return details;
}

function render(){
  document.getElementById("version").textContent = "v" + SPEC.version;
  document.getElementById("footer-version").textContent = "vfbquery " + SPEC.version;
  document.getElementById("lede-desc").textContent = SPEC.description;
  const toc = document.getElementById("toc");
  const groupsBox = document.getElementById("groups");
  for (const group of SPEC.groups){
    toc.append(el("h4", {text: group.group}));
    const heading = el("h2", {class: "group", id: "g-" + slug(group.group), text: group.group});
    groupsBox.append(heading);
    for (const endpoint of group.endpoints){
      toc.append(el("a", {href: "#" + slug(endpoint.path), text: endpoint.path}));
      const body = el("div", {class: "body"});
      if (endpoint.description) body.append(el("p", {class: "desc", text: endpoint.description}));
      const table = el("table", {class: "params"});
      const pathParams = endpoint.path_params || [];
      const queryParams = endpoint.params || [];
      if (pathParams.length + queryParams.length){
        table.append(el("tr", null, el("th", {text: "parameter"}),
                                    el("th", {text: ""}), el("th", {text: "value"})));
        for (const param of pathParams) table.append(paramRow(param, "path"));
        for (const param of queryParams) table.append(paramRow(param, "query"));
        table.append(paramRow({name: "extra", doc:
          "Additional parameters, passed verbatim (name=value&name2=value2)"}, "extra"));
        body.append(table);
      }
      if (endpoint.path === "/catmaid/{instance}/{command}")
        body.append(catmaidCommandTable(SPEC.vocabularies.catmaid_commands || {}));
      const meta = el("span", {class: "meta"});
      const runBtn = el("button", {class: "run", text: "Run"});
      body.append(el("div", {class: "runrow"}, runBtn, meta),
                  el("div", {class: "url"}),
                  el("pre", {class: "result", hidden: "hidden"}));
      const details = el("details", {class: "ep", id: slug(endpoint.path)},
        el("summary", null,
          el("span", {class: "method", text: "GET"}),
          el("span", {class: "path", text: endpoint.path}),
          el("span", {class: "summ", text: endpoint.summary || ""})),
        body);
      runBtn.addEventListener("click", () => run(body, endpoint));
      groupsBox.append(details);
    }
  }
  fillCatmaidInstances();
}

async function fillCatmaidInstances(){
  const selects = document.querySelectorAll('select[data-lazy="catmaid_instances"]');
  if (!selects.length) return;
  try {
    const resp = await fetch("catmaid", {headers: {Accept: "application/json"}});
    const listing = await resp.json();
    const ids = (listing.instances || []).map(inst => inst.id);
    for (const select of selects){
      const chosen = select.value;
      select.textContent = "";
      optionList(select, ids, chosen || "fafb");
    }
  } catch (err) { /* dropdown stays free-text-ish; the example still works */ }
}

fetch("docs.json", {headers: {Accept: "application/json"}})
  .then(resp => resp.json())
  .then(spec => { SPEC = spec; render(); })
  .catch(err => {
    document.getElementById("lede-desc").textContent =
      "Could not load /docs.json: " + err;
  });
</script>
</body>
</html>
"""
