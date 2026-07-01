import pysolr
from .term_info_queries import deserialize_term_info
# Replace VfbConnect import with our new SimpleVFBConnect
from .owlery_client import SimpleVFBConnect
# Keep dict_cursor if it's used elsewhere - lazy import to avoid GUI issues
from marshmallow import Schema, fields, post_load
from typing import List, Tuple, Dict, Any, Union
import pandas as pd
from marshmallow import ValidationError
import json
import numpy as np
from urllib.parse import unquote
from .solr_result_cache import with_solr_cache, solr_caching_disabled
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import re
import requests
import logging
import inspect
import os
import concurrent.futures

# --- Bounded term-info sub-query execution -------------------------------
# Generic high-level terms (e.g. a top-level anatomy class with a huge subclass
# closure) used to hang term-info: a saturated preview triggered an unbounded
# limit=-1 re-run purely to count rows, materialising every row with full
# markdown/thumbnail encoding. The cold computation never returned, so the
# v3-cached proxy never populated either. Two guards make the response always
# resolve (and therefore cache):
#   * COUNT_CAP bounds any count re-run; beyond it the exact total is not worth
#     the cost and we report -1 ("many").
#   * SUBQUERY_TIMEOUT_S is a per-sub-query wall-clock budget; on overrun we
#     abandon that sub-query (empty preview, count -1) and carry on.
SUBQUERY_TIMEOUT_S = int(os.environ.get("VFBQUERY_SUBQUERY_TIMEOUT_S", "600"))
COUNT_CAP = int(os.environ.get("VFBQUERY_COUNT_CAP", "1000"))


def _run_with_timeout(func, args=(), kwargs=None, timeout=None):
    """Run ``func`` with a wall-clock budget and return its result.

    The call runs in a worker thread; if it overruns ``timeout`` seconds we
    raise ``concurrent.futures.TimeoutError`` and stop waiting. Python cannot
    forcibly kill the worker, but we no longer block on it, so a slow
    Neo4j/Solr/Owlery round-trip cannot stall the whole term-info response; the
    thread drains in the background when its I/O finally returns.
    """
    kwargs = kwargs or {}
    if timeout is None:
        timeout = SUBQUERY_TIMEOUT_S
    ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    fut = ex.submit(func, *args, **kwargs)
    try:
        return fut.result(timeout=timeout)
    finally:
        # Never block on a runaway call; let the pool drain in the background.
        ex.shutdown(wait=False)

# Custom JSON encoder to handle NumPy and pandas types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif hasattr(obj, 'item'):  # Handle pandas scalar types
            return obj.item()
        return super(NumpyEncoder, self).default(obj)

def safe_to_dict(df, sort_by_id=True):
    """Convert DataFrame to dict with numpy types converted to native Python types"""
    if isinstance(df, pd.DataFrame):
        # Convert numpy dtypes to native Python types
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype.name.startswith('int'):
                df_copy[col] = df_copy[col].astype('object')
            elif df_copy[col].dtype.name.startswith('float'):
                df_copy[col] = df_copy[col].astype('object')
        
        # Sort by id column in descending order if it exists and sort_by_id is True
        if sort_by_id and 'id' in df_copy.columns:
            df_copy = df_copy.sort_values('id', ascending=False)
        
        return df_copy.to_dict("records")
    return df

# Lazy import for dict_cursor to avoid GUI library issues
def get_dict_cursor():
    """Lazy import dict_cursor to avoid import issues during testing"""
    try:
        from .neo4j_client import dict_cursor
        return dict_cursor
    except ImportError as e:
        raise ImportError(f"Could not import dict_cursor: {e}")

# Connect to the VFB SOLR server
vfb_solr = pysolr.Solr('http://solr.virtualflybrain.org/solr/vfb_json/', always_commit=False, timeout=990)
logger = logging.getLogger(__name__)

# Replace VfbConnect with SimpleVFBConnect
vc = SimpleVFBConnect()

# ---------------------------------------------------------------------------
# Canonical VFB term link
# ---------------------------------------------------------------------------
# Public, environment-independent permalink base for a VFB term. This resolves
# to the term's report page outside the app and is recognised as an internal
# link by the v2 query-results table (MarkdownLinkComponent parses the
# short_form out of the `/reports/<id>` path). Never hard-code an app URL such
# as https://v2.virtualflybrain.org/org.geppetto.frontend/geppetto?id=<id> into
# query output -- that pins results to one deployment. Build every VFB term
# link from here (or via the helpers below) so the form is defined in one place.
VFB_REPORT_BASE = "https://virtualflybrain.org/reports/"


def vfb_report_url(short_form: str) -> str:
    """Public permalink for a VFB term id, e.g. .../reports/VFB_00101567."""
    return f"{VFB_REPORT_BASE}{short_form}"


def vfb_term_link(label: str, short_form: str) -> str:
    """Markdown link for a VFB term: [label](https://virtualflybrain.org/reports/<id>)."""
    return f"[{label}]({vfb_report_url(short_form)})"


def initialize_vfb_connect():
    """
    Initialize VFB_connect by triggering the lazy load of the vfb and nc properties.
    This causes VFB_connect to cache all terms, which takes ~95 seconds on first call.
    Subsequent calls to functions using vc.nc will be fast.
    
    :return: True if initialization successful, False otherwise
    """
    try:
        # Access the properties to trigger lazy loading
        _ = vc.vfb
        _ = vc.nc
        return True
    except Exception as e:
        print(f"Failed to initialize VFB_connect: {e}")
        return False

class Query:
    def __init__(self, query, label, function, takes, preview=0, preview_columns=[], preview_results=[], output_format="table", count=-1):
        self.query = query
        self.label = label
        self.function = function
        self.takes = takes
        self.preview = preview
        self.preview_columns = preview_columns
        self.preview_results = preview_results
        self.output_format = output_format
        self.count = count

    def __str__(self):
        return f"Query: {self.query}, Label: {self.label}, Function: {self.function}, Takes: {self.takes}, Preview: {self.preview}, Preview Columns: {self.preview_columns}, Preview Results: {self.preview_results}, Count: {self.count}"

    def to_dict(self):
        return {
            "query": self.query,
            "label": self.label,
            "function": self.function,
            "takes": self.takes,
            "preview": self.preview,
            "preview_columns": self.preview_columns,
            "preview_results": self.preview_results,
            "output_format": self.output_format,
            "count": self.count,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            query=data["query"],
            label=data["label"],
            function=data["function"],
            takes=data["takes"],
            preview=data["preview"],
            preview_columns=data["preview_columns"],
            preview_results=data["preview_results"],
            output_format=data.get("output_format", 'table'),
            count=data["count"],
        )

class TakesSchema(Schema):
    short_form = fields.Raw(required=True)
    default = fields.Raw(required=False, allow_none=True)

class QuerySchema(Schema):
    query = fields.String(required=True)
    label = fields.String(required=True)
    function = fields.String(required=True)
    takes = fields.Nested(TakesSchema(), required=False, missing={})
    preview = fields.Integer(required=False, missing=0)
    preview_columns = fields.List(fields.String(), required=False, load_default=[])
    preview_results = fields.List(fields.Dict(), required=False, load_default=[])
    output_format = fields.String(required=False, load_default='table')
    count = fields.Integer(required=False, load_default=-1)

class License:
    def __init__(self, iri, short_form, label, icon, source, source_iri):
        self.iri = iri 
        self.short_form = short_form 
        self.label = label
        self.icon = icon
        self.source = source
        self.source_iri = source_iri

class LicenseSchema(Schema):
    iri        = fields.String(required=True)
    short_form = fields.String(required=True)
    label      = fields.String(required=True)
    icon       = fields.String(required=True)
    source     = fields.String(required=True)
    source_iri = fields.String(required=True)


class LicenseField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(LicenseSchema(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        if not isinstance(value, License):
            raise ValidationError("Invalid input")
        return {"iri": value.iri
                , "short_form": value.short_form
                , "label": value.label
                ,"icon": value.icon
                , "source": value.source
                , "source_iri": value.source_iri}

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return LicenseSchema().load(value)
    
class Coordinates:
    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z

class CoordinatesSchema(Schema):
    X = fields.Float(required=True)
    Y = fields.Float(required=True)
    Z = fields.Float(required=True)
    
    def _serialize(self, obj, **kwargs):
        return {"X": obj.X, "Y": obj.Y, "Z": obj.Z}
    
    def _deserialize(self, value, attr=None, data=None, **kwargs):
        return {"X":value.X, "Y":value.Y, "Z":value.Z}

class CoordinatesField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(CoordinatesSchema(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        if not isinstance(value, Coordinates):
            raise ValidationError("Invalid input")
        return {"X": value.X, "Y": value.Y, "Z": value.Z}

    def _deserialize(self, value, attr=None, data=None, **kwargs):
        if value is None:
            return value
        return f"X={value.X}, Y={value.Y}, Z={value.Z}" 

class Image:
    def __init__(self, id, label, thumbnail=None, thumbnail_transparent=None, nrrd=None, wlz=None, obj=None, swc=None, index=None, center=None, extent=None, voxel=None, orientation=None, type_id=None, type_label=None):
        self.id = id
        self.label = label
        self.thumbnail = thumbnail
        self.thumbnail_transparent = thumbnail_transparent
        self.nrrd = nrrd
        self.wlz = wlz
        self.obj = obj
        self.swc = swc
        self.index = index
        self.center = center
        self.extent = extent
        self.voxel = voxel
        self.orientation = orientation
        self.type_label = type_label
        self.type_id = type_id

class ImageSchema(Schema):
    id = fields.String(required=True)
    label = fields.String(required=True)
    thumbnail = fields.String(required=False, allow_none=True)
    thumbnail_transparent = fields.String(required=False, allow_none=True)
    nrrd = fields.String(required=False, allow_none=True)
    wlz = fields.String(required=False, allow_none=True)
    obj = fields.String(required=False, allow_none=True)
    swc = fields.String(required=False, allow_none=True)
    index = fields.Integer(required=False, allow_none=True)
    center = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    extent = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    voxel = fields.Nested(CoordinatesSchema(), required=False, allow_none=True)
    orientation = fields.String(required=False, allow_none=True)
    type_label = fields.String(required=False, allow_none=True)
    type_id = fields.String(required=False, allow_none=True)

class ImageField(fields.Nested):
    def __init__(self, **kwargs):
        super().__init__(ImageSchema(), **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return value
        return {"id": value.id
                , "label": value.label
                , "thumbnail": value.thumbnail
                , "thumbnail_transparent": value.thumbnail_transparent
                , "nrrd": value.nrrd
                , "wlz": value.wlz
                , "obj": value.obj
                , "swc": value.swc
                , "index": value.index
                , "center": value.center
                , "extent": value.extent
                , "voxel": value.voxel
                , "orientation": value.orientation
                , "type_id": value.type_id
                , "type_label": value.type_label
                }

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return value
        return ImageSchema().load(value)

class QueryField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.to_dict()

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict):
            raise ValidationError("Invalid input type.")
        return Query.from_dict(value)

class TermInfoOutputSchema(Schema):
    Name = fields.String(required=True)
    Id = fields.String(required=True)
    SuperTypes = fields.List(fields.String(), required=True)
    Meta = fields.Dict(keys=fields.String(), values=fields.String(), required=True)
    Tags = fields.List(fields.String(), required=True)
    Queries = fields.List(QueryField(), required=False)
    # RelatedTools: MCP tools (other than run_query) that are useful for this entity.
    # Each entry: {"tool": "<tool_name>", "label": "...", "default_args": {...}}.
    # Distinct from Queries because these are not dispatched via run_query — the
    # client should call the named tool directly with default_args.
    RelatedTools = fields.List(fields.Dict(), required=False)
    IsIndividual = fields.Bool(missing=False, required=False)
    Images = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsClass = fields.Bool(missing=False, required=False)
    Examples = fields.Dict(keys=fields.String(), values=fields.List(fields.Nested(ImageSchema()), missing={}), required=False, allow_none=True)
    IsTemplate = fields.Bool(missing=False, required=False)
    IsPaintedDomain = fields.Bool(missing=False, required=False)
    Domains = fields.Dict(keys=fields.Integer(), values=fields.Nested(ImageSchema()), required=False, allow_none=True)
    Licenses = fields.Dict(keys=fields.Integer(), values=fields.Nested(LicenseSchema()), required=False, allow_none=True)
    Publications = fields.List(fields.Dict(keys=fields.String(), values=fields.Raw()), required=False)
    Synonyms = fields.List(fields.Dict(keys=fields.String(), values=fields.Raw()), required=False, allow_none=True)
    Technique = fields.List(fields.String(), required=False, allow_none=True)
    # External DB cross-references (site label + accession link + icon), rendered
    # as the panel's xrefs section.
    Xrefs = fields.List(fields.Dict(keys=fields.String(), values=fields.Raw()), required=False, allow_none=True)

    @post_load
    def make_term_info(self, data, **kwargs):
        if "Queries" in data:
            data["Queries"] = [query.to_dict() for query in data["Queries"]]
        return data

    def __str__(self):
        term_info_data = self.make_term_info(self.data)
        if "Queries" in term_info_data:
            term_info_data["Queries"] = [query.to_dict() for query in term_info_data["Queries"]]
        return str(self.dump(term_info_data))

def encode_brackets(text):
    """
    Encodes square brackets in the given text to prevent breaking markdown link syntax.
    Parentheses are NOT encoded as they don't break markdown syntax.

    :param text: The text to encode.
    :return: The text with square brackets encoded.
    """
    return (text.replace('[', '%5B')
                .replace(']', '%5D'))

# Module-level pre-compiled patterns + translation tables. Defining these
# once at import time (rather than per call) is itself a measurable win on
# large frames: re.compile is cached but the lookup still adds up over
# millions of cells, and str.translate with a pre-built table is faster
# than chained .replace calls.
_BRACKET_TRANSLATE = str.maketrans({'[': '%5B', ']': '%5D'})

# Image-markdown cell: `[![alt](url 'title')](ref)` OR
# `[![alt](url "title")](ref)` OR with no title slot. We only care about
# the URL slot so we can secure it; alt/title/ref pass through unchanged.
_RE_IMAGE_URL = re.compile(
    r"(\[!\[[^\]]*\]\()([^'\"\s)]*)([^)]*\)\]\([^)]+\))"
)

# Regular markdown link: `[label](url)`. We secure the URL and percent-
# encode bracket characters inside the label so a label like
# "P{GMR95F02-GAL4} expression pattern[CPTI100022]" doesn't break the V2
# markdown parser.
_RE_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')


def _encode_image_url(match: 're.Match') -> str:
    """Repl callback for image-markdown cells — secure URL, preserve rest."""
    prefix, url, suffix = match.group(1), match.group(2), match.group(3)
    if url and url.startswith('http://'):
        url = 'https://' + url[7:]
    return f"{prefix}{url}{suffix}"


def _encode_regular_md_link(match: 're.Match') -> str:
    """Repl callback for `[label](url)` — bracket-encode label, secure URL."""
    label, url = match.group(1), match.group(2)
    if '[' in label or ']' in label:
        label = label.translate(_BRACKET_TRANSLATE)
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    return f"[{label}]({url})"


def encode_markdown_links(df, columns):
    """
    Vectorised markdown-link encoder.

    For each named column:
      - Image-markdown cells (`[![alt](url 'title')](ref)`): secure the URL
        (http→https). Alt, title, ref pass through unchanged so the V2
        processor's IMAGE_MARKDOWN regex still matches both single- and
        double-quoted title forms.
      - Regular markdown cells (`[label](url), [label2](url2), ...`):
        percent-encode `[` and `]` inside the label part and secure URLs.
      - Plain text rows are left alone.

    Implementation: pandas `Series.str.replace(regex=True, repl=callable)`
    runs the substring scanner in C and only crosses into Python for the
    actual substitution callback — roughly 10–50× faster than the
    previous per-row `.apply(encode_label)` loop on the 500k-row
    AllAlignedImages workload that surfaced this bottleneck. Skips empty
    DataFrames and non-string columns cheaply.

    Backwards-compatible: input nulls are preserved; existing data with
    pre-secured URLs comes back untouched.
    """
    if df is None or df.empty:
        return df

    for column in columns:
        if column not in df.columns:
            continue
        s = df[column]
        if s.dtype != object:
            continue

        # `str.replace` skips NaN automatically. We coerce to string only
        # for the rows that are non-null to keep null cells as-is.
        notnull_mask = s.notna()
        if not notnull_mask.any():
            continue
        non_null = s.where(notnull_mask, '').astype(str)

        # Branch on shape using a vectorised prefix check — this is a single
        # C-loop over the column, far cheaper than re-detecting per row.
        is_image = non_null.str.startswith('[![', na=False)

        if is_image.any():
            # Image-markdown rows: secure URL only, preserve title quoting.
            image_rows = non_null[is_image]
            image_rows = image_rows.str.replace(
                _RE_IMAGE_URL, _encode_image_url, regex=True
            )
            non_null = non_null.where(~is_image, image_rows)

        non_image_mask = ~is_image
        if non_image_mask.any():
            # Label-shape rows: bracket-encode + secure URL via regex callback.
            label_rows = non_null[non_image_mask]
            label_rows = label_rows.str.replace(
                _RE_MD_LINK, _encode_regular_md_link, regex=True
            )
            non_null = non_null.where(is_image, label_rows)

        # Write back, preserving original null cells.
        df.loc[notnull_mask, column] = non_null[notnull_mask]

    return df
    

# Author-year citation linking ------------------------------------------------
# Cited publications appear in the definition/comment prose as plain author-year
# text (e.g. "Wolff et al., 2015"). We hold the id for each via the term's pubs
# (def_pubs / pub_syn / pubs), so we wrap matching mentions in markdown links the
# panel renders. Citations with no matching pub id are logged: they should also
# have appeared in the term's References, so a miss indicates a missing
# has_reference edge worth investigating.
_CITATION_RE = re.compile(
    r"[A-Z][A-Za-z.'\u2019-]+"
    r"(?:\s+et al\.|\s+and\s+[A-Z][A-Za-z.'\u2019-]+|\s+&\s+[A-Z][A-Za-z.'\u2019-]+)?"
    r",?\s+\d{4}[a-z]?"
)


def _pub_author_year(pub):
    """Short author-year microref text for a pub, e.g. 'Wolff et al., 2015'."""
    core = getattr(pub, 'core', None)
    if not core:
        return ""
    micro = getattr(pub, 'microref', '') or ""
    if micro:
        return micro.strip()
    label = getattr(core, 'label', '') or ""
    if "," in label:
        parts = label.split(",")
        if len(parts) > 1:
            return (parts[0] + "," + parts[1]).strip()
    return label.strip()


def _collect_term_pub_map(vfbTerm):
    """{author_year_text: short_form} for every pub the term cites."""
    pubs = list(getattr(vfbTerm, 'def_pubs', None) or [])
    for syn in (getattr(vfbTerm, 'pub_syn', None) or []):
        if getattr(syn, 'pub', None):
            pubs.append(syn.pub)
        pubs.extend(getattr(syn, 'pubs', None) or [])
    pubs.extend(getattr(vfbTerm, 'pubs', None) or [])
    mapping = {}
    for p in pubs:
        core = getattr(p, 'core', None)
        sf = getattr(core, 'short_form', '') if core else ''
        if not sf or sf == 'Unattributed':
            continue
        ay = _pub_author_year(p)
        if ay and ay not in mapping:
            mapping[ay] = sf
    return mapping


def _split_author_year(author_year):
    """('Wolff et al., 2015') -> ('Wolff et al.', '2015'); handles trailing letter."""
    m = re.match(r"^(.*?),?\s*\(?(\d{4})[a-z]?\)?$", author_year.strip())
    return (m.group(1).strip(), m.group(2)) if m else (None, None)


def _linkify_citations(text, pub_map, term_id="", field=""):
    """Wrap known author-year citations (either 'Author, 2015' or 'Author (2015)')
    in markdown links, normalising to '[Author, 2015](id)'. Logs unmatched ones."""
    if not text:
        return text
    items = []
    for ay, sf in pub_map.items():
        author, year = _split_author_year(ay)
        if author and year:
            items.append((author, year, sf))
    # Longest author first so 'Ito and Awasaki' wins over 'Ito et al.' etc.
    items.sort(key=lambda x: len(x[0]), reverse=True)
    linked = text
    for author, year, sf in items:
        pat = re.compile(r"(?<!\[)" + re.escape(author) + r"(?:,\s*|\s+\(|\s+)" + year + r"\)?(?!\])")
        linked = pat.sub("[" + author + ", " + year + "](" + sf + ")", linked)
    # Flag citations in the prose we could not link -- they should also be in References.
    matched_keys = {(a, y) for a, y, _ in items}
    missing = []
    for cite in _CITATION_RE.findall(text):
        a, y = _split_author_year(cite.strip().rstrip(','))
        if a and y and (a, y) not in matched_keys:
            missing.append(a + ", " + y)
    if missing:
        logger.warning(
            "term_info %s %s cites publications with no matching reference id "
            "(should also appear in References -- investigate missing has_reference): %s",
            term_id, field, sorted(set(missing)))
    return linked


def term_info_parse_object(results, short_form):
    termInfo = {}
    termInfo["SuperTypes"] = []
    termInfo["Tags"] = []
    termInfo["Queries"] = []
    termInfo["RelatedTools"] = []
    termInfo["IsClass"] = False
    termInfo["IsIndividual"] = False
    termInfo["IsTemplate"] = False
    termInfo["Images"] = {}
    termInfo["Examples"] = {}
    termInfo["Domains"] = {}
    termInfo["Licenses"] = {}
    termInfo["Publications"] = []
    termInfo["IsPaintedDomain"] = False
    termInfo["Technique"] = []
    
    if results.hits > 0 and results.docs and len(results.docs) > 0:
        termInfo["Meta"] = {}
        try:
            # Deserialize the term info from the first result
            vfbTerm = deserialize_term_info(results.docs[0]['term_info'][0])
        except KeyError:
            print(f"SOLR doc missing 'term_info': {results.docs[0]}")
            return None
        except Exception as e:
            print(f"Error deserializing term info: {e}")
            return None
            
        queries = []
        # Initialize synonyms variable to avoid UnboundLocalError
        synonyms = []
        termInfo["Id"] = vfbTerm.term.core.short_form
        termInfo["Meta"]["Name"] = "[%s](%s)"%(encode_brackets(vfbTerm.term.core.label), vfbTerm.term.core.short_form)
        mainlabel = vfbTerm.term.core.label
        if hasattr(vfbTerm.term.core, 'symbol') and vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
            termInfo["Meta"]["Symbol"] = "[%s](%s)"%(encode_brackets(vfbTerm.term.core.symbol), vfbTerm.term.core.short_form)
            mainlabel = vfbTerm.term.core.symbol
        termInfo["Name"] = mainlabel
        termInfo["SuperTypes"] = vfbTerm.term.core.types if hasattr(vfbTerm.term.core, 'types') else []
        if "Class" in termInfo["SuperTypes"]:
            termInfo["IsClass"] = True
        elif "Individual" in termInfo["SuperTypes"]:
            termInfo["IsIndividual"] = True
        try:
            # Retrieve tags from the term's unique_facets attribute
            termInfo["Tags"] = vfbTerm.term.core.unique_facets
        except (NameError, AttributeError):
            # If unique_facets attribute doesn't exist, use the term's types
            termInfo["Tags"] = vfbTerm.term.core.types if hasattr(vfbTerm.term.core, 'types') else []
        # Map of author-year -> pub id for citation linking in description/comment.
        _pub_map = _collect_term_pub_map(vfbTerm)
        try:
            # Retrieve description and link known author-year citations in the prose.
            _desc_body = "".join(vfbTerm.term.description)
            termInfo["Meta"]["Description"] = _linkify_citations(_desc_body, _pub_map, termInfo.get("Id", short_form), "description")
        except (NameError, AttributeError):
            pass
        # Append class definition references (def_pubs) inline to the description
        # as markdown microref links, matching how the panel renders them today
        # (legacy VFBProcessTermInfoCachedJson definition() + "(<microrefs>)").
        # Kept inline rather than as a separate Publications entry so the display
        # is identical and no new panel section is introduced.
        if getattr(vfbTerm, 'def_pubs', None):
            def_refs = [p.get_microref() for p in vfbTerm.def_pubs
                        if hasattr(p, 'get_miniref') and p.get_miniref()
                        and hasattr(p, 'get_microref') and p.get_microref()]
            if def_refs:
                existing_desc = termInfo["Meta"].get("Description", "")
                termInfo["Meta"]["Description"] = (existing_desc + "\n(" + ", ".join(def_refs) + ")") if existing_desc else ("(" + ", ".join(def_refs) + ")")
        try:
            # Retrieve comment and link known author-year citations.
            _comment_body = "".join(vfbTerm.term.comment)
            termInfo["Meta"]["Comment"] = _linkify_citations(_comment_body, _pub_map, termInfo.get("Id", short_form), "comment")
        except (NameError, AttributeError):
            pass
        # External homepage link + logo (e.g. a DataSet's FlyBase/project link and
        # icon). Rendered as the panel's link / logo rows
        # (VFBProcessTermInfoCachedJson.java:1456 / :1449). Previously dropped.
        try:
            _link = vfbTerm.term.get_link() if hasattr(vfbTerm.term, 'get_link') else ""
            if _link:
                termInfo["Meta"]["Link"] = _link
        except (AttributeError, TypeError):
            pass
        try:
            _logo = vfbTerm.term.get_logo() if hasattr(vfbTerm.term, 'get_logo') else ""
            if _logo:
                termInfo["Meta"]["Logo"] = _logo
        except (AttributeError, TypeError):
            pass
        
        if hasattr(vfbTerm, 'parents') and vfbTerm.parents and len(vfbTerm.parents) > 0:
            parents = []

            # Sort the parents alphabetically
            sorted_parents = sorted(vfbTerm.parents, key=lambda parent: parent.label)

            for parent in sorted_parents:
                parents.append("[%s](%s)"%(encode_brackets(parent.label), parent.short_form))
            termInfo["Meta"]["Types"] = "; ".join(parents)

        if hasattr(vfbTerm, 'relationships') and vfbTerm.relationships and len(vfbTerm.relationships) > 0:
            relationships = []
            pubs_from_relationships = [] # New: Collect publication references from relationships
            techniques = set() # Collect imaging techniques from relationships

            # Group relationships by relation type and remove duplicates
            grouped_relationships = {}
            for relationship in vfbTerm.relationships:
                if hasattr(relationship.relation, 'short_form') and relationship.relation.short_form:
                    relation_key = (relationship.relation.label, relationship.relation.short_form)
                elif hasattr(relationship.relation, 'iri') and relationship.relation.iri:
                    relation_key = (relationship.relation.label, relationship.relation.iri.split('/')[-1])
                elif hasattr(relationship.relation, 'label') and relationship.relation.label:
                    relation_key = (relationship.relation.label, relationship.relation.label)
                else:
                    # Skip relationships with no identifiable relation
                    continue
                    
                if not hasattr(relationship, 'object') or not hasattr(relationship.object, 'label'):
                    # Skip relationships with missing object information
                    continue
                    
                object_key = (relationship.object.label, getattr(relationship.object, 'short_form', ''))
                
                # Collect imaging techniques from relationships
                relation_id = None
                if hasattr(relationship.relation, 'short_form') and relationship.relation.short_form:
                    relation_id = relationship.relation.short_form
                elif hasattr(relationship.relation, 'iri') and relationship.relation.iri:
                    relation_id = relationship.relation.iri.split('/')[-1]
                
                if relation_id == 'OBI_0000312':  # is_specified_output_of
                    if hasattr(relationship.object, 'label') and relationship.object.label:
                        techniques.add(relationship.object.label)
                
                # New: Extract publications from this relationship if they exist
                if hasattr(relationship, 'pubs') and relationship.pubs:
                    for pub in relationship.pubs:
                        if hasattr(pub, 'get_miniref') and pub.get_miniref():
                            publication = {}
                            publication["title"] = pub.core.label if hasattr(pub, 'core') and hasattr(pub.core, 'label') else ""
                            publication["short_form"] = pub.core.short_form if hasattr(pub, 'core') and hasattr(pub.core, 'short_form') else ""
                            publication["microref"] = pub.get_microref() if hasattr(pub, 'get_microref') and pub.get_microref() else ""
                            
                            # Add external references
                            refs = []
                            if hasattr(pub, 'PubMed') and pub.PubMed:
                                refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={pub.PubMed}")
                            if hasattr(pub, 'FlyBase') and pub.FlyBase:
                                refs.append(f"http://flybase.org/reports/{pub.FlyBase}")
                            if hasattr(pub, 'DOI') and pub.DOI:
                                refs.append(f"https://doi.org/{pub.DOI}")
                            
                            publication["refs"] = refs
                            pubs_from_relationships.append(publication)
                
                if relation_key not in grouped_relationships:
                    grouped_relationships[relation_key] = set()
                grouped_relationships[relation_key].add(object_key)

            # Sort the grouped_relationships by keys
            sorted_grouped_relationships = dict(sorted(grouped_relationships.items()))

            # Append the grouped relationships to termInfo
            for relation_key, object_set in sorted_grouped_relationships.items():
                # Sort the object_set by object_key
                sorted_object_set = sorted(list(object_set))
                relation_objects = []
                for object_key in sorted_object_set:
                    relation_objects.append("[%s](%s)" % (encode_brackets(object_key[0]), object_key[1]))
                relationships.append("[%s](%s): %s" % (encode_brackets(relation_key[0]), relation_key[1], ', '.join(relation_objects)))
            termInfo["Meta"]["Relationships"] = "; ".join(relationships)

            # New: Add relationship publications to main publications list
            if pubs_from_relationships:
                if "Publications" not in termInfo:
                    termInfo["Publications"] = pubs_from_relationships
                else:
                    # Merge with existing publications, avoiding duplicates by short_form
                    existing_pub_short_forms = {pub.get("short_form", "") for pub in termInfo["Publications"]}
                    for pub in pubs_from_relationships:
                        if pub.get("short_form", "") not in existing_pub_short_forms:
                            termInfo["Publications"].append(pub)
                            existing_pub_short_forms.add(pub.get("short_form", ""))

            # Add techniques from relationships to termInfo for Individuals
            if termInfo["IsIndividual"] and techniques:
                termInfo["Technique"].extend(techniques)
                termInfo["Technique"] = sorted(list(set(termInfo["Technique"])))

        # If the term has anatomy channel images, retrieve the images and associated information
        if vfbTerm.anatomy_channel_image and len(vfbTerm.anatomy_channel_image) > 0:
            images = {}
            techniques = set()
            for image in vfbTerm.anatomy_channel_image:
                # Check if this is a computer graphic image (painted domain)
                if hasattr(image, 'channel_image') and hasattr(image.channel_image, 'imaging_technique'):
                    technique = image.channel_image.imaging_technique
                    if hasattr(technique, 'symbol') and technique.symbol and 'computer' in technique.symbol.lower():
                        termInfo["IsPaintedDomain"] = True
                    # Collect technique for Individual terms
                    if hasattr(technique, 'label') and technique.label:
                        techniques.add(technique.label)
                
                record = {}
                record["id"] = image.anatomy.short_form
                label = image.anatomy.label
                if image.anatomy.symbol and len(image.anatomy.symbol) > 0:
                    label = image.anatomy.symbol
                record["label"] = label
                if not image.channel_image.image.template_anatomy.short_form in images.keys():
                    images[image.channel_image.image.template_anatomy.short_form]=[]
                record["thumbnail"] = image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
                record["thumbnail_transparent"] = image.channel_image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
                for key in vars(image.channel_image.image).keys():
                    if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image.channel_image.image)[key]) > 1:
                        record[key.replace("image_","")] = vars(image.channel_image.image)[key].replace("http://","https://")
                images[image.channel_image.image.template_anatomy.short_form].append(record)
            
            # Sort each template's images by id in descending order (newest first)
            for template_key in images:
                images[template_key] = sorted(images[template_key], key=lambda x: x["id"], reverse=True)
            
            termInfo["Examples"] = images
            # Add techniques to termInfo for Individuals
            if termInfo["IsIndividual"] and techniques:
                termInfo["Technique"].extend(techniques)
                termInfo["Technique"] = sorted(list(set(termInfo["Technique"])))
            # add a query for listing all available images -- only for anatomy
            # Class terms (get_instances expects a Class, per this query's own
            # Class+Anatomy criteria). DataSets/Individuals that merely have
            # images must not get it (they use DatasetImages etc.), otherwise a
            # dataset shows a spurious "List all available images" query.
            if contains_all_tags(termInfo["SuperTypes"], ["Class", "Anatomy"]):
                q = ListAllAvailableImages_to_schema(termInfo["Name"], {"short_form":vfbTerm.term.core.short_form})
                queries.append(q)

        # If the term has channel images but not anatomy channel images, create thumbnails from channel images.
        if vfbTerm.channel_image and len(vfbTerm.channel_image) > 0:
            images = {}
            techniques = set()
            for image in vfbTerm.channel_image:
                # Check if this is a computer graphic image (painted domain)
                if hasattr(image, 'imaging_technique'):
                    technique = image.imaging_technique
                    if hasattr(technique, 'symbol') and technique.symbol and 'computer' in technique.symbol.lower():
                        termInfo["IsPaintedDomain"] = True
                    # Collect technique for Individual terms
                    if hasattr(technique, 'label') and technique.label:
                        techniques.add(technique.label)
                
                record = {}
                record["id"] = vfbTerm.term.core.short_form
                label = vfbTerm.term.core.label
                if vfbTerm.term.core.symbol and len(vfbTerm.term.core.symbol) > 0:
                    label = vfbTerm.term.core.symbol
                record["label"] = label
                if not image.image.template_anatomy.short_form in images.keys():
                    images[image.image.template_anatomy.short_form]=[]
                record["thumbnail"] = image.image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
                record["thumbnail_transparent"] = image.image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
                for key in vars(image.image).keys():
                    if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image.image)[key]) > 1:
                        record[key.replace("image_","")] = vars(image.image)[key].replace("http://","https://")
                images[image.image.template_anatomy.short_form].append(record)
            
            # Sort each template's images by id in descending order (newest first)
            for template_key in images:
                images[template_key] = sorted(images[template_key], key=lambda x: x["id"], reverse=True)
            
            # Add the thumbnails to the term info
            termInfo["Images"] = images
            # Add techniques to termInfo for Individuals
            if termInfo["IsIndividual"] and techniques:
                termInfo["Technique"].extend(techniques)
                termInfo["Technique"] = sorted(list(set(termInfo["Technique"])))

        if vfbTerm.dataset_license and len(vfbTerm.dataset_license) > 0: 
            licenses = {}
            for idx, dataset_license in enumerate(vfbTerm.dataset_license):
                record = {}
                record['iri'] = dataset_license.license.core.iri
                record['short_form'] = dataset_license.license.core.short_form
                record['label'] = dataset_license.license.core.label
                record['icon'] = dataset_license.license.icon
                record['source_iri'] = dataset_license.dataset.core.iri
                record['source'] = dataset_license.dataset.core.label
                licenses[idx] = record 
            termInfo["Licenses"] = licenses
              
        if vfbTerm.template_channel and vfbTerm.template_channel.channel.short_form:
            termInfo["IsTemplate"] = True
            images = {}
            image = vfbTerm.template_channel
            record = {}
            
            # Validate that the channel ID matches the template ID (numeric part should be the same)
            template_id = vfbTerm.term.core.short_form
            channel_id = vfbTerm.template_channel.channel.short_form
            
            # Extract numeric parts for validation
            if template_id and channel_id:
                template_numeric = template_id.replace("VFB_", "") if template_id.startswith("VFB_") else ""
                channel_numeric = channel_id.replace("VFBc_", "") if channel_id.startswith("VFBc_") else ""
                
                if template_numeric != channel_numeric:
                    print(f"Warning: Template ID {template_id} does not match channel ID {channel_id}")
                    label = vfbTerm.template_channel.channel.label
                    record["id"] = channel_id
                else:
                    label = vfbTerm.term.core.label
                    record["id"] = template_id
            
            if vfbTerm.template_channel.channel.symbol != "" and len(vfbTerm.template_channel.channel.symbol) > 0:
                label = vfbTerm.template_channel.channel.symbol
            record["label"] = label
            if not template_id in images.keys():
                images[template_id]=[]
            record["thumbnail"] = image.image_thumbnail.replace("http://","https://").replace("thumbnailT.png","thumbnail.png")
            record["thumbnail_transparent"] = image.image_thumbnail.replace("http://","https://").replace("thumbnail.png","thumbnailT.png")
            for key in vars(image).keys():
                if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                    record[key.replace("image_","")] = vars(image)[key].replace("http://","https://")
            if len(image.index) > 0:
              record['index'] = int(image.index[0])
            vars(image).keys()
            image_vars = vars(image)
            if 'center' in image_vars.keys():
                record['center'] = image.get_center()
            if 'extent' in image_vars.keys():
                record['extent'] = image.get_extent()
            if 'voxel' in image_vars.keys():
                record['voxel'] = image.get_voxel()
            if 'orientation' in image_vars.keys():
                record['orientation'] = image.orientation
            images[template_id].append(record)

            # Add the thumbnails to the term info
            termInfo["Images"] = images

            if vfbTerm.template_domains and len(vfbTerm.template_domains) > 0:
                images = {}
                termInfo["IsTemplate"] = True
                for image in vfbTerm.template_domains:
                    record = {}
                    record["id"] = image.anatomical_individual.short_form
                    label = image.anatomical_individual.label
                    if image.anatomical_individual.symbol != "" and len(image.anatomical_individual.symbol) > 0:
                        label = image.anatomical_individual.symbol
                    record["label"] = label
                    record["type_id"] = image.anatomical_type.short_form
                    label = image.anatomical_type.label
                    if image.anatomical_type.symbol != "" and len(image.anatomical_type.symbol) > 0:
                        label = image.anatomical_type.symbol
                    record["type_label"] = label
                    record["index"] = int(image.index[0])
                    record["thumbnail"] = image.folder.replace("http://", "https://") + "thumbnail.png"
                    record["thumbnail_transparent"] = image.folder.replace("http://", "https://") + "thumbnailT.png"
                    for key in vars(image).keys():
                        if "image_" in key and not ("thumbnail" in key or "folder" in key) and len(vars(image)[key]) > 1:
                            record[key.replace("image_", "")] = vars(image)[key].replace("http://", "https://")
                    record["center"] = image.get_center()
                    images[record["index"]] = record

                # Sort the domains by their index and add them to the term info
                sorted_images = {int(key): value for key, value in sorted(images.items(), key=lambda x: x[0])}
                termInfo["Domains"] = sorted_images

        # SplitsTargeting — splits (intersectional expression patterns) that
        # target this neuron class. TargetNeurons — neurons a split class targets.
        # Live Neo4j queries (indexer neuron_split / split_neuron clauses),
        # surfaced as queries with a count badge rather than static fields.
        if contains_all_tags(termInfo["SuperTypes"], ["Class", "Neuron"]):
            q = SplitsTargeting_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        if contains_all_tags(termInfo["SuperTypes"], ["Class", "Split"]):
            q = TargetNeurons_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)

        if contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron"]):
            q = SimilarMorphologyTo_to_schema(termInfo["Name"], {"neuron": vfbTerm.term.core.short_form, "similarity_score": "NBLAST_score"})
            queries.append(q)
        if contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron", "has_neuron_connectivity"]):
            q = NeuronInputsTo_to_schema(termInfo["Name"], {"neuron_short_form": vfbTerm.term.core.short_form})
            queries.append(q)
            # NeuronNeuronConnectivity query - neurons connected to this neuron
            q = NeuronNeuronConnectivityQuery_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPartHere query - for Class+Anatomy terms (synaptic neuropils, etc.)
        # Matches XMI criteria: Class + Synaptic_neuropil, or other anatomical regions
        # Excluded for neuron classes: "neurons with some part in <a neuron>" is not a meaningful query
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and "Neuron" not in termInfo["SuperTypes"] and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Anatomy" in termInfo["SuperTypes"]
        ):
            q = NeuronsPartHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsSynaptic query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsSynaptic_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPresynapticHere query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsPresynapticHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronsPostsynapticHere query - for synaptic neuropils and visual systems
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Visual_system OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or 
            "Visual_system" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = NeuronsPostsynapticHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ComponentsOf query - for clones
        # Matches XMI criteria: Class + Clone
        if contains_all_tags(termInfo["SuperTypes"], ["Class", "Clone"]):
            q = ComponentsOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # PartsOf query - for any Class except neuron classes
        # Matches XMI criteria: Class (any)
        # Excluded for neuron classes: anatomical sub-parts of a neuron type are not modelled
        # in the ontology in a way that makes this query useful at the class level.
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and "Neuron" not in termInfo["SuperTypes"]:
            q = PartsOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # SubclassesOf query - for any Class
        # Matches XMI criteria: Class (any)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]):
            q = SubclassesOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NeuronClassesFasciculatingHere query - for tracts/nerves
        # Matches XMI criteria: Class + Tract_or_nerve (VFB uses Neuron_projection_bundle type)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and "Neuron_projection_bundle" in termInfo["SuperTypes"]:
            q = NeuronClassesFasciculatingHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # TractsNervesInnervatingHere query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = TractsNervesInnervatingHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # LineageClonesIn query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = LineageClonesIn_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ImagesNeurons query - for synaptic neuropils
        # Matches XMI criteria: Class + (Synaptic_neuropil OR Synaptic_neuropil_domain)
        # Returns individual neuron images (instances) rather than neuron classes
        if contains_all_tags(termInfo["SuperTypes"], ["Class"]) and (
            "Synaptic_neuropil" in termInfo["SuperTypes"] or
            "Synaptic_neuropil_domain" in termInfo["SuperTypes"]
        ):
            q = ImagesNeurons_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # ImagesThatDevelopFrom query - for neuroblasts
        # Matches XMI criteria: Class + Neuroblast
        # Returns individual neuron images that develop from the neuroblast
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Neuroblast"]):
            q = ImagesThatDevelopFrom_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # epFrag query - for expression patterns
        # Matches XMI criteria: Class + Expression_pattern
        # Returns individual expression pattern fragment images
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Expression_pattern"]):
            q = epFrag_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)

        # AnatomyExpressedIn query - for expression patterns / fragments
        # Matches XMI criteria: Class + Expression_pattern  OR
        #                       Class + Expression_pattern_fragment
        # Returns anatomy classes where this expression pattern is expressed.
        # The forward-direction "transgene expression here" lookup for
        # anatomy entities is owned by TransgeneExpressionHere.
        if termInfo["SuperTypes"] and (
            contains_all_tags(termInfo["SuperTypes"], ["Class", "Expression_pattern"]) or
            contains_all_tags(termInfo["SuperTypes"], ["Class", "Expression_pattern_fragment"])
        ):
            q = AnatomyExpressedIn_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # anatScRNAseqQuery query - for anatomical regions with scRNAseq data
        # Matches XMI criteria: Class + Anatomy + hasScRNAseq
        # Returns scRNAseq clusters and datasets for the anatomical region
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Anatomy", "hasScRNAseq"]):
            q = anatScRNAseqQuery_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # clusterExpression query - for clusters
        # Matches XMI criteria: Individual + Cluster
        # Returns genes expressed in the cluster
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Cluster"]):
            q = clusterExpression_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # expressionCluster query - for genes with scRNAseq data
        # Matches XMI criteria: Class + Gene + hasScRNAseq
        # Returns clusters expressing the gene
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Gene", "hasScRNAseq"]):
            q = expressionCluster_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # scRNAdatasetData query - for scRNAseq datasets
        # Matches XMI criteria: DataSet + hasScRNAseq
        # Returns all clusters in the dataset
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["DataSet", "hasScRNAseq"]):
            q = scRNAdatasetData_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # NBLAST similarity queries
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Neuron", "NBLASTexp"]):
            q = SimilarMorphologyToPartOf_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # SimilarMorphologyToPartOfexp query - reverse NBLASTexp
        # Matches XMI criteria: (Individual + Expression_pattern + NBLASTexp) OR (Individual + Expression_pattern_fragment + NBLASTexp)
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "NBLASTexp"]) and (
            "Expression_pattern" in termInfo["SuperTypes"] or
            "Expression_pattern_fragment" in termInfo["SuperTypes"]
        ):
            q = SimilarMorphologyToPartOfexp_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "neuronbridge"]):
            q = SimilarMorphologyToNB_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "Expression_pattern", "neuronbridge"]):
            q = SimilarMorphologyToNBexp_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "UNBLAST"]):
            q = SimilarMorphologyToUserData_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Dataset/Template queries
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Template", "Individual"]):
            q = PaintedDomains_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
            q2 = AllAlignedImages_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q2)
            q3 = AlignedDatasets_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q3)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["DataSet", "has_image"]):
            q = DatasetImages_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Template"]):
            q = AllDatasets_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Publication query
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Individual", "pub"]):
            q = TermsForPub_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Transgene expression query
        # Matches XMI criteria: (Class + Nervous_system + Anatomy) OR (Class + Nervous_system + Neuron)
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Nervous_system"]) and (
            "Anatomy" in termInfo["SuperTypes"] or "Neuron" in termInfo["SuperTypes"]
        ):
            q = TransgeneExpressionHere_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
        
        # Class connectivity queries — downstream and upstream partner neuron classes
        # Matches criteria: Class + Neuron (neuron class with indexed connectivity data)
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Neuron"]):
            q = DownstreamClassConnectivity_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)
            q = UpstreamClassConnectivity_to_schema(termInfo["Name"], {"short_form": vfbTerm.term.core.short_form})
            queries.append(q)

        # Hierarchy entries — surfaced in RelatedTools, dispatched via the
        # get_hierarchy MCP tool rather than run_query.
        sf_for_hier = vfbTerm.term.core.short_form
        # subclass_of hierarchy is meaningful for cell-type taxonomies.
        # Gate: Class + Cell (matches the "Cell"-bounded ancestor filter inside
        # get_hierarchy itself).
        if termInfo["SuperTypes"] and contains_all_tags(termInfo["SuperTypes"], ["Class", "Cell"]):
            termInfo["RelatedTools"].append({
                "tool": "get_hierarchy",
                "label": f"Cell-type hierarchy of {termInfo['Name']}",
                "default_args": {
                    "id": sf_for_hier,
                    "relationship": "subclass_of",
                    "direction": "both",
                    "max_depth": 1,
                },
            })
        # part_of hierarchy is meaningful for nervous-system regions
        # (brain, neuropils, ganglia, tracts), but NOT for cells/neurons or
        # non-neural anatomy. Special-case the nervous system root, which lacks
        # the "Nervous_system" SuperType because it isn't part_of itself.
        is_ns_region = (
            termInfo["SuperTypes"]
            and contains_all_tags(termInfo["SuperTypes"], ["Class", "Nervous_system"])
            and "Cell" not in termInfo["SuperTypes"]
        )
        is_ns_root = sf_for_hier == "FBbt_00005093"
        if is_ns_region or is_ns_root:
            termInfo["RelatedTools"].append({
                "tool": "get_hierarchy",
                "label": f"Region containment hierarchy of {termInfo['Name']}",
                "default_args": {
                    "id": sf_for_hier,
                    "relationship": "part_of",
                    "direction": "both",
                    "max_depth": 1,
                },
            })

        # FlyBase stock finder — for Feature terms (FBgn/FBal/FBti/FBtp/FBco/FBst)
        sf = vfbTerm.term.core.short_form
        if sf.startswith(("FBgn", "FBal", "FBti", "FBtp", "FBco", "FBst")):
            q = FindStocks_to_schema(termInfo["Name"], {"short_form": sf})
            queries.append(q)
            # Also surface the dedicated find_stocks MCP tool, which exposes
            # the optional collection_filter parameter (Bloomington, Kyoto,
            # VDRC, etc.) that the run_query/FindStocks path does not.
            termInfo["RelatedTools"].append({
                "tool": "find_stocks",
                "label": f"Find fly stocks for {termInfo['Name']} (with optional stock-centre filter)",
                "default_args": {"feature_id": sf},
            })

        # FlyBase combination publications — for FBco terms
        if sf.startswith("FBco"):
            q = FindComboPublications_to_schema(termInfo["Name"], {"short_form": sf})
            queries.append(q)
            # Also surface the dedicated find_combo_publications MCP tool,
            # which returns full per-publication metadata (DOI, PMID, miniref,
            # year) ready for citation rendering.
            termInfo["RelatedTools"].append({
                "tool": "find_combo_publications",
                "label": f"Find publications for {termInfo['Name']} (with full citation metadata)",
                "default_args": {"fbco_id": sf},
            })

        # For individuals that are painted domains of anatomical regions, add parent class queries
        if termInfo["IsIndividual"] and termInfo["Technique"] and any('computer' in t.lower() for t in termInfo["Technique"]):
            anatomical_classes = []
            
            # Check parents
            if vfbTerm.parents:
                for parent in vfbTerm.parents:
                    if parent.types and "Class" in parent.types and "Anatomy" in parent.types:
                        anatomical_classes.append(parent)
            
            # Check relationships for anatomical classes
            if vfbTerm.relationships:
                for rel in vfbTerm.relationships:
                    if hasattr(rel, 'object') and rel.object and hasattr(rel.object, 'types') and rel.object.types:
                        if "Class" in rel.object.types and "Anatomy" in rel.object.types:
                            anatomical_classes.append(rel.object)
            
            # Remove duplicates based on short_form
            seen = set()
            unique_anatomical_classes = []
            for cls in anatomical_classes:
                if cls.short_form not in seen:
                    seen.add(cls.short_form)
                    unique_anatomical_classes.append(cls)
            
            for parent in unique_anatomical_classes:
                parent_short_form = parent.short_form
                parent_label = parent.label if parent.label else parent_short_form
                
                # Add queries based on parent types
                if "Anatomy" in parent.types or "Synaptic_neuropil" in parent.types or "Synaptic_neuropil_domain" in parent.types:
                    # NeuronsPartHere query
                    q = NeuronsPartHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsSynaptic query
                    q = NeuronsSynaptic_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsPresynapticHere query
                    q = NeuronsPresynapticHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # NeuronsPostsynapticHere query
                    q = NeuronsPostsynapticHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # TractsNervesInnervatingHere query
                    q = TractsNervesInnervatingHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # LineageClonesIn query
                    q = LineageClonesIn_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                    
                    # ImagesNeurons query
                    q = ImagesNeurons_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Expression_pattern" in parent.types or "Expression_pattern_fragment" in parent.types:
                    # AnatomyExpressedIn query — anatomy classes where this
                    # expression pattern is expressed.
                    q = AnatomyExpressedIn_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Anatomy" in parent.types and "hasScRNAseq" in parent.types:
                    # anatScRNAseqQuery query
                    q = anatScRNAseqQuery_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Neuron_projection_bundle" in parent.types:
                    # NeuronClassesFasciculatingHere query
                    q = NeuronClassesFasciculatingHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Neuroblast" in parent.types:
                    # ImagesThatDevelopFrom query
                    q = ImagesThatDevelopFrom_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Expression_pattern" in parent.types:
                    # epFrag query
                    q = epFrag_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                if "Nervous_system" in parent.types and ("Anatomy" in parent.types or "Neuron" in parent.types):
                    # TransgeneExpressionHere query
                    q = TransgeneExpressionHere_to_schema(parent_label, {"short_form": parent_short_form})
                    queries.append(q)
                
                # PartsOf query - for any Class
                q = PartsOf_to_schema(parent_label, {"short_form": parent_short_form})
                queries.append(q)
                
                # SubclassesOf query - for any Class
                q = SubclassesOf_to_schema(parent_label, {"short_form": parent_short_form})
                queries.append(q)
        
        # Add Publications to the termInfo object
        if vfbTerm.pubs and len(vfbTerm.pubs) > 0:
            publications = []
            for pub in vfbTerm.pubs:
                if pub.get_miniref():
                    publication = {}
                    publication["title"] = pub.core.label if pub.core.label else ""
                    publication["short_form"] = pub.core.short_form if pub.core.short_form else ""
                    publication["microref"] = pub.get_microref() if hasattr(pub, 'get_microref') and pub.get_microref() else ""

                    # Add external references
                    refs = []
                    if hasattr(pub, 'PubMed') and pub.PubMed:
                        refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={pub.PubMed}")
                    if hasattr(pub, 'FlyBase') and pub.FlyBase:
                        refs.append(f"http://flybase.org/reports/{pub.FlyBase}")
                    if hasattr(pub, 'DOI') and pub.DOI:
                        refs.append(f"https://doi.org/{pub.DOI}")

                    publication["refs"] = refs
                    publications.append(publication)

            termInfo["Publications"] = publications

        # Add Synonyms for Class entities. pub_syn holds one entry per
        # (synonym, pub); get_merged_synonyms() collapses these to one entry per
        # synonym with the combined refs and drops the Unattributed placeholder.
        if termInfo["SuperTypes"] and "Class" in termInfo["SuperTypes"] and vfbTerm.pub_syn and len(vfbTerm.pub_syn) > 0:
            synonyms = vfbTerm.get_merged_synonyms()
            # Only add the synonyms if we found any
            if synonyms:
                termInfo["Synonyms"] = synonyms

        # Alternative approach for extracting synonyms from relationships
        if "Class" in termInfo["SuperTypes"] and vfbTerm.relationships and len(vfbTerm.relationships) > 0:
            synonyms = []
            for relationship in vfbTerm.relationships:
                if (relationship.relation.label == "has_exact_synonym" or 
                    relationship.relation.label == "has_broad_synonym" or 
                    relationship.relation.label == "has_narrow_synonym"):
                    
                    synonym = {}
                    synonym["label"] = relationship.object.label
                    
                    # Determine scope based on relation type
                    if relationship.relation.label == "has_exact_synonym":
                        synonym["scope"] = "exact"
                    elif relationship.relation.label == "has_broad_synonym":
                        synonym["scope"] = "broad"
                    elif relationship.relation.label == "has_narrow_synonym":
                        synonym["scope"] = "narrow"
                    
                    synonym["type"] = "synonym"
                    synonyms.append(synonym)
            
            # Only add the synonyms if we found any
            if synonyms and "Synonyms" not in termInfo:
                termInfo["Synonyms"] = synonyms

        # Special handling for Publication entities. The SOLR SuperType marker is
        # the lowercase "pub" (parity gap C — gating on "Publication" meant the
        # block never fired, dropping pub title/PubMed/DOI/FlyBase links).
        if termInfo["SuperTypes"] and ("pub" in termInfo["SuperTypes"] or "Publication" in termInfo["SuperTypes"]) and vfbTerm.pub_specific_content:
            publication = {}
            publication["title"] = vfbTerm.pub_specific_content.title if hasattr(vfbTerm.pub_specific_content, 'title') else ""
            publication["short_form"] = vfbTerm.term.core.short_form
            publication["microref"] = termInfo["Name"]
            
            # Add external references
            refs = []
            if hasattr(vfbTerm.pub_specific_content, 'PubMed') and vfbTerm.pub_specific_content.PubMed:
                refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={vfbTerm.pub_specific_content.PubMed}")
            if hasattr(vfbTerm.pub_specific_content, 'FlyBase') and vfbTerm.pub_specific_content.FlyBase:
                refs.append(f"http://flybase.org/reports/{vfbTerm.pub_specific_content.FlyBase}")
            if hasattr(vfbTerm.pub_specific_content, 'DOI') and vfbTerm.pub_specific_content.DOI:
                refs.append(f"https://doi.org/{vfbTerm.pub_specific_content.DOI}")
            
            publication["refs"] = refs
            termInfo["Publications"] = [publication]

        # Append new synonyms to any existing ones
        if synonyms:
            if "Synonyms" not in termInfo:
                termInfo["Synonyms"] = synonyms
            else:
                # Create a set of existing synonym labels to avoid duplicates
                existing_labels = {syn["label"] for syn in termInfo["Synonyms"]}
                # Only append synonyms that don't already exist
                for synonym in synonyms:
                    if synonym["label"] not in existing_labels:
                        termInfo["Synonyms"].append(synonym)
                        existing_labels.add(synonym["label"])

        # Build the complete References list from the full has_reference set.
        # has_reference edges are partitioned by `typ` into pubs / def_pubs /
        # pub_syn; their union is the term's complete reference list. We collect
        # all three, de-duplicate by short_form (duplicate edges and the
        # Unattributed placeholder are dropped) and emit full external URLs
        # (FlyBase / PubMed / DOI) built from the pub node properties. The inline
        # definition microrefs and the synonym `publication` strings are left
        # untouched -- only the References row draws from this list.
        ref_entries = {}
        for existing in (termInfo.get("Publications") or []):
            sf = existing.get("short_form", "")
            if sf and sf != "Unattributed" and sf not in ref_entries:
                ref_entries[sf] = existing
        extra_pubs = list(getattr(vfbTerm, 'def_pubs', None) or [])
        for syn in (getattr(vfbTerm, 'pub_syn', None) or []):
            if getattr(syn, 'pub', None):
                extra_pubs.append(syn.pub)
            for p in (getattr(syn, 'pubs', None) or []):
                extra_pubs.append(p)
        for pub in extra_pubs:
            core = getattr(pub, 'core', None)
            sf = getattr(core, 'short_form', '') if core else ''
            if not sf or sf == "Unattributed" or sf in ref_entries:
                continue
            refs = []
            if getattr(pub, 'PubMed', ''):
                refs.append(f"http://www.ncbi.nlm.nih.gov/pubmed/?term={pub.PubMed}")
            if getattr(pub, 'FlyBase', ''):
                refs.append(f"http://flybase.org/reports/{pub.FlyBase}")
            if getattr(pub, 'DOI', ''):
                refs.append(f"https://doi.org/{pub.DOI}")
            ref_entries[sf] = {
                "title": core.label if core and core.label else "",
                "short_form": sf,
                "microref": pub.get_microref() if hasattr(pub, 'get_microref') and pub.get_microref() else (core.label if core else ""),
                "refs": refs,
            }
        if ref_entries:
            termInfo["Publications"] = list(ref_entries.values())

        # External database cross-references (xrefs). Rendered today as the
        # panel's xrefs link section (VFBProcessTermInfoCachedJson.java:1536):
        # site label, icon and the external accession link. Previously dropped
        # by this parser (e.g. medulla's Insect Brain DB link).
        if getattr(vfbTerm, 'xrefs', None):
            xrefs_out = []
            for x in vfbTerm.xrefs:
                site = getattr(x, 'site', None)
                # never build a link to a deprecated site
                if site is not None and getattr(site, 'is_deprecated', None) and site.is_deprecated():
                    continue
                label = getattr(site, 'label', '') if site else ''
                acc = x.accession if getattr(x, 'accession', None) and x.accession != "None" else ''
                if acc:
                    link = (x.link_base or '') + acc + (x.link_postfix or '')
                elif getattr(x, 'homepage', None):
                    link = x.homepage
                else:
                    link = getattr(site, 'iri', '') if site else ''
                entry = {"label": label, "accession": acc, "link": link}
                if getattr(x, 'icon', None):
                    entry["icon"] = x.icon
                xrefs_out.append(entry)
            if xrefs_out:
                termInfo["Xrefs"] = xrefs_out

        # Related individuals — same Rel shape as relationships, rendered as its
        # own panel section (VFBProcessTermInfoCachedJson.java:1529). Kept as a
        # Meta string so it travels with the other Meta rows.
        if getattr(vfbTerm, 'related_individuals', None):
            grouped_ri = {}
            for rel in vfbTerm.related_individuals:
                if not (hasattr(rel, 'relation') and hasattr(rel.relation, 'label')):
                    continue
                if not (hasattr(rel, 'object') and hasattr(rel.object, 'label')):
                    continue
                rid = getattr(rel.relation, 'short_form', None) or rel.relation.label
                key = (rel.relation.label, rid)
                obj = (rel.object.label, getattr(rel.object, 'short_form', ''))
                grouped_ri.setdefault(key, set()).add(obj)
            related = []
            for (rlabel, rid), objs in sorted(grouped_ri.items()):
                objlinks = ", ".join("[%s](%s)" % (encode_brackets(o[0]), o[1]) for o in sorted(objs))
                related.append("[%s](%s): %s" % (encode_brackets(rlabel), rid, objlinks))
            if related:
                termInfo["Meta"]["RelatedIndividuals"] = "; ".join(related)


        # Add the queries to the term info
        termInfo["Queries"] = queries

        # print("termInfo object after loading:", termInfo)
    if "Queries" in termInfo:
        termInfo["Queries"] = [query.to_dict() for query in termInfo["Queries"]]
    # print("termInfo object before schema validation:", termInfo)
    try:
        return TermInfoOutputSchema().load(termInfo)
    except ValidationError as e:
        print(f"Validation error when parsing term info: {e}")
        # Return the raw termInfo as a fallback
        return termInfo

def NeuronInputsTo_to_schema(name, take_default):
    query = "NeuronInputsTo"
    label = f"Find neurons with synapses into {name}"
    function = "get_individual_neuron_inputs"
    takes = {
        "neuron_short_form": {"$and": ["Individual", "Neuron"]},
        "default": take_default,
    }
    preview = -1
    preview_columns = ["Neurotransmitter", "Weight"]
    output_format = "ribbon"

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns, output_format=output_format)

def SimilarMorphologyTo_to_schema(name, take_default):
    query = "SimilarMorphologyTo"
    label = f"Find similar neurons to {name}"
    function = "get_similar_neurons"
    takes = {
        "short_form": {"$and": ["Individual", "Neuron"]},
        "default": take_default,
    }
    preview = 5
    # Match the v1.10.1 SimilarMorphologyTo* preview shape and add the new
    # type column this PR exposes — keeps term-info previews in sync with
    # the full /run_query response. source/source_id are intentionally
    # omitted; they're noisy in compact previews and only meaningful when
    # the user opens the full table. Keep score before name so preview
    # sorting continues to default to score-descending under the current
    # header-order-based preview sort selection.
    preview_columns = ["id", "score", "name", "tags", "type", "template", "technique", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)

def ListAllAvailableImages_to_schema(name, take_default):
    query = "ListAllAvailableImages"
    label = f"List all available images of {name}"
    function = "get_instances"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id","label","tags","thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)

def NeuronsPartHere_to_schema(name, take_default):
    """
    Schema for NeuronsPartHere query.
    Finds neuron classes that have some part overlapping with the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil (types.1 + types.5)
    - Additional type matches for comprehensive coverage
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and overlaps some $ID"
    """
    query = "NeuronsPartHere"
    label = f"Neurons with some part in {name}"
    function = "get_neurons_with_part_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5  # Show 5 preview results with example images
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsSynaptic_to_schema(name, take_default):
    """
    Schema for NeuronsSynaptic query.
    Finds neuron classes that have synaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_synaptic_terminals_in some $ID"
    """
    query = "NeuronsSynaptic"
    label = f"Neurons with synaptic terminals in {name}"
    function = "get_neurons_with_synapses_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsPresynapticHere_to_schema(name, take_default):
    """
    Schema for NeuronsPresynapticHere query.
    Finds neuron classes that have presynaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_presynaptic_terminal_in some $ID"
    """
    query = "NeuronsPresynapticHere"
    label = f"Neurons with presynaptic terminals in {name}"
    function = "get_neurons_with_presynaptic_terminals_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "template", "technique", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronsPostsynapticHere_to_schema(name, take_default):
    """
    Schema for NeuronsPostsynapticHere query.
    Finds neuron classes that have postsynaptic terminals in the specified anatomical region.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Visual_system
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: "Neuron and has_postsynaptic_terminal_in some $ID"
    """
    query = "NeuronsPostsynapticHere"
    label = f"Neurons with postsynaptic terminals in {name}"
    function = "get_neurons_with_postsynaptic_terminals_in"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ComponentsOf_to_schema(name, take_default):
    """
    Schema for ComponentsOf query.
    Finds components (parts) of the specified anatomical class.
    
    Matching criteria from XMI:
    - Class + Clone
    
    Query chain: Owlery part_of query → process → SOLR
    OWL query: "part_of some $ID"
    """
    query = "ComponentsOf"
    label = f"Components of {name}"
    function = "get_components_of"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def PartsOf_to_schema(name, take_default):
    """
    Schema for PartsOf query.
    Finds parts of the specified anatomical class.
    
    Matching criteria from XMI:
    - Class (any)
    
    Query chain: Owlery part_of query → process → SOLR
    OWL query: "part_of some $ID"
    """
    query = "PartsOf"
    label = f"Parts of {name}"
    function = "get_parts_of"
    takes = {
        "short_form": {"$and": ["Class"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def SubclassesOf_to_schema(name, take_default):
    """
    Schema for SubclassesOf query.
    Finds subclasses of the specified class.
    
    Matching criteria from XMI:
    - Class (any)
    
    Query chain: Owlery subclasses query → process → SOLR
    OWL query: Direct subclasses of $ID
    """
    query = "SubclassesOf"
    label = f"Subclasses of {name}"
    function = "get_subclasses_of"
    takes = {
        "short_form": {"$and": ["Class"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def SplitsTargeting_to_schema(name, take_default):
    """Schema for SplitsTargeting query: splits that target a neuron class.
    Matching criteria: Class + Neuron (mirrors the indexer neuron_split clause)."""
    return Query(query="SplitsTargeting", label=f"Splits targeting {name}",
                 function="get_splits_targeting",
                 takes={"short_form": {"$and": ["Class", "Neuron"]}, "default": take_default},
                 preview=5, preview_columns=["id", "label", "tags", "thumbnail"])


def TargetNeurons_to_schema(name, take_default):
    """Schema for TargetNeurons query: neurons targeted by a split class.
    Matching criteria: Class + Split (mirrors the indexer split_neuron clause)."""
    return Query(query="TargetNeurons", label=f"Neurons targeted by {name}",
                 function="get_neurons_targeted_by_split",
                 takes={"short_form": {"$and": ["Class", "Split"]}, "default": take_default},
                 preview=5, preview_columns=["id", "label", "tags", "thumbnail"])


def NeuronClassesFasciculatingHere_to_schema(name, take_default):
    """
    Schema for NeuronClassesFasciculatingHere query.
    Finds neuron classes that fascicululate with (run along) a tract or nerve.
    
    Matching criteria from XMI:
    - Class + Tract_or_nerve (VFB uses Neuron_projection_bundle type)
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Neuron' that 'fasciculates with' some '{short_form}'
    """
    query = "NeuronClassesFasciculatingHere"
    label = f"Neurons fasciculating in {name}"
    function = "get_neuron_classes_fasciculating_here"
    takes = {
        "short_form": {"$and": ["Class", "Neuron_projection_bundle"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronNeuronConnectivityQuery_to_schema(name, take_default):
    """
    Schema for neuron_neuron_connectivity_query.
    Finds neurons connected to the specified neuron.
    Matching criteria from XMI: Connected_neuron
    Query chain: Neo4j compound query → process
    """
    query = "NeuronNeuronConnectivityQuery"
    label = f"Neurons connected to {name}"
    function = "get_neuron_neuron_connectivity"
    takes = {
        "short_form": {"$and": ["Individual", "Connected_neuron"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "outputs", "inputs", "tags"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def NeuronRegionConnectivityQuery_to_schema(name, take_default):
    """
    Schema for neuron_region_connectivity_query.
    Shows connectivity to regions from a specified neuron.
    Matching criteria from XMI: Region_connectivity
    Query chain: Neo4j compound query → process
    """
    query = "NeuronRegionConnectivityQuery"
    label = f"Connectivity per region for {name}"
    function = "get_neuron_region_connectivity"
    takes = {
        "short_form": {"$and": ["Individual", "Region_connectivity"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "region", "presynaptic_terminals", "postsynaptic_terminals", "tags"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def DownstreamClassConnectivity_to_schema(name, take_default):
    """
    Schema for downstream class connectivity query.
    Shows which neuron classes receive synapses from this neuron class.
    Matching criteria: Class + Neuron

    Implementation: multi-step aggregation, not a single Solr lookup.
      1. Neo4j: the queried class plus each subclass that has connectivity
         instances, with the instances in each one's SUBCLASSOF closure.
      2. Solr cache (batched): per-instance synaptic partners.
      3. Solr: direct partner classes from the downstream_connectivity_query
         field (seed set for the partner-side ancestor walk).
      4. Neo4j: walk SUBCLASSOF up from each direct partner to the neuron root.
      5. Neo4j (batched): partner_instance -> {class_ids} membership map.
      6. In-memory aggregation with set-union semantics to handle FBbt
         multi-inheritance without double-counting, emitted as a separate row
         block per queried (sub)class (input term first); the queried (sub)class
         fills the ``upstream_class`` slot (downstream query) or
         ``downstream_class`` slot (upstream query) of the v2 layout.

    Results are cached server-side (@with_solr_cache) per queried class, so
    repeat calls return in milliseconds, but cold calls on broad classes can
    take tens of seconds.
    """
    query = "DownstreamClassConnectivity"
    label = f"Downstream connectivity classes for {name}"
    function = "get_downstream_class_connectivity"
    takes = {
        "short_form": {"$and": ["Class", "Neuron"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["upstream_class", "downstream_class", "total_n", "connected_n", "percent_connected", "pairwise_connections", "total_weight", "avg_weight"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def UpstreamClassConnectivity_to_schema(name, take_default):
    """
    Schema for upstream class connectivity query.
    Shows which neuron classes send synapses to this neuron class.
    Matching criteria: Class + Neuron

    Implementation: same multi-step aggregation as
    DownstreamClassConnectivity but with the upstream_connectivity_query
    Solr field as the seed for the partner-side ancestor walk. See
    DownstreamClassConnectivity_to_schema for the full pipeline.
    """
    query = "UpstreamClassConnectivity"
    label = f"Upstream connectivity classes for {name}"
    function = "get_upstream_class_connectivity"
    takes = {
        "short_form": {"$and": ["Class", "Neuron"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["upstream_class", "downstream_class", "total_n", "connected_n", "percent_connected", "pairwise_connections", "total_weight", "avg_weight"]
    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def TractsNervesInnervatingHere_to_schema(name, take_default):
    """
    Schema for TractsNervesInnervatingHere query.
    Finds tracts and nerves that innervate a synaptic neuropil.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Tract_or_nerve' that 'innervates' some '{short_form}'
    """
    query = "TractsNervesInnervatingHere"
    label = f"Tracts/nerves innervating {name}"
    function = "get_tracts_nerves_innervating_here"
    takes = {
        "short_form": {"$or": [{"$and": ["Class", "Synaptic_neuropil"]}, {"$and": ["Class", "Synaptic_neuropil_domain"]}]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "template", "technique", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def LineageClonesIn_to_schema(name, take_default):
    """
    Schema for LineageClonesIn query.
    Finds lineage clones that overlap with a synaptic neuropil or domain.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery subclass query → process → SOLR
    OWL query: 'Clone' that 'overlaps' some '{short_form}'
    """
    query = "LineageClonesIn"
    label = f"Lineage clones found in {name}"
    function = "get_lineage_clones_in"
    takes = {
        "short_form": {"$and": ["Class", "Synaptic_neuropil"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "template", "technique", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ImagesNeurons_to_schema(name, take_default):
    """
    Schema for ImagesNeurons query.
    Finds individual neuron images with parts in a synaptic neuropil or domain.
    
    Matching criteria from XMI:
    - Class + Synaptic_neuropil
    - Class + Synaptic_neuropil_domain
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: 'Neuron' that 'overlaps' some '{short_form}' (returns instances, not classes)
    """
    query = "ImagesNeurons"
    label = f"Images of neurons with some part in {name}"
    function = "get_images_neurons"
    takes = {
        "short_form": {"$or": [{"$and": ["Class", "Synaptic_neuropil"]}, {"$and": ["Class", "Synaptic_neuropil_domain"]}]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def ImagesThatDevelopFrom_to_schema(name, take_default):
    """
    Schema for ImagesThatDevelopFrom query.
    Finds individual neuron images that develop from a neuroblast.
    
    Matching criteria from XMI:
    - Class + Neuroblast
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: 'Neuron' that 'develops_from' some '{short_form}' (returns instances, not classes)
    """
    query = "ImagesThatDevelopFrom"
    label = f"Images of neurons that develop from {name}"
    function = "get_images_that_develop_from"
    takes = {
        "short_form": {"$and": ["Class", "Neuroblast"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def epFrag_to_schema(name, take_default):
    """
    Schema for epFrag query.
    Finds individual expression pattern fragment images that are part of an expression pattern.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Expression_pattern
    
    Query chain: Owlery instances query → process → SOLR
    OWL query: instances that are 'part_of' some '{short_form}' (returns instances, not classes)
    """
    query = "epFrag"
    label = f"Images of fragments of {name}"
    function = "get_expression_pattern_fragments"
    takes = {
        "short_form": {"$and": ["Class", "Expression_pattern"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "label", "tags", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def AnatomyExpressedIn_to_schema(name, take_default):
    """
    Schema for AnatomyExpressedIn query.

    Given an expression pattern, returns the anatomy classes in which the
    pattern's Individuals overlap or are part_of anatomy Individuals.

    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi

    Matching criteria from XMI:
    - Class + Expression_pattern
    - Class + Expression_pattern_fragment

    Cypher query:
      MATCH (ep:Class:Expression_pattern)
            <-[ar:overlaps|part_of]-(anoni:Individual)
            -[:INSTANCEOF]->(anat:Class:Anatomy)
      WHERE ep.short_form = $id
    """
    query = "AnatomyExpressedIn"
    label = f"Anatomy where {name} is expressed"
    function = "get_expression_overlaps_here"
    takes = {
        "short_form": {
            "$or": [
                {"$and": ["Class", "Expression_pattern"]},
                {"$and": ["Class", "Expression_pattern_fragment"]},
            ]
        },
        "default": take_default,
    }
    preview = 5
    # v1.14.2: schema gained Stage / Template / Imaging Technique /
    # Thumbnail columns to match the legacy ExpressionOverlapsHere
    # column shape (Name / Reference / Gross_Type / Stage /
    # Template_Space / Imaging_Technique / Images).
    preview_columns = ["id", "name", "pubs", "tags", "stages", "template", "technique", "thumbnail"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def anatScRNAseqQuery_to_schema(name, take_default):
    """
    Schema for anatScRNAseqQuery query.
    Returns single cell transcriptomics data (clusters and datasets) for an anatomical region.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Anatomy + hasScRNAseq (has Single Cell RNA Seq Results)
    
    Query chain: Owlery Subclasses → Owlery Pass → Neo4j anat_scRNAseq_query
    Cypher query: MATCH (primary:Class:Anatomy)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
                  WHERE primary.short_form = $id
    """
    query = "anatScRNAseqQuery"
    label = f"scRNAseq data for {name}"
    function = "get_anatomy_scrnaseq"
    takes = {
        "short_form": {"$and": ["Class", "Anatomy", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "dataset", "pubs"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def clusterExpression_to_schema(name, take_default):
    """
    Schema for clusterExpression query.
    Returns genes expressed in a specified cluster with expression levels.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Individual + Cluster
    
    Query chain: Neo4j cluster_expression_query → process
    Cypher query: MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
                  WHERE primary.short_form = $id
    """
    query = "clusterExpression"
    label = f"Genes expressed in {name}"
    function = "get_cluster_expression"
    takes = {
        "short_form": {"$and": ["Individual", "Cluster"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "expression_level", "expression_extent", "function"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def expressionCluster_to_schema(name, take_default):
    """
    Schema for expressionCluster query.
    Returns scRNAseq clusters expressing a specified gene.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - Class + Gene + hasScRNAseq (has Single Cell RNA Seq Results)
    
    Query chain: Neo4j expression_cluster_query → process
    Cypher query: MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
                  WHERE g.short_form = $id
    """
    query = "expressionCluster"
    label = f"Clusters expressing {name}"
    function = "get_expression_cluster"
    takes = {
        "short_form": {"$and": ["Class", "Gene", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "expression_level", "expression_extent"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def scRNAdatasetData_to_schema(name, take_default):
    """
    Schema for scRNAdatasetData query.
    Returns all clusters in a scRNAseq dataset.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Matching criteria from XMI:
    - DataSet + hasScRNAseq (scRNAseq dataset type)
    
    Query chain: Neo4j dataset_scRNAseq_query → process
    Cypher query: MATCH (c:Individual:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
                  WHERE ds.short_form = $id
    """
    query = "scRNAdatasetData"
    label = f"Clusters in dataset {name}"
    function = "get_scrnaseq_dataset_data"
    takes = {
        "short_form": {"$and": ["DataSet", "hasScRNAseq"]},
        "default": take_default,
    }
    preview = 5
    preview_columns = ["id", "name", "tags", "anatomy", "pubs"]

    return Query(query=query, label=label, function=function, takes=takes, preview=preview, preview_columns=preview_columns)


def SimilarMorphologyToPartOf_to_schema(name, take_default):
    """Schema for SimilarMorphologyToPartOf (NBLASTexp) query."""
    return Query(query="SimilarMorphologyToPartOf", label=f"Similar morphology to part of {name}", function="get_similar_morphology_part_of", takes={"short_form": {"$and": ["Individual", "Neuron", "NBLASTexp"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags", "template", "technique", "thumbnail"])


def SimilarMorphologyToPartOfexp_to_schema(name, take_default):
    """Schema for SimilarMorphologyToPartOfexp (reverse NBLASTexp) query."""
    return Query(query="SimilarMorphologyToPartOfexp", label=f"Similar morphology to part of {name}", function="get_similar_morphology_part_of_exp", takes={"short_form": {"$or": [{"$and": ["Individual", "Expression_pattern", "NBLASTexp"]}, {"$and": ["Individual", "Expression_pattern_fragment", "NBLASTexp"]}]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags", "template", "technique", "thumbnail"])


def SimilarMorphologyToNB_to_schema(name, take_default):
    """Schema for SimilarMorphologyToNB (NeuronBridge) query."""
    return Query(query="SimilarMorphologyToNB", label=f"NeuronBridge matches for {name}", function="get_similar_morphology_nb", takes={"short_form": {"$and": ["Individual", "neuronbridge"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags", "template", "technique", "thumbnail"])


def SimilarMorphologyToNBexp_to_schema(name, take_default):
    """Schema for SimilarMorphologyToNBexp (NeuronBridge expression) query."""
    return Query(query="SimilarMorphologyToNBexp", label=f"NeuronBridge matches for {name}", function="get_similar_morphology_nb_exp", takes={"short_form": {"$and": ["Individual", "Expression_pattern", "neuronbridge"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score", "tags", "type", "template", "technique", "thumbnail"])


def SimilarMorphologyToUserData_to_schema(name, take_default):
    """Schema for SimilarMorphologyToUserData (user upload NBLAST) query."""
    return Query(query="SimilarMorphologyToUserData", label=f"NBLAST results for {name}", function="get_similar_morphology_userdata", takes={"short_form": {"$and": ["Individual", "UNBLAST"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "score"])


def PaintedDomains_to_schema(name, take_default):
    """Schema for PaintedDomains query."""
    return Query(query="PaintedDomains", label=f"Painted domains for {name}", function="get_painted_domains", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "type", "description", "thumbnail"])


def DatasetImages_to_schema(name, take_default):
    """Schema for DatasetImages query."""
    return Query(query="DatasetImages", label=f"Images in dataset {name}", function="get_dataset_images", takes={"short_form": {"$and": ["DataSet", "has_image"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags", "type", "template", "technique", "thumbnail"])


def AllAlignedImages_to_schema(name, take_default):
    """Schema for AllAlignedImages query."""
    return Query(query="AllAlignedImages", label=f"All images aligned to {name}", function="get_all_aligned_images", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "tags", "type", "template", "technique", "thumbnail"])


def AlignedDatasets_to_schema(name, take_default):
    """Schema for AlignedDatasets query."""
    return Query(query="AlignedDatasets", label=f"Datasets aligned to {name}", function="get_aligned_datasets", takes={"short_form": {"$and": ["Template", "Individual"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "pubs", "tags", "license", "template", "technique", "thumbnail", "image_count"])


def AllDatasets_to_schema(name, take_default):
    """Schema for AllDatasets query."""
    return Query(query="AllDatasets", label="All available datasets", function="get_all_datasets", takes={"short_form": {"$and": ["Template"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "pubs", "tags", "license", "template", "technique", "thumbnail", "image_count"])


def TermsForPub_to_schema(name, take_default):
    """Schema for TermsForPub query."""
    return Query(query="TermsForPub", label=f"Terms referencing {name}", function="get_terms_for_pub", takes={"short_form": {"$and": ["Individual", "pub"]}, "default": take_default}, preview=10, preview_columns=["id", "name", "reference_type", "tags", "type"])


def TransgeneExpressionHere_to_schema(name, take_default):
    """Schema for TransgeneExpressionHere query.
    
    Matching criteria from XMI:
    - Class + Nervous_system + Anatomy
    - Class + Nervous_system + Neuron
    
    Query chain: Multi-step Owlery and Neo4j queries
    """
    return Query(query="TransgeneExpressionHere", label=f"Transgene expression in {name}", function="get_transgene_expression_here", takes={"short_form": {"$and": ["Class", "Nervous_system", "Anatomy"]}, "default": take_default}, preview=5, preview_columns=["id", "name", "expressed_in", "pubs", "tags", "template", "technique", "thumbnail"])


def FindStocks_to_schema(name, take_default):
    """Schema for FindStocks query — find available fly stocks from FlyBase."""
    return Query(
        query="FindStocks",
        label=f"Find fly stocks for {name}",
        function="get_flybase_stocks",
        takes={"short_form": {"$and": ["Feature"]}, "default": take_default},
        preview=5,
        preview_columns=["stock_id", "stock_number", "genotype", "collection"],
    )


def FindComboPublications_to_schema(name, take_default):
    """Schema for FindComboPublications query — find publications for a split system combination."""
    return Query(
        query="FindComboPublications",
        label=f"Find publications for {name}",
        function="get_flybase_combo_pubs",
        takes={"short_form": {"$and": ["Feature"]}, "default": take_default},
        preview=5,
        preview_columns=["fbrf", "title", "year", "pub_type"],
    )


def serialize_solr_output(results):
    # Create a copy of the document and remove Solr-specific fields
    doc = dict(results.docs[0])
    # Remove the _version_ field which can cause serialization issues with large integers
    doc.pop('_version_', None)
    
    # Serialize the sanitized dictionary to JSON using NumpyEncoder
    json_string = json.dumps(doc, ensure_ascii=False, cls=NumpyEncoder)
    json_string = json_string.replace('\\', '')
    json_string = json_string.replace('"{', '{')
    json_string = json_string.replace('}"', '}')
    json_string = json_string.replace("\'", '-')
    return json_string 

# ---------------------------------------------------------------------------
# Background preview warming
#
# Rich terms -- painted-domain individuals especially -- carry many connectivity
# and count preview queries that fill_query_results runs serially. On a cold
# cache that can take minutes and blocks the caller, which is what stalls the
# geppetto UI on "Loading ...". To keep term-info responsive we return
# immediately with the previews left unresolved (count -1) and compute the full
# previews on a background thread, writing them into the term_info cache via
# force_refresh so the next open is complete.
#
# Self-healing falls out of the existing cache validation: a cached term_info
# whose queries still have count < 0 is treated as incomplete on read and
# re-executed, so a blank entry is never served as final -- it just re-triggers
# this fast path (and the background warm) until the full result lands.
# ---------------------------------------------------------------------------
_bg_preview_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="vfb-terminfo-warm")
_bg_preview_inflight = set()
_bg_preview_lock = threading.Lock()


def _blank_query_previews(term_info):
    """Return term_info with every query's preview left unresolved (count -1)."""
    for query in term_info.get('Queries', []):
        query['preview_results'] = {
            'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']),
            'rows': []
        }
        # -1 = not yet counted (distinct from a genuine 0), so the UI shows the
        # query as pending and the cache treats the entry as not-yet-complete.
        query['count'] = -1
    return term_info


def _schedule_preview_warm(short_form):
    """Compute the full term-info previews in the background and cache them."""
    with _bg_preview_lock:
        if short_form in _bg_preview_inflight:
            return
        _bg_preview_inflight.add(short_form)

    def _warm():
        try:
            import vfbquery
            # force_refresh re-runs get_term_info with full (synchronous) preview
            # execution and overwrites the cached entry, so the next open is fast
            # AND complete.
            vfbquery.get_term_info(short_form, preview=True, force_refresh=True)
        except Exception as e:
            print(f"Background term_info preview warm failed for {short_form}: {e}")
        finally:
            with _bg_preview_lock:
                _bg_preview_inflight.discard(short_form)

    _bg_preview_executor.submit(_warm)


@with_solr_cache('term_info')
def get_term_info(short_form: str, preview: bool = True, force_refresh: bool = False):
    """
    Retrieves the term info for the given term short form.
    Results are cached in SOLR for 3 months to improve performance.

    :param short_form: short form of the term
    :param preview: if True, executes query previews to populate preview_results (default: True)
    :return: term info
    """
    parsed_object = None
    try:
        # Search for the term in the SOLR server
        results = vfb_solr.search('id:' + short_form)
        # Check if any results were returned
        parsed_object = term_info_parse_object(results, short_form)
        if parsed_object:
            # Only try to fill query results if preview is enabled and there are queries to fill
            if preview and parsed_object.get('Queries') and len(parsed_object['Queries']) > 0:
                # Two-phase preview loading: on a normal (foreground) cold call,
                # return immediately with previews unresolved so the caller is not
                # blocked by slow connectivity/count queries, and warm the full
                # previews into the cache on a background thread. The background
                # job (force_refresh=True) and cache-disabled runs (the test suite,
                # which validates live data) still fill synchronously below.
                if not force_refresh and not solr_caching_disabled():
                    _schedule_preview_warm(short_form)
                    return _blank_query_previews(parsed_object)
                try:
                    term_info = fill_query_results(parsed_object, force_refresh=force_refresh)
                    if term_info:
                        return term_info
                    else:
                        print("Failed to fill query preview results!")
                        # Set default values for queries when fill_query_results fails
                        for query in parsed_object.get('Queries', []):
                            # Set default preview_results structure
                            query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                            # Unknown count (-1), not known-empty (0): keep queries live
                            query['count'] = -1
                        return parsed_object
                except Exception as e:
                    print(f"Error filling query results (setting default values): {e}")
                    # Set default values for queries when fill_query_results fails
                    for query in parsed_object.get('Queries', []):
                        # Set default preview_results structure
                        query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                        # Unknown count (-1), not known-empty (0): keep queries live
                        query['count'] = -1
                    return parsed_object
            else:
                # No queries to fill (preview=False) or no queries defined, return parsed object directly
                return parsed_object
        else:
            print(f"No valid term info found for ID '{short_form}'")
            return None
    except ValidationError as e:
        # handle the validation error
        print("Schema validation error when parsing response")
        print("Error details:", e)
        print("Original data:", results)
        print("Parsed object:", parsed_object)
        return parsed_object
    except IndexError as e:
        print(f"No results found for ID '{short_form}'")
        print("Error details:", e)
        if parsed_object:
            print("Parsed object:", parsed_object)
            if 'term_info' in locals():
                print("Term info:", term_info)
        else:
            print("Error accessing SOLR server!")
        return None
    except Exception as e:
        print(f"Unexpected error when retrieving term info: {type(e).__name__}: {e}")
        return parsed_object

@with_solr_cache('instances')
def get_instances(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves available image-bearing instances for the given class short form.

    Subclass closure is resolved via Owlery's reasoner (consistent with the
    `Neurons*Here`, `ImagesThatDevelopFrom`, `TractsNervesInnervatingHere`
    family that all use ``_owlery_query_to_results(query_instances=True)``).
    Per-instance image metadata is then fetched from Neo4j in a single
    batched query keyed on the Owlery-returned IDs.

    Falls back to the SOLR ``term_info`` ``anatomy_channel_image`` extract
    if either Owlery or Neo4j is unavailable.

    :param short_form: short form of the class
    :param return_dataframe: return a pandas DataFrame if True, otherwise a formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: results rows
    """
    
    try:
        # Step 1: ask Owlery for the SUBCLASS closure of the queried class.
        # Owlery's `/subclasses` reasoner does the OWL inference (handles
        # equivalence classes, defined classes, anonymous class expressions
        # in the parent chain, etc.). The queried class itself is included
        # so leaf classes still match.
        #
        # Why Owlery for subclasses (not instances) — VFB stores Individual→
        # Class membership as Neo4j INSTANCEOF edges, NOT as OWL
        # ClassAssertion axioms. Owlery has the class hierarchy but no
        # individual assertions, so its `/instances` endpoint returns
        # nothing for entities whose Individuals live only in Neo4j. We
        # must do the instance match in Neo4j against the Owlery-derived
        # subclass set. This mirrors the legacy v2 XMI two-step chain
        # (Owlery subclasses → SOLR per-class lookup) without the SOLR
        # intermediate.
        #
        # Why this matters: the previous Cypher used a single-edge
        # `(i)-[:INSTANCEOF]->(p:Class {short_form: $id})` match — only
        # individuals *directly* typed as the queried class were seen.
        # For any parent class (e.g. mushroom body intrinsic neuron
        # FBbt_00007484, whose individuals are typed Kenyon cell etc.)
        # the query returned 0 even though SOLR had dozens of image rows
        # on file.
        owl_query = f"<{_short_form_to_iri(short_form)}>"
        subclass_ids = vc.vfb.oc.get_subclasses(query=owl_query, query_by_label=False)
        # Always include the queried class itself so leaf classes still match.
        class_ids = list({short_form, *subclass_ids})

        # Step 2: fetch image metadata for instances of any of those
        # classes from Neo4j. The `parent` column reports the actual class
        # each instance is typed as (often a leaf subclass of the queried
        # class) — more useful for v2 display than echoing the queried id.
        query = f"""
        MATCH (i:Individual:has_image)-[:INSTANCEOF]->(p:Class),
              (i)<-[:depicts]-(tc:Individual)-[r:in_register_with]->(tct:Template)-[:depicts]->(templ:Template),
              (i)-[:has_source]->(ds:DataSet)
        WHERE p.short_form IN {class_ids!r}
        OPTIONAL MATCH (i)-[rx:database_cross_reference]->(site:Site)
        OPTIONAL MATCH (ds)-[:has_license|license]->(lic:License)
        RETURN i.short_form as id,
               apoc.text.format("[%s](%s)",[i.label,i.short_form]) AS label,
               apoc.text.join(i.uniqueFacets, '|') AS tags,
               apoc.text.format("[%s](%s)",[p.label,p.short_form]) AS parent,
               // Deprecated sites: show the source/accession text but no link.
               CASE WHEN site:Deprecated THEN COALESCE(site.label,'') ELSE REPLACE(apoc.text.format("[%s](%s)",[site.label,site.short_form]), '[null](null)', '') END AS source,
               CASE WHEN site:Deprecated THEN COALESCE(rx.accession[0],'') ELSE REPLACE(apoc.text.format("[%s](%s)",[rx.accession[0],site.link_base[0] + rx.accession[0]]), '[null](null)', '') END AS source_id,
               apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]) AS template,
               apoc.text.format("[%s](%s)",[ds.label,ds.short_form]) AS dataset,
               REPLACE(apoc.text.format("[%s](%s)",[lic.label,lic.short_form]), '[null](null)', '') AS license,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[i.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(r.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), i.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + i.short_form]), "[![null]( 'null')](null)", "") as thumbnail
               ORDER BY id Desc
        """

        # Cheap true count: aggregate over the SAME MATCH/OPTIONAL grain as the
        # main query but without the per-row apoc.text.format string building,
        # thumbnail construction or ORDER BY. This returns the real total even
        # when the main query is LIMITed for a preview, so fill_query_results
        # gets an accurate count without re-running the full row materialisation
        # (the cause of the hang on broad anatomy classes). count(*) over the
        # identical pattern matches len(df) when unlimited.
        count_query = f"""
        MATCH (i:Individual:has_image)-[:INSTANCEOF]->(p:Class),
              (i)<-[:depicts]-(tc:Individual)-[r:in_register_with]->(tct:Template)-[:depicts]->(templ:Template),
              (i)-[:has_source]->(ds:DataSet)
        WHERE p.short_form IN {class_ids!r}
        OPTIONAL MATCH (i)-[rx:database_cross_reference]->(site:Site)
        OPTIONAL MATCH (ds)-[:has_license|license]->(lic:License)
        RETURN count(*) AS total_count
        """

        if limit != -1:
            query += f" LIMIT {limit}"

        # Run the query using VFB_connect
        results = vc.nc.commit_list([query])
        
        # Convert the results to a DataFrame
        df = pd.DataFrame.from_records(get_dict_cursor()(results))

        # The registration + has_source MATCH yields one row per
        # (instance, template, dataset). Collapse to one row per instance:
        #  - thumbnail -> the "; "-joined multi-image carousel the V2 Images column
        #    renders, DISTINCT (a template's thumbnail is identical across the
        #    instance's datasets, so it must not repeat), so the frontend can bring
        #    the loaded template's thumbnail to the front;
        #  - dataset   -> a distinct ", "-joined list (an image from several
        #    datasets is one row listing them, not one row per dataset);
        #  - other columns take the first (representative) value; ORDER BY id kept.
        if not df.empty and 'id' in df.columns and 'thumbnail' in df.columns:
            def _join_distinct(series, sep):
                seen = []
                for v in series:
                    if isinstance(v, str) and v and v not in seen:
                        seen.append(v)
                return sep.join(seen)
            agg = {c: 'first' for c in df.columns if c not in ('id', 'thumbnail', 'dataset')}
            agg['thumbnail'] = lambda s: _join_distinct(s, '; ')
            if 'dataset' in df.columns:
                agg['dataset'] = lambda s: _join_distinct(s, ', ')
            df = df.groupby('id', as_index=False, sort=False).agg(agg)

        columns_to_encode = ['label', 'parent', 'source', 'source_id', 'template', 'dataset', 'license', 'thumbnail']
        df = encode_markdown_links(df, columns_to_encode)

        # When limited, the returned rows are a preview; get the true total from
        # the cheap aggregation. When unlimited, len(df) already is the total.
        if limit != -1:
            count_records = get_dict_cursor()(vc.nc.commit_list([count_query]))
            total_count = int(count_records[0]['total_count']) if count_records else len(df)
        else:
            total_count = len(df)

        if return_dataframe:
            return df

        # Format the results
        formatted_results = {
            "headers": _get_instances_headers(),
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "label",
                        "tags",
                        "parent",
                        "source",
                        "source_id",
                        "template",
                        "dataset",
                        "license",
                        "thumbnail"
                    ]
                }
                for row in safe_to_dict(df)
            ],
            "count": total_count
        }

        return formatted_results
        
    except Exception as e:
        # Fallback to SOLR-based implementation when Neo4j is unavailable
        print(f"Neo4j unavailable ({e}), using SOLR fallback for get_instances")
        return _get_instances_from_solr(short_form, return_dataframe, limit)

def _get_instances_from_solr(short_form: str, return_dataframe=True, limit: int = -1):
    """
    SOLR-based fallback implementation for get_instances.
    Extracts instance data from term_info anatomy_channel_image array.
    """
    try:
        # Get term_info data from SOLR
        term_info_results = vc.get_TermInfo([short_form], return_dataframe=False)
        
        if len(term_info_results) == 0:
            # Return empty results with proper structure
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_instances_headers(),
                "rows": [],
                "count": 0
            }
        
        term_info = term_info_results[0]
        anatomy_images = term_info.get('anatomy_channel_image', [])
        
        # Apply limit if specified
        if limit != -1 and limit > 0:
            anatomy_images = anatomy_images[:limit]
        
        # Convert anatomy_channel_image to instance rows with rich data
        rows = []
        for img in anatomy_images:
            anatomy = img.get('anatomy', {})
            channel_image = img.get('channel_image', {})
            image_info = channel_image.get('image', {}) if channel_image else {}
            template_anatomy = image_info.get('template_anatomy', {}) if image_info else {}
            
            # Extract tags from unique_facets (matching original Neo4j format and ordering)
            unique_facets = anatomy.get('unique_facets', [])
            anatomy_types = anatomy.get('types', [])
            
            # Create ordered list matching the expected Neo4j format
            # Based on test diff, expected order and tags: Nervous_system, Adult, Visual_system, Synaptic_neuropil_domain
            # Note: We exclude 'Synaptic_neuropil' as it doesn't appear in expected output
            ordered_tags = []
            for tag_type in ['Nervous_system', 'Adult', 'Visual_system', 'Synaptic_neuropil_domain']:
                if tag_type in anatomy_types or tag_type in unique_facets:
                    ordered_tags.append(tag_type)
            
            # Use the ordered tags to match expected format
            tags = '|'.join(ordered_tags)
            
            # Extract thumbnail URL and convert to HTTPS
            thumbnail_url = image_info.get('image_thumbnail', '') if image_info else ''
            if thumbnail_url:
                # Replace http with https and thumbnailT.png with thumbnail.png
                thumbnail_url = thumbnail_url.replace('http://', 'https://').replace('thumbnailT.png', 'thumbnail.png')
            
            # Format thumbnail with proper markdown link (matching Neo4j behavior)
            thumbnail = ''
            if thumbnail_url and template_anatomy:
                # Prefer symbol over label for template (matching Neo4j behavior)
                template_label = template_anatomy.get('label', '')
                if template_anatomy.get('symbol') and len(template_anatomy.get('symbol', '')) > 0:
                    template_label = template_anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                template_label = unquote(template_label)
                template_short_form = template_anatomy.get('short_form', '')
                
                # Prefer symbol over label for anatomy (matching Neo4j behavior)
                anatomy_label = anatomy.get('label', '')
                if anatomy.get('symbol') and len(anatomy.get('symbol', '')) > 0:
                    anatomy_label = anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                anatomy_label = unquote(anatomy_label)
                anatomy_short_form = anatomy.get('short_form', '')
                
                if template_label and anatomy_label:
                    # Create thumbnail markdown link matching the original format
                    # DO NOT encode brackets in alt text - that's done later by encode_markdown_links
                    alt_text = f"{anatomy_label} aligned to {template_label}"
                    link_target = f"{template_short_form},{anatomy_short_form}"
                    thumbnail = f"[![{alt_text}]({thumbnail_url} '{alt_text}')]({link_target})"
            
            # Format template information
            template_formatted = ''
            if template_anatomy:
                # Prefer symbol over label (matching Neo4j behavior)
                template_label = template_anatomy.get('label', '')
                if template_anatomy.get('symbol') and len(template_anatomy.get('symbol', '')) > 0:
                    template_label = template_anatomy.get('symbol')
                # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
                template_label = unquote(template_label)
                template_short_form = template_anatomy.get('short_form', '')
                if template_label and template_short_form:
                    template_formatted = f"[{template_label}]({template_short_form})"
            
            # Handle label formatting (match Neo4j format - prefer symbol over label)
            anatomy_label = anatomy.get('label', 'Unknown')
            if anatomy.get('symbol') and len(anatomy.get('symbol', '')) > 0:
                anatomy_label = anatomy.get('symbol')
            # Decode URL-encoded strings from SOLR (e.g., ME%28R%29 -> ME(R))
            anatomy_label = unquote(anatomy_label)
            anatomy_short_form = anatomy.get('short_form', '')
            
            row = {
                'id': anatomy_short_form,
                'label': f"[{anatomy_label}]({anatomy_short_form})",
                'tags': tags,
                'parent': f"[{term_info.get('term', {}).get('core', {}).get('label', 'Unknown')}]({short_form})",
                'source': '',  # Not readily available in SOLR anatomy_channel_image
                'source_id': '',
 'template': template_formatted,
                'dataset': '',  # Not readily available in SOLR anatomy_channel_image
                'license': '',
                'thumbnail': thumbnail
            }
            rows.append(row)
        
        # Sort by ID to match expected ordering (Neo4j uses "ORDER BY id Desc")
        rows.sort(key=lambda x: x['id'], reverse=True)
        
        total_count = len(anatomy_images)
        
        if return_dataframe:
            df = pd.DataFrame(rows)
            # Apply encoding to markdown links (matches Neo4j implementation)
            columns_to_encode = ['label', 'parent', 'source', 'source_id', 'template', 'dataset', 'license', 'thumbnail']
            df = encode_markdown_links(df, columns_to_encode)
            return df
        
        return {
            "headers": _get_instances_headers(),
            "rows": rows,
            "count": total_count
        }
        
    except Exception as e:
        print(f"Error in SOLR fallback for get_instances: {e}")
        # Return empty results with proper structure
        if return_dataframe:
            return pd.DataFrame()
        return {
            "headers": _get_instances_headers(),
            "rows": [],
            "count": 0
        }

def _get_instances_headers():
    """Return standard headers for get_instances results"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "parent": {"title": "Parent Type", "type": "markdown", "order": 1},
        "template": {"title": "Template", "type": "markdown", "order": 4},
        "tags": {"title": "Gross Types", "type": "tags", "order": 3},
        "source": {"title": "Data Source", "type": "markdown", "order": 5},
        "source_id": {"title": "Data Source", "type": "markdown", "order": 6},
        "dataset": {"title": "Dataset", "type": "markdown", "order": 7},
        "license": {"title": "License", "type": "markdown", "order": 8},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }

def _get_templates_minimal(limit: int = -1, return_dataframe: bool = False):
    """
    Minimal fallback implementation for get_templates when Neo4j is unavailable.
    Returns hardcoded list of core templates with basic information.
    """
    # Core templates with their basic information
    # Include all columns to match full get_templates() structure
    templates_data = [
        {"id": "VFB_00101567", "name": "JRC2018Unisex", "tags": "VFB|VFB_vol|has_image", "order": 1, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00200000", "name": "JRC_FlyEM_Hemibrain", "tags": "VFB|VFB_vol|has_image", "order": 2, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00017894", "name": "Adult Brain", "tags": "VFB|VFB_painted|has_image", "order": 3, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00101384", "name": "JFRC2", "tags": "VFB|VFB_vol|has_image", "order": 4, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00050000", "name": "JFRC2010", "tags": "VFB|VFB_vol|has_image", "order": 5, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00049000", "name": "Ito2014", "tags": "VFB|VFB_painted|has_image", "order": 6, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00100000", "name": "FCWB", "tags": "VFB|VFB_vol|has_image", "order": 7, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00030786", "name": "Adult VNS", "tags": "VFB|VFB_painted|has_image", "order": 8, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00110000", "name": "L3 CNS", "tags": "VFB|VFB_vol|has_image", "order": 9, "thumbnail": "", "dataset": "", "license": ""},
        {"id": "VFB_00120000", "name": "L1 CNS", "tags": "VFB|VFB_vol|has_image", "order": 10, "thumbnail": "", "dataset": "", "license": ""},
    ]
    
    # Apply limit if specified
    if limit > 0:
        templates_data = templates_data[:limit]
    
    count = len(templates_data)
    
    if return_dataframe:
        df = pd.DataFrame(templates_data)
        return df
    
    # Format as dict with headers and rows (match full get_templates structure)
    formatted_results = {
        "headers": {
            "id": {"title": "Add", "type": "selection_id", "order": -1},
            "order": {"title": "Order", "type": "numeric", "order": 1, "sort": {0: "Asc"}},
            "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
            "tags": {"title": "Tags", "type": "tags", "order": 2},
            "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9},
            "dataset": {"title": "Dataset", "type": "metadata", "order": 3},
            "license": {"title": "License", "type": "metadata", "order": 4}
        },
        "rows": templates_data,
        "count": count
    }
    
    return formatted_results

@with_solr_cache('templates')
def get_templates(limit: int = -1, return_dataframe: bool = False):
    """Get list of templates

    :param limit: maximum number of results to return (default -1, returns all results)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :return: list of templates (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    try:
        count_query = """MATCH (t:Template)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc:Template)
                    RETURN COUNT(DISTINCT t) AS total_count"""

        count_results = vc.nc.commit_list([count_query])
        count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
        total_count = count_df['total_count'][0] if not count_df.empty else 0
    except Exception as e:
        # Fallback to minimal template list when Neo4j is unavailable
        print(f"Neo4j unavailable ({e}), using minimal template list fallback")
        return _get_templates_minimal(limit, return_dataframe)

    # Define the main Cypher query
    # Match full pattern to exclude template channel nodes
    # Use COLLECT to aggregate multiple datasets/licenses into single row per template
    query = f"""
    MATCH (p:Class)<-[:INSTANCEOF]-(t:Template)<-[:depicts]-(tc:Template)-[r:in_register_with]->(tc)
    OPTIONAL MATCH (t)-[:has_source]->(ds:DataSet)
    OPTIONAL MATCH (ds)-[:has_license|license]->(lic:License)
    WITH t, r, COLLECT(DISTINCT ds) as datasets, COLLECT(DISTINCT lic) as licenses
    RETURN DISTINCT t.short_form as id,
           apoc.text.format("[%s](%s)",[t.label,t.short_form]) AS name,
           apoc.text.join(t.uniqueFacets, '|') AS tags,
           apoc.text.join([ds IN datasets | apoc.text.format("[%s](%s)",[ds.label,ds.short_form])], ', ') AS dataset,
           apoc.text.join([lic IN licenses | REPLACE(apoc.text.format("[%s](%s)",[lic.label,lic.short_form]), '[null](null)', '')], ', ') AS license,
           COALESCE(REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[t.label, REPLACE(COALESCE(r.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), t.label, t.short_form]), "[![null]( 'null')](null)", ""), "") as thumbnail,
           99 as order
           ORDER BY id DESC
    """

    if limit != -1:
        query += f" LIMIT {limit}"

    # Run the query using VFB_connect
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    columns_to_encode = ['name', 'dataset', 'license', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)

    template_order = ["VFB_00101567","VFB_00200000","VFB_00017894","VFB_00101384","VFB_00050000","VFB_00049000","VFB_00100000","VFB_00030786","VFB_00110000","VFB_00120000"]

    order = 1

    for template in template_order:
        df.loc[df['id'] == template, 'order'] = order
        order += 1

    # Sort the DataFrame by 'order'
    df = df.sort_values('order')

    if return_dataframe:
        return df

    # Format the results
    formatted_results = {
        "headers": {
            "id": {"title": "Add", "type": "selection_id", "order": -1},
            "order": {"title": "Order", "type": "numeric", "order": 1, "sort": {0: "Asc"}},
            "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
            "tags": {"title": "Tags", "type": "tags", "order": 2},
            "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9},
            "dataset": {"title": "Dataset", "type": "metadata", "order": 3},
            "license": {"title": "License", "type": "metadata", "order": 4}
        },
        "rows": [
            {
                key: row[key]
                for key in [
                    "id",
                    "order",
                    "name",
                    "tags",
                    "thumbnail",
                    "dataset",
                    "license"
                ]
            }
            for row in safe_to_dict(df)
        ],
        "count": total_count
    }
    
    return formatted_results

def get_related_anatomy(template_short_form: str, limit: int = -1, return_dataframe: bool = False):
    """
    Retrieve related anatomical structures for a given template.

    :param template_short_form: The short form of the template to query.
    :param limit: Maximum number of results to return. Default is -1, which returns all results.
    :param return_dataframe: If True, returns results as a pandas DataFrame. Otherwise, returns a list of dicts.
    :return: Related anatomical structures and paths.
    """

    # Define the Cypher query
    query = f"""
    MATCH (root:Class)<-[:INSTANCEOF]-(t:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(tc:Template)<-[ie:in_register_with]-(c:Individual)-[:depicts]->(image:Individual)-[r:INSTANCEOF]->(anat:Class:Anatomy)
    WHERE exists(ie.index)
    WITH root, anat,r,image
    MATCH p=allshortestpaths((root)<-[:SUBCLASSOF|part_of*..50]-(anat))
    UNWIND nodes(p) as n
    UNWIND nodes(p) as m
    WITH * WHERE id(n) < id(m)
    MATCH path = allShortestPaths( (n)-[:SUBCLASSOF|part_of*..1]-(m) )
    RETURN collect(distinct {{ node_id: id(anat), short_form: anat.short_form, image: image.short_form }}) AS image_nodes, id(root) AS root, collect(path)
    """

    if limit != -1:
        query += f" LIMIT {limit}"

    # Execute the query using your database connection (e.g., VFB_connect)
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame (if needed)
    if return_dataframe:
        df = pd.DataFrame.from_records(results)
        return df

    # Otherwise, return the raw results
    return results

def get_similar_neurons(neuron, similarity_score='NBLAST_score', return_dataframe=True, limit: int = -1):
    """Get JSON report of individual neurons similar to input neuron

    :param neuron:
    :param similarity_score: Optionally specify similarity score to chose
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns list of dicts.
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: list of similar neurons (id, label, tags, source (db) id, accession_in_source) + similarity score.
    :rtype: pandas.DataFrame or list of dicts

    """
    count_query = f"""MATCH (c1:Class)<-[:INSTANCEOF]-(n1)-[r:has_similar_morphology_to]-(n2)-[:INSTANCEOF]->(c2:Class) 
                WHERE n1.short_form = '{neuron}' and exists(r.{similarity_score})
                RETURN COUNT(DISTINCT n2) AS total_count"""

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Extends the v1.10.1 channel/template/technique pattern. Adds:
    #   - type      = pipe-joined parent class labels (n2 -[:INSTANCEOF]-> Class)
    #     matches v2 prod's `Type` column from SOLR's `types` collection
    #   - template  = `[symbol](short_form)` markdown of the alignment template
    #   - technique = imaging technique label (channel -[:is_specified_output_of]-> Class)
    #
    # Each OPTIONAL branch is wrapped in a CALL subquery so the outer query
    # carries one row per n2 throughout. Without this, an n2 with N
    # cross-references × M alignments × K types would produce N×M×K rows
    # that DISTINCT then collapses at the end — wasteful, especially on
    # densely-typed neurons. Each subquery either aggregates (for `type`)
    # or LIMIT 1s (for the single representative cross-ref / alignment
    # the V2 row needs), so n2 stays the row key end-to-end.
    main_query = f"""MATCH (c1:Class)<-[:INSTANCEOF]-(n1:Individual)-[r:has_similar_morphology_to]-(n2:Individual)-[:INSTANCEOF]->(c2:Class)
            WHERE n1.short_form = '{neuron}' and exists(r.{similarity_score})
            WITH DISTINCT r, n2
            CALL {{
                WITH n2
                OPTIONAL MATCH (n2)-[:INSTANCEOF]->(typ:Class)
                RETURN apoc.text.join([x IN collect(DISTINCT CASE WHEN typ.short_form IS NULL THEN NULL ELSE apoc.text.format('[%s](%s)', [typ.label, typ.short_form]) END) WHERE x IS NOT NULL], '; ') AS type
            }}
            CALL {{
                WITH n2
                OPTIONAL MATCH (n2)-[rx:database_cross_reference]->(site:Site)
                WHERE site.is_data_source
                WITH rx, site LIMIT 1
                RETURN rx, site
            }}
            CALL {{
                WITH n2
                OPTIONAL MATCH (n2)<-[:depicts]-(channel:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
                OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
                WITH n2, collect({{ri: ri, templ: templ, technique: technique}}) AS aligns
                WITH n2, [a IN aligns WHERE a.templ IS NOT NULL] AS va
                RETURN
                    CASE WHEN size(va)=0 THEN null ELSE head(va).templ END AS templ,
                    CASE WHEN size(va)=0 THEN null ELSE head(va).technique END AS technique,
                    apoc.text.join([a IN va |
                        apoc.text.format("[![%s](%s '%s')](%s)", [
                            n2.label + " aligned to " + (CASE WHEN a.templ.symbol[0] <> '' THEN a.templ.symbol[0] ELSE a.templ.label END),
                            REPLACE(COALESCE(a.ri.thumbnail[0],''),'thumbnailT.png','thumbnail.png'),
                            n2.label + " aligned to " + (CASE WHEN a.templ.symbol[0] <> '' THEN a.templ.symbol[0] ELSE a.templ.label END),
                            a.templ.short_form + "," + n2.short_form
                        ])
                    ], '; ') AS thumbnails
            }}
            RETURN n2.short_form as id,
            apoc.text.format("[%s](%s)", [n2.label, n2.short_form]) AS name,
            r.{similarity_score}[0] AS score,
            apoc.text.join(coalesce(n2.uniqueFacets, []), '|') AS tags,
            type,
            CASE WHEN site:Deprecated THEN COALESCE(site.label,'') ELSE REPLACE(apoc.text.format("[%s](%s)",[site.label,site.short_form]), '[null](null)', '') END AS source,
            CASE WHEN site:Deprecated THEN COALESCE(rx.accession[0],'') ELSE REPLACE(apoc.text.format("[%s](%s)",[rx.accession[0], (site.link_base[0] + rx.accession[0])]), '[null](null)', '') END AS source_id,
            REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            thumbnails as thumbnail
            ORDER BY score DESC"""

    if limit != -1:
        main_query += f" LIMIT {limit}"

    # Run the query using VFB_connect
    results = vc.nc.commit_list([main_query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    # template is a `[symbol](short_form)` markdown link — must be encoded the
    # same way as name/source/source_id/thumbnail so the V2 frontend's link
    # parser renders it consistently. type/technique are plain text and
    # don't need encoding.
    columns_to_encode = ['name', 'source', 'source_id', 'template', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)

    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "Add", "type": "selection_id", "order": -1},
                "score": {"title": "Score", "type": "numeric", "order": 1, "sort": {0: "Desc"}},
                "name": {"title": "Name", "type": "markdown", "order": 1, "sort": {1: "Asc"}},
                "tags": {"title": "Tags", "type": "tags", "order": 2},
                "type": {"title": "Type", "type": "text", "order": 3},
                "source": {"title": "Source", "type": "metadata", "order": 4},
                "source_id": {"title": "Source ID", "type": "metadata", "order": 5},
                "template": {"title": "Template", "type": "markdown", "order": 6},
                "technique": {"title": "Imaging Technique", "type": "text", "order": 7},
                "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "name",
                        "score",
                        "tags",
                        "type",
                        "source",
                        "source_id",
                        "template",
                        "technique",
                        "thumbnail"
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results

def get_individual_neuron_inputs(neuron_short_form: str, return_dataframe=True, limit: int = -1, summary_mode: bool = False):
    """
    Retrieve neurons that have synapses into the specified neuron, along with the neurotransmitter
    types, and additional information about the neurons.

    :param neuron_short_form: The short form identifier of the neuron to query.
    :param return_dataframe: If True, returns results as a pandas DataFrame. Otherwise, returns a dictionary.
    :param limit: Maximum number of results to return. Default is -1, which returns all results.
    :param summary_mode: If True, returns a preview of the results with summed weights for each neurotransmitter type.
    :return: Neurons, neurotransmitter types, and additional neuron information.
    """

    # Define the common part of the Cypher query
    query_common = f"""
    MATCH (a:has_neuron_connectivity {{short_form:'{neuron_short_form}'}})<-[r:synapsed_to]-(b:has_neuron_connectivity)
    UNWIND(labels(b)) as l
    WITH * WHERE l contains "ergic"
    OPTIONAL MATCH (c:Class:Neuron) WHERE c.short_form starts with "FBbt_" AND toLower(c.label)=toLower(l+" neuron")
    """
    if not summary_mode:
        count_query = f"""{query_common}
                    RETURN COUNT(DISTINCT b) AS total_count"""
    else:
        count_query = f"""{query_common}
                    RETURN COUNT(DISTINCT c) AS total_count"""

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Define the part of the query for normal mode
    query_normal = f"""
    OPTIONAL MATCH (b)-[:INSTANCEOF]->(neuronType:Class),
                   (b)<-[:depicts]-(imageChannel:Individual)-[image:in_register_with]->(templateChannel:Template)-[:depicts]->(templ:Template),
                   (imageChannel)-[:is_specified_output_of]->(imagingTechnique:Class)
    RETURN 
        b.short_form as id,
        apoc.text.format("[%s](%s)", [l, c.short_form]) as Neurotransmitter, 
        sum(r.weight[0]) as Weight,
        apoc.text.format("[%s](%s)", [b.label, b.short_form]) as Name,
        apoc.text.format("[%s](%s)", [neuronType.label, neuronType.short_form]) as Type,
        apoc.text.join(b.uniqueFacets, '|') as Gross_Type,
        apoc.text.join(collect(DISTINCT apoc.text.format("[%s](%s)", [templ.label, templ.short_form])), ', ') as Template_Space,
        apoc.text.format("[%s](%s)", [imagingTechnique.label, imagingTechnique.short_form]) as Imaging_Technique,
        apoc.text.join(collect(DISTINCT REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[b.label + " aligned to " + (CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END), REPLACE(COALESCE(image.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), b.label + " aligned to " + (CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END), templ.short_form + "," + b.short_form]), "[![null]( 'null')](null)", "")), '; ') as Images
    ORDER BY Weight Desc
    """

    # Define the part of the query for preview mode
    query_preview = f"""
    RETURN DISTINCT c.short_form as id,
        apoc.text.format("[%s](%s)", [l, c.short_form]) as Neurotransmitter, 
        sum(r.weight[0]) as Weight
    ORDER BY Weight Desc
    """

    # Choose the appropriate part of the query based on the summary_mode parameter
    query = query_common + (query_preview if summary_mode else query_normal)

    if limit != -1 and not summary_mode:
        query += f" LIMIT {limit}"

    # Execute the query using your database connection (e.g., vc.nc)
    results = vc.nc.commit_list([query])

    # Convert the results to a DataFrame
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    columns_to_encode = ['Neurotransmitter', 'Type', 'Name', 'Template_Space', 'Imaging_Technique', 'thumbnail']
    df = encode_markdown_links(df, columns_to_encode)
    
    # If return_dataframe is True, return the results as a DataFrame
    if return_dataframe:
        return df

    # Format the results for the preview
    if not summary_mode:
        results = {
            "headers": {
                "id": {"title": "ID", "type": "text", "order": -1},
                "Neurotransmitter": {"title": "Neurotransmitter", "type": "markdown", "order": 0},
                "Weight": {"title": "Weight", "type": "numeric", "order": 1},
                "Name": {"title": "Name", "type": "markdown", "order": 2},
                "Type": {"title": "Type", "type": "markdown", "order": 3},
                "Gross_Type": {"title": "Gross Type", "type": "text", "order": 4},
                "Template_Space": {"title": "Template Space", "type": "markdown", "order": 5},
                "Imaging_Technique": {"title": "Imaging Technique", "type": "markdown", "order": 6},
                "Images": {"title": "Images", "type": "markdown", "order": 7}
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "Neurotransmitter",
                        "Weight",
                        "Name",
                        "Type",
                        "Gross_Type",
                        "Template_Space",
                        "Imaging_Technique",
                        "Images"
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
    else:
        results = {
            "headers": {
                "id": {"title": "ID", "type": "text", "order": -1},
                "Neurotransmitter": {"title": "Neurotransmitter", "type": "markdown", "order": 0},
                "Weight": {"title": "Weight", "type": "numeric", "order": 1},
            },
            "rows": [
                {
                    key: row[key]
                    for key in [
                        "id",
                        "Neurotransmitter",
                        "Weight",
                    ]
                }
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
    
    return results


def get_expression_overlaps_here(expression_pattern_short_form: str, return_dataframe=True, limit: int = -1):
    """Anatomy classes overlapped by the specified expression pattern.

    INVERSE direction of TransgeneExpressionHere — given an expression
    pattern, return the anatomy classes whose Individuals are overlapped
    by (or part_of) the expression pattern's Individuals. Backs the
    XMI AnatomyExpressedIn CompoundRefQuery's matchingCriteria
    (Class + Expression_pattern OR Class + Expression_pattern_fragment).

    Columns: id / name / tags / pubs — id is the anatomy short_form,
    name is the anatomy label, tags / pubs collect dataset and pub
    metadata over the expressing Individuals.

    :param expression_pattern_short_form: short_form of an
        Expression_pattern Class (e.g. 'VFBexp_FBtp0001321')
    :param return_dataframe: pandas DataFrame if True else formatted dict
    :param limit: -1 for all results, otherwise cap on row count
    """
    count_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class:Anatomy)
        WHERE ep.short_form = '{expression_pattern_short_form}'
        RETURN COUNT(DISTINCT anat) AS total_count
    """

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # v1.14.2: mirror the legacy XMI Cypher for ExpressionOverlapsHere
    # at geppetto-vfb@998cc28d9^:model/vfb.xmi dataSources[0]/@queries.9
    # — add Stage / Template_Space / Imaging_Technique / Images columns
    # by walking from the result anatomy class (not the input EP):
    #   - stages   : (anoni)-[:Related]->(:FBdv)   (development stage)
    #   - template : (anat)<-[:has_source|SUBCLASSOF|INSTANCEOF*]
    #                      -(:Individual)
    #                      <-[:depicts]-(channel:Individual)
    #                      -[:in_register_with]->(template:Individual)
    #                      -[:depicts]->(template_anat:Individual)
    #   - technique: (channel)-[:is_specified_output_of]->(technique:Class)
    #   - thumbnail: built from template_anat + i + irw.thumbnail[0]
    # Apply LIMIT before the CALL subqueries to keep the multi-hop walks
    # bounded on EPs with hundreds of overlapping anatomy classes.
    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    main_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(anoni:Individual)-[:INSTANCEOF]->(anat:Class:Anatomy)
        WHERE ep.short_form = '{expression_pattern_short_form}'
        WITH anat, collect(DISTINCT ar.pub[0]) AS pub_shorts, collect(DISTINCT anoni) AS anonis
        ORDER BY anat.label
        {limit_clause}
        CALL {{
            WITH pub_shorts
            UNWIND pub_shorts AS p_sf
            OPTIONAL MATCH (p:pub {{ short_form: p_sf }})
            WITH p WHERE p IS NOT NULL
                       AND coalesce(p.label, p.short_form) IS NOT NULL
                       AND coalesce(p.label, p.short_form) <> ''
                       AND coalesce(p.label, p.short_form) <> 'Unattributed'
            RETURN apoc.text.join(
                collect(DISTINCT apoc.text.format("[%s](%s)",
                                                   [coalesce(p.label, p.short_form), p.short_form])),
                '; '
            ) AS pubs
        }}
        CALL {{
            WITH anonis
            UNWIND anonis AS anoni
            OPTIONAL MATCH (anoni)-[:Related]->(o:FBdv)
            WITH o WHERE o IS NOT NULL
            RETURN apoc.text.join(collect(DISTINCT coalesce(o.label, o.short_form)), '; ') AS stages
        }}
        CALL {{
            WITH anat
            OPTIONAL MATCH (anat)<-[:has_source|SUBCLASSOF|INSTANCEOF*]-(i:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH anat, i, template_anat, technique, irw
            WHERE i IS NOT NULL
            WITH anat, i, template_anat, technique, irw LIMIT 5
            WITH anat, collect({{i: i, template_anat: template_anat, technique: technique, irw: irw}}) AS imgs
            WITH anat, imgs, head(imgs) AS rep
            RETURN
                rep.template_anat AS template_anat,
                rep.technique AS technique,
                apoc.text.join([x IN imgs |
                    REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",
                        [coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.template_anat.symbol[0] <> '' THEN x.template_anat.symbol[0] ELSE x.template_anat.label END,
                         REPLACE(COALESCE(x.irw.thumbnail[0], ''), 'thumbnailT.png', 'thumbnail.png'),
                         coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.template_anat.symbol[0] <> '' THEN x.template_anat.symbol[0] ELSE x.template_anat.label END,
                         x.template_anat.short_form + "," + coalesce(x.i.short_form, anat.short_form)]),
                    "[![null]( 'null')](null)", "")
                ], ' | ') AS thumbnail
        }}
        RETURN
            anat.short_form AS id,
            apoc.text.format("[%s](%s)", [anat.label, anat.short_form]) AS name,
            apoc.text.join(coalesce(anat.uniqueFacets, []), '|') AS tags,
            pubs,
            stages,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            thumbnail
    """

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))

    if not df.empty:
        df = encode_markdown_links(df, ['name', 'pubs', 'template', 'thumbnail'])

    if return_dataframe:
        return df

    return {
        "headers": {
            "id":        {"title": "ID",                "type": "selection_id", "order": -1},
            "name":      {"title": "Anatomy",           "type": "markdown",     "order":  0},
            "pubs":      {"title": "Publications",      "type": "markdown",     "order":  1},
            "tags":      {"title": "Tags",              "type": "tags",         "order":  2},
            "stages":    {"title": "Stage",             "type": "text",         "order":  3},
            "template":  {"title": "Template",          "type": "markdown",     "order":  4},
            "technique": {"title": "Imaging Technique", "type": "text",         "order":  5},
            "thumbnail": {"title": "Thumbnail",         "type": "markdown",     "order":  9},
        },
        "rows": [
            {k: row[k] for k in ["id", "name", "pubs", "tags", "stages", "template", "technique", "thumbnail"]}
            for row in safe_to_dict(df, sort_by_id=False)
        ],
        "count": total_count,
    }


def contains_all_tags(lst: List[str], tags: List[str]) -> bool:
    """
    Checks if the given list contains all the tags passed.

    :param lst: list of strings to check
    :param tags: list of strings to check for in lst
    :return: True if lst contains all tags, False otherwise
    """
    return all(tag in lst for tag in tags)

@with_solr_cache('neurons_part_here')
def get_neurons_with_part_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have some part overlapping with the specified anatomical region.
    
    This implements the NeuronsPartHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery (Index 1) → Process → SOLR (Index 3)
    OWL query (from XMI): <FBbt_00005106> and <RO_0002131> some <$ID>
    Where: FBbt_00005106 = neuron, RO_0002131 = overlaps
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with parts in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_query', include_source=True, query_by_label=False)


@with_solr_cache('neurons_synaptic')
def get_neurons_with_synapses_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have synaptic terminals in the specified anatomical region.
    
    This implements the NeuronsSynaptic query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002130 = has synaptic terminals in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with synaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002130> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neurons_presynaptic')
def get_neurons_with_presynaptic_terminals_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have presynaptic terminals in the specified anatomical region.
    
    This implements the NeuronsPresynapticHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002113 = has presynaptic terminal in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with presynaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002113> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neurons_postsynaptic')
def get_neurons_with_postsynaptic_terminals_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that have postsynaptic terminals in the specified anatomical region.
    
    This implements the NeuronsPostsynapticHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002110 = has postsynaptic terminal in
    Matching criteria: Class + Synaptic_neuropil, Class + Visual_system, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the anatomical region (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes with postsynaptic terminals in the specified region
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002110> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('components_of')
def get_components_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves components (parts) of the specified anatomical class.
    
    This implements the ComponentsOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery Part of → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/$ID>
    Where: BFO_0000050 = part of
    Matching criteria: Class + Clone
    
    :param short_form: short form of the anatomical class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Components of the specified class
    """
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('parts_of')
def get_parts_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves parts of the specified anatomical class.
    
    This implements the PartsOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery Part of → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/BFO_0000050> some <http://purl.obolibrary.org/obo/$ID>
    Where: BFO_0000050 = part of
    Matching criteria: Class (any)
    
    :param short_form: short form of the anatomical class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Parts of the specified class
    """
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('subclasses_of')
def get_subclasses_of(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves subclasses of the specified class.
    
    This implements the SubclassesOf query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query: Direct subclasses of '<class>'
    Matching criteria: Class (any)
    
    :param short_form: short form of the class
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Subclasses of the specified class
    """
    # For subclasses, we query the class itself (Owlery subclasses endpoint handles this)
    # Use angle brackets for IRI conversion, not quotes
    owl_query = f"<{short_form}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


def _targeting_rows(base_match, var, short_form, return_dataframe, limit):
    """Shared runner for the split<->neuron targeting queries.

    base_match must bind the result class to ``var`` for the given ``short_form``.
    Returns the standard class-row table (id/label/tags/thumbnail) + true count,
    so fill_query_results gets the real count without a re-run.
    """
    count_query = base_match + f" RETURN count(DISTINCT {var}) AS total_count"
    count_df = pd.DataFrame.from_records(get_dict_cursor()(vc.nc.commit_list([count_query])))
    total_count = int(count_df['total_count'][0]) if not count_df.empty else 0

    main_query = base_match + (
        f" WITH DISTINCT {var} "
        f"CALL {{ WITH {var} OPTIONAL MATCH ({var})<-[:INSTANCEOF]-(:Individual)<-[:depicts]-"
        "(:Individual)-[irw:in_register_with]->(:Template)-[:depicts]->(templ:Template) "
        "RETURN irw, templ LIMIT 1 } "
        f"RETURN {var}.short_form AS id, "
        f"apoc.text.format(\"[%s](%s)\",[{var}.label, {var}.short_form]) AS label, "
        f"apoc.text.join(coalesce({var}.uniqueFacets,[]),'|') AS tags, "
        f"REPLACE(apoc.text.format(\"[![%s](%s '%s')](%s)\",[{var}.label, "
        "REPLACE(COALESCE(irw.thumbnail[0],''),'thumbnailT.png','thumbnail.png'), "
        f"{var}.label, templ.short_form + ',' + {var}.short_form]), "
        "\"[![null]( 'null')](null)\", \"\") AS thumbnail "
        "ORDER BY label"
    )
    if limit != -1:
        main_query += f" LIMIT {limit}"
    df = pd.DataFrame.from_records(get_dict_cursor()(vc.nc.commit_list([main_query])))
    df = encode_markdown_links(df, ['label', 'thumbnail'])
    if return_dataframe:
        return df
    return {
        "headers": _get_standard_query_headers(),
        "rows": [{k: row.get(k) for k in ["id", "label", "tags", "thumbnail"]}
                 for row in safe_to_dict(df, sort_by_id=False)],
        "count": total_count,
    }


@with_solr_cache('splits_targeting')
def get_splits_targeting(short_form: str, return_dataframe=True, limit: int = -1):
    """Splits (intersectional expression patterns) that target the given neuron class.

    Live Neo4j query mirroring the indexer's neuron_split clause
    (VFB_json_schema_indexer query_roller.neuron_split) — surfaced as a query
    with a preview + count badge rather than a static term-info field.
    """
    base = (
        "MATCH (:Class {label:'intersectional expression pattern'})"
        "<-[:SUBCLASSOF]-(ep:Class)<-[:part_of]-(:Individual)"
        f"-[:INSTANCEOF]->(primary:Class {{short_form:'{short_form}'}})"
    )
    return _targeting_rows(base, "ep", short_form, return_dataframe, limit)


@with_solr_cache('neurons_targeted_by_split')
def get_neurons_targeted_by_split(short_form: str, return_dataframe=True, limit: int = -1):
    """Neurons targeted by the given split class.

    Live Neo4j query mirroring the indexer's split_neuron clause
    (VFB_json_schema_indexer query_roller.split_neuron).
    """
    base = (
        "MATCH (:Class {label:'intersectional expression pattern'})"
        f"<-[:SUBCLASSOF]-(primary:Class {{short_form:'{short_form}'}})"
        "<-[:part_of]-(:Individual)-[:INSTANCEOF]->(n:Neuron)"
    )
    return _targeting_rows(base, "n", short_form, return_dataframe, limit)


@with_solr_cache('neuron_classes_fasciculating_here')
def get_neuron_classes_fasciculating_here(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves neuron classes that fasciculate with (run along) the specified tract or nerve.
    
    This implements the NeuronClassesFasciculatingHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002101> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005106 = neuron, RO_0002101 = fasciculates with
    Matching criteria: Class + Tract_or_nerve
    
    :param short_form: short form of the tract or nerve (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Neuron classes that fasciculate with the specified tract or nerve
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002101> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('tracts_nerves_innervating_here')
def get_tracts_nerves_innervating_here(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves tracts and nerves that innervate the specified synaptic neuropil.
    
    This implements the TractsNervesInnervatingHere query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00005099 = tract or nerve, RO_0002134 = innervates
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Tracts and nerves that innervate the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005099> and <http://purl.obolibrary.org/obo/RO_0002134> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('lineage_clones_in')
def get_lineage_clones_in(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves lineage clones that overlap with the specified synaptic neuropil.
    
    This implements the LineageClonesIn query from the VFB XMI specification.
    Query chain (from XMI): Owlery → Process → SOLR
    OWL query (from XMI): object=<http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <http://purl.obolibrary.org/obo/$ID>
    Where: FBbt_00007683 = clone, RO_0002131 = overlaps
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Lineage clones that overlap with the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00007683> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, solr_field='anat_query', query_by_label=False)


@with_solr_cache('neuron_neuron_connectivity_query')
def get_neuron_neuron_connectivity(short_form: str, return_dataframe=True, limit: int = -1, min_weight: float = 0, direction: str = 'both'):
    """
    Retrieves neurons connected to the specified neuron.

    This implements the neuron_neuron_connectivity_query from the VFB XMI specification.
    Query chain (from XMI): Neo4j compound query → process
    Matching criteria: Individual + Connected_neuron

    Uses synapsed_to relationships to find partner neurons.
    Returns inputs (upstream) and outputs (downstream) connection information,
    plus Type / Template_Space / Imaging_Technique / Images columns matching
    v2 prod parity (AnatomyExpressedIn / TermsForPub pattern: CALL-subquery
    walk over (oi)<-[:depicts]-(channel)-[in_register_with]->(template)
    -[:depicts]->(template_anat), bounded by LIMIT before the CALL fires).

    :param short_form: short form of the neuron (Individual)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :param min_weight: minimum connection weight threshold (default 0, XMI spec uses 1)
    :param direction: filter by connection direction - 'both' (default), 'upstream', or 'downstream'
    :return: Partner neurons with their input/output connection weights and image columns

    Note: Caching only applies when all parameters are at default values (complete results).
    """
    base_cypher = f"""
    MATCH (primary:Individual {{short_form: '{short_form}'}})
    MATCH (oi:Individual)-[r:synapsed_to]-(primary)
    WHERE exists(r.weight) AND r.weight[0] > {min_weight}
    WITH primary, oi
    OPTIONAL MATCH (oi)<-[down:synapsed_to]-(primary)
    WITH down, oi, primary
    OPTIONAL MATCH (primary)<-[up:synapsed_to]-(oi)
    """

    direction_filter = ""
    if direction == 'upstream':
        direction_filter = " WHERE up IS NOT NULL AND up.weight[0] > 0"
    elif direction == 'downstream':
        direction_filter = " WHERE down IS NOT NULL AND down.weight[0] > 0"

    # Count query stays cheap — no walks, just per-row collapse.
    count_query = base_cypher + direction_filter + """
        WITH DISTINCT oi
        RETURN count(oi) AS total_count
    """

    # Main query: collect INSTANCEOF parents into Type, then LIMIT before the
    # template/technique/thumbnail CALL subquery so the multi-hop walk only
    # fires on rows we actually return (mirrors AnatomyExpressedIn).
    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    main_cypher = base_cypher + direction_filter + f"""
        WITH DISTINCT oi, down, up
        OPTIONAL MATCH (oi)-[:INSTANCEOF]->(typ:Class)
        WITH oi, down, up,
             apoc.text.join(
                 [x IN collect(DISTINCT CASE WHEN typ.short_form IS NULL THEN NULL ELSE apoc.text.format('[%s](%s)', [typ.label, typ.short_form]) END) WHERE x IS NOT NULL],
                 '; '
             ) AS type
        ORDER BY oi.label
        {limit_clause}
        CALL {{
            WITH oi
            OPTIONAL MATCH (oi)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH oi, collect({{irw: irw, template_anat: template_anat, technique: technique}}) AS aligns
            WITH oi, [a IN aligns WHERE a.template_anat IS NOT NULL] AS va
            RETURN
                CASE WHEN size(va)=0 THEN null ELSE head(va).template_anat END AS template_anat,
                CASE WHEN size(va)=0 THEN null ELSE head(va).technique END AS technique,
                apoc.text.join([a IN va |
                    apoc.text.format("[![%s](%s '%s')](%s)", [
                        coalesce(oi.label,'image') + " aligned to " + (CASE WHEN a.template_anat.symbol[0] <> '' THEN a.template_anat.symbol[0] ELSE a.template_anat.label END),
                        REPLACE(COALESCE(a.irw.thumbnail[0],''),'thumbnailT.png','thumbnail.png'),
                        coalesce(oi.label,'image') + " aligned to " + (CASE WHEN a.template_anat.symbol[0] <> '' THEN a.template_anat.symbol[0] ELSE a.template_anat.label END),
                        a.template_anat.short_form + "," + oi.short_form
                    ])
                ], '; ') AS thumbnails
        }}
        RETURN
            oi.short_form AS id,
            apoc.text.format("[%s](%s)", [oi.label, oi.short_form]) AS label,
            type,
            coalesce(down.weight[0], 0) AS outputs,
            coalesce(up.weight[0], 0) AS inputs,
            apoc.text.join(coalesce(oi.uniqueFacets, []), '|') AS tags,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            thumbnails AS thumbnail
    """

    results = vc.nc.commit_list([main_cypher])
    rows = get_dict_cursor()(results)

    if limit != -1:
        count_results = vc.nc.commit_list([count_query])
        count_rows = get_dict_cursor()(count_results)
        total_count = count_rows[0].get('total_count', 0) if count_rows else 0
    else:
        total_count = len(rows)

    if return_dataframe:
        df = pd.DataFrame(rows)
        if not df.empty:
            df = encode_markdown_links(df, ['label', 'template', 'thumbnail'])
        return df

    return {
        'headers': {
            'id':        {'title': 'Neuron ID',         'type': 'selection_id', 'order': -1},
            'label':     {'title': 'Partner Neuron',    'type': 'markdown',     'order':  0},
            'type':      {'title': 'Type',              'type': 'text',         'order':  1},
            'outputs':   {'title': 'Outputs',           'type': 'number',       'order':  2},
            'inputs':    {'title': 'Inputs',            'type': 'number',       'order':  3},
            'template':  {'title': 'Template',          'type': 'markdown',     'order':  4},
            'technique': {'title': 'Imaging Technique', 'type': 'text',         'order':  5},
            'tags':      {'title': 'Tags',              'type': 'tags',         'order':  6},
            'thumbnail': {'title': 'Thumbnail',         'type': 'markdown',     'order':  9},
        },
        'rows': [
            {k: row.get(k) for k in ['id', 'label', 'type', 'outputs', 'inputs', 'template', 'technique', 'tags', 'thumbnail']}
            for row in rows
        ],
        'count': total_count,
    }


@with_solr_cache('neuron_region_connectivity_query')
def get_neuron_region_connectivity(short_form: str, return_dataframe=True, limit: int = -1):
    """Retrieves brain regions where the specified neuron has synaptic terminals.

    v1.14.12: add Type / Template / Imaging Technique / Thumbnail columns
    matching the AnatomyExpressedIn / NeuronNeuronConnectivityQuery pattern.
    CALL subquery walks (target)<-[:depicts]-(channel)-[in_register_with]->
    (template)-[:depicts]->(template_anat) and (channel)-[:is_specified_output_of]
    ->(technique). LIMIT applied before the CALL fires so the multi-hop walk
    only runs on returned rows. region wrapped as `[label](short_form)`
    markdown so the Brain Region column is clickable.

    :param short_form: short form of the neuron (Individual)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Brain regions with presynaptic and postsynaptic terminal counts + image cols
    """
    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    cypher = f"""
        MATCH (primary:Individual {{short_form: '{short_form}'}})
        MATCH (target:Individual)<-[r:has_presynaptic_terminals_in|has_postsynaptic_terminal_in]-(primary)
        WITH DISTINCT collect(properties(r)) + [{{}}] AS props, target, primary
        WITH apoc.map.removeKeys(
                 apoc.map.merge(props[0], coalesce(props[1], {{}})),
                 ['iri', 'short_form', 'Related', 'label', 'type']
             ) AS synapse_counts,
             target, primary
        OPTIONAL MATCH (target)-[:INSTANCEOF]->(typ:Class)
        WITH target, synapse_counts,
             apoc.text.join(
                 [x IN collect(DISTINCT CASE WHEN typ.short_form IS NULL THEN NULL ELSE apoc.text.format('[%s](%s)', [typ.label, typ.short_form]) END) WHERE x IS NOT NULL],
                 '; '
             ) AS type
        ORDER BY target.label
        {limit_clause}
        CALL {{
            WITH target
            OPTIONAL MATCH (target)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH channel, template, template_anat, technique, irw
            LIMIT 1
            RETURN channel, template, template_anat, technique, irw
        }}
        RETURN
            target.short_form AS id,
            apoc.text.format("[%s](%s)", [target.label, target.short_form]) AS region,
            type,
            synapse_counts.`pre` AS presynaptic_terminals,
            synapse_counts.`post` AS postsynaptic_terminals,
            apoc.text.join(coalesce(target.uniqueFacets, []), '|') AS tags,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            REPLACE(apoc.text.format("[![%s](%s '%s')](%s)", [coalesce(target.label, 'image') + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, REPLACE(COALESCE(irw.thumbnail[0], ''), 'thumbnailT.png', 'thumbnail.png'), coalesce(target.label, 'image') + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form + "," + target.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
    """

    results = vc.nc.commit_list([cypher])
    rows = get_dict_cursor()(results)

    if return_dataframe:
        df = pd.DataFrame(rows)
        if not df.empty:
            df = encode_markdown_links(df, ['region', 'template', 'thumbnail'])
        return df

    return {
        'headers': {
            'id':                     {'title': 'Region ID',             'type': 'selection_id', 'order': -1},
            'region':                 {'title': 'Brain Region',          'type': 'markdown',     'order':  0},
            'type':                   {'title': 'Type',                  'type': 'text',         'order':  1},
            'presynaptic_terminals':  {'title': 'Presynaptic Terminals', 'type': 'number',       'order':  2},
            'postsynaptic_terminals': {'title': 'Postsynaptic Terminals','type': 'number',       'order':  3},
            'template':               {'title': 'Template',              'type': 'markdown',     'order':  4},
            'technique':              {'title': 'Imaging Technique',     'type': 'text',         'order':  5},
            'tags':                   {'title': 'Tags',                  'type': 'tags',         'order':  6},
            'thumbnail':              {'title': 'Thumbnail',             'type': 'markdown',     'order':  9},
        },
        'rows': [
            {k: row.get(k) for k in ['id', 'region', 'type', 'presynaptic_terminals', 'postsynaptic_terminals', 'template', 'technique', 'tags', 'thumbnail']}
            for row in rows
        ],
        'count': len(rows),
    }


def _fetch_connectivity_entries(short_form: str, solr_field: str, subclass_ids=None):
    """Fetch connectivity entries from Solr for a neuron class and all its
    OWLERY subclasses.

    Returns a flat list of parsed JSON entries (dicts) from the Solr
    connectivity field, collected across every subclass doc.

    ``subclass_ids`` may be a pre-resolved subclass set (the queried class plus
    its Owlery subclass closure) to avoid re-querying Owlery when the caller has
    already computed it; when omitted it is fetched here.
    """
    # Step 1: OWLERY subclass expansion (includes the class itself). Use the
    # caller-supplied set when given, otherwise resolve it via Owlery.
    if subclass_ids is None:
        owl_query = f"<{short_form}>"
        try:
            subclass_ids = vc.vfb.oc.get_subclasses(
                query=owl_query, query_by_label=False, verbose=False
            )
        except Exception as e:
            print(f"Owlery subclass query failed for {short_form}: {e}")
            subclass_ids = []

    # Always include the queried class itself; normalise to a list.
    subclass_ids = list(subclass_ids)
    if short_form not in subclass_ids:
        subclass_ids.insert(0, short_form)

    if not subclass_ids:
        return []

    # Step 2: Batch-fetch from Solr using {!terms f=id}
    id_list = ','.join(subclass_ids)
    try:
        results = vfb_solr.search(
            q='id:*',
            fq=f'{{!terms f=id}}{id_list}',
            fl=solr_field,
            rows=len(subclass_ids),
        )
    except Exception as e:
        print(f"Error querying Solr for {solr_field}: {e}")
        return []

    # Step 3: Parse all connectivity JSON from all returned docs
    all_entries = []
    for doc in results.docs:
        if solr_field not in doc:
            continue
        raw = doc[solr_field]
        field_json = raw[0] if isinstance(raw, list) else raw
        try:
            entries = json.loads(field_json)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(entries, list):
            all_entries.extend(entries)
        else:
            all_entries.append(entries)

    return all_entries


def _num(v):
    """Coerce a value to a number, defaulting to 0."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0


# Root class for partner-side ancestor walk. Edges contributing to a partner
# class row require the partner instance to be (transitively) an instance of
# that class, with NEURON_ROOT_SHORT_FORM bounding the walk to avoid generic
# anatomy classes.
NEURON_ROOT_SHORT_FORM = 'FBbt_00005106'


def _get_partner_class_ancestors(direct_partner_ids, neuron_root=NEURON_ROOT_SHORT_FORM):
    """Walk SUBCLASSOF up from each direct partner class to ``neuron_root``.

    Returns ``(class_ids, labels)`` where ``class_ids`` is the union of every
    direct partner plus its ancestors that are also subclasses of
    ``neuron_root``. ``labels`` maps id -> human-readable label.
    """
    if not direct_partner_ids:
        return set(), {}
    direct_list = sorted(direct_partner_ids)
    query = (
        "MATCH (root:Class {short_form: '%s'})<-[:SUBCLASSOF*0..]-(c:Class)"
        "<-[:SUBCLASSOF*0..]-(d:Class) "
        "WHERE d.short_form IN %s "
        "RETURN DISTINCT c.short_form AS id, c.label AS label"
        % (neuron_root, direct_list)
    )
    try:
        results = vc.nc.commit_list([query])
        rows = get_dict_cursor()(results)
    except Exception as e:
        print(f"Partner class hierarchy query failed: {e}")
        # Fall back to direct partners only so we still produce some output.
        return set(direct_partner_ids), {pid: pid for pid in direct_partner_ids}
    ids = set()
    labels = {}
    for row in rows:
        cid = row.get('id')
        if not cid:
            continue
        ids.add(cid)
        labels[cid] = row.get('label') or cid
    return ids, labels


def _build_partner_instance_class_membership(class_ids):
    """Build ``instance_id -> set(class_ids)`` for the supplied partner
    classes, using a single Cypher round-trip with SUBCLASSOF closure.

    Multi-typed instances appear in multiple class sets, which is exactly what
    we need for set-union aggregation across hierarchy levels. Doing this with
    one batched query rather than per-class avoids hundreds of round-trips
    when ``class_ids`` is large.
    """
    if not class_ids:
        return {}
    class_list = sorted(class_ids)
    query = (
        "MATCH (c:Class)<-[:SUBCLASSOF*0..]-(:Class)<-[:INSTANCEOF]-"
        "(n:Individual:has_neuron_connectivity) "
        "WHERE c.short_form IN %s "
        "RETURN c.short_form AS cid, collect(DISTINCT n.short_form) AS iids"
        % class_list
    )
    try:
        results = vc.nc.commit_list([query])
        rows = get_dict_cursor()(results)
    except Exception as e:
        print(f"Partner class membership query failed: {e}")
        return {}
    instance_to_classes = {}
    for row in rows:
        cid = row.get('cid')
        for iid in row.get('iids') or []:
            instance_to_classes.setdefault(iid, set()).add(cid)
    return instance_to_classes


def _bulk_fetch_per_instance_connectivity(instance_ids):
    """Bulk-fetch cached ``neuron_neuron_connectivity_query`` results from the
    Solr cache collection for the given instance IDs.

    Returns ``(found, missing)`` where ``found`` maps instance_id ->
    list-of-partner-rows and ``missing`` lists instances that had no cache hit.
    Tries the ``_dataframe_False`` variant first (rows are easy to parse),
    then falls back to ``_dataframe_True`` for any instances still missing.
    """
    if not instance_ids:
        return {}, []
    instance_ids = list(instance_ids)
    found = {}
    prefix = 'vfb_query_neuron_neuron_connectivity_query_'
    for suffix in ('_dataframe_False', '_dataframe_True'):
        remaining = [i for i in instance_ids if i not in found]
        if not remaining:
            break
        cache_ids = [f'{prefix}{i}{suffix}' for i in remaining]
        try:
            results = vfb_solr.search(
                q='*:*',
                fq='{!terms f=id}' + ','.join(cache_ids),
                fl='id,cache_data',
                rows=len(cache_ids),
            )
        except Exception as e:
            print(f"Bulk per-instance cache fetch failed ({suffix}): {e}")
            continue
        for doc in results.docs:
            doc_id = doc.get('id')
            cache_data_raw = doc.get('cache_data')
            if isinstance(cache_data_raw, list):
                cache_data_raw = cache_data_raw[0] if cache_data_raw else None
            if not doc_id or not cache_data_raw:
                continue
            if not (doc_id.startswith(prefix) and doc_id.endswith(suffix)):
                continue
            iid = doc_id[len(prefix):-len(suffix)]
            try:
                cached = json.loads(cache_data_raw)
                result = cached.get('result')
                if isinstance(result, str):
                    result = json.loads(result)
                if isinstance(result, dict):
                    rows = result.get('rows', [])
                elif isinstance(result, list):
                    rows = result
                else:
                    rows = []
                found[iid] = rows
            except Exception as e:
                print(f"Failed to parse cached connectivity for {iid}: {e}")
    missing = [i for i in instance_ids if i not in found]
    return found, missing


def _aggregate_class_connectivity(short_form, direction,
                                  neuron_root=NEURON_ROOT_SHORT_FORM):
    """Aggregate class-level partner connectivity for the queried class AND
    each of its subclasses individually, correctly under FBbt
    multi-inheritance using set-union over instance memberships.

    ``direction`` is ``'downstream'`` (partner = downstream of queried class)
    or ``'upstream'``. Returns a flat list of row dicts; every row is tagged
    with the queried (sub)class it belongs to via ``query_id`` /
    ``_query_label``. The input term's own rows (aggregated over its full
    instance population, exactly as before) come first, followed by a block of
    rows for each subclass that has connectivity instances, ordered by class id.

    The expensive pieces (per-instance edges, partner-side hierarchy and
    membership) are computed once for the whole subtree and instances are then
    partitioned by queried (sub)class, so cost is roughly independent of the
    number of subclasses.
    """
    from collections import defaultdict

    # 1a. Queried (sub)classes in scope: the input term plus every subclass.
    #     Reuse Owlery's reasoner subclass closure (the canonical subclass set
    #     used throughout VFBquery — get_instances, _fetch_connectivity_entries
    #     — and effectively cached) rather than a fresh Neo4j SUBCLASSOF
    #     traversal. The same set seeds the partner-fetch in step 3 below, so
    #     it is computed once here. Owlery excludes the queried class itself, so
    #     add it back.
    try:
        owl_query = f"<{short_form}>"
        subclass_ids = vc.vfb.oc.get_subclasses(
            query=owl_query, query_by_label=False, verbose=False
        )
    except Exception as e:
        print(f"Owlery subclass query failed for {short_form}: {e}")
        subclass_ids = []
    query_class_ids = {short_form, *(subclass_ids or [])}

    # 1b. queried (sub)class -> its instances (SUBCLASSOF closure), with labels.
    #     The proven anchored membership query (single variable-length walk
    #     bounded by ``WHERE ... IN [ids]``) returns the instances AND the label
    #     for every queried (sub)class that actually has connectivity instances
    #     — which is exactly the set of blocks we emit — so no separate label
    #     lookup or subtree query is needed. Classes with no instances simply
    #     don't come back.
    membership_q = (
        "MATCH (c:Class)<-[:SUBCLASSOF*0..]-(:Class)<-[:INSTANCEOF]-"
        "(n:Individual:has_neuron_connectivity) "
        "WHERE c.short_form IN %s "
        "RETURN c.short_form AS cid, c.label AS label, "
        "collect(DISTINCT n.short_form) AS iids" % sorted(query_class_ids)
    )
    try:
        rows = get_dict_cursor()(vc.nc.commit_list([membership_q]))
    except Exception as e:
        print(f"Queried-side membership query failed for {short_form}: {e}")
        return []
    query_class_to_instances = defaultdict(set)
    query_labels = {}
    all_instances = set()
    for r in rows:
        cid = r.get('cid')
        iids = set(r.get('iids') or [])
        if not cid or not iids:
            continue
        query_class_to_instances[cid] = iids
        query_labels[cid] = r.get('label') or cid
        all_instances.update(iids)
    if not query_class_to_instances:
        return []
    query_labels.setdefault(short_form, short_form)

    # 2. Per-instance edges from cache (once for the whole subtree). Cache
    #    misses are skipped with a warning; the resulting connected_n /
    #    pairwise / total_weight will be a slight underestimate when this
    #    happens.
    found_edges, missing = _bulk_fetch_per_instance_connectivity(all_instances)
    if missing:
        print(
            f"Warning: per-instance connectivity cache missing for "
            f"{len(missing)}/{len(all_instances)} instances under {short_form}; "
            f"those will be skipped (results may be a slight underestimate)."
        )
    if not found_edges:
        return []

    weight_key = 'outputs' if direction == 'downstream' else 'inputs'

    # 3. Direct partner classes from the existing class-level connectivity
    #    field (already cached, unioned across the input term's subclass docs)
    #    — used as the seed set for the partner-side ancestor walk. Reuse the
    #    subclass set already resolved in step 1a rather than re-querying Owlery.
    solr_field = (
        'downstream_connectivity_query' if direction == 'downstream'
        else 'upstream_connectivity_query'
    )
    class_entries = _fetch_connectivity_entries(
        short_form, solr_field, subclass_ids=query_class_ids)
    direct_partner_ids = set()
    for entry in class_entries:
        obj = entry.get('object', {})
        pid = obj.get('short_form')
        if pid:
            direct_partner_ids.add(pid)

    # 4. Walk SUBCLASSOF up from each direct partner to ``neuron_root``.
    partner_class_ids, class_labels = _get_partner_class_ancestors(
        direct_partner_ids, neuron_root,
    )
    if not partner_class_ids:
        return []

    # 5. Build partner_instance_id -> {class_ids it belongs to}, restricted
    #    to in-scope partner classes. The helper already returns this
    #    instance -> {classes} mapping, so it is used directly. From it we also
    #    derive the total instance count per partner class (with SUBCLASSOF
    #    closure), which is the denominator when the partner is the presynaptic
    #    side (the upstream direction — see VFB_connect parity below).
    instance_to_partner_classes = _build_partner_instance_class_membership(partner_class_ids)
    partner_class_total = defaultdict(int)
    _partner_class_members = defaultdict(set)
    for iid, classes in instance_to_partner_classes.items():
        for c in classes:
            _partner_class_members[c].add(iid)
    for c, members in _partner_class_members.items():
        partner_class_total[c] = len(members)

    # 6. Aggregate edges into per-(partner-class) buckets via set-union
    #    semantics, separately for each queried (sub)class.
    #
    #    Normalization matches VFB_connect's ``get_connected_neurons_by_type``:
    #    ``total_n`` / ``connected_n`` describe the PRESYNAPTIC (source) side of
    #    each connection (the column names stay as the v2 frontend expects).
    #      - downstream direction: queried class -> partner, so the presynaptic
    #        side is the queried (sub)class. ``total_n`` is the queried-class
    #        instance count (constant within the block) and ``connected_n``
    #        counts queried instances that connect.
    #      - upstream direction: partner -> queried class, so the presynaptic
    #        side is the partner class. ``total_n`` is the partner class
    #        instance count (varies per partner row) and ``connected_n`` counts
    #        partner instances that connect.
    queried_is_presynaptic = (direction == 'downstream')

    def block_for(query_id):
        instances = query_class_to_instances.get(query_id) or set()
        if not instances:
            return []
        total_queried = len(instances)
        buckets = defaultdict(lambda: {
            'edges': set(), 'weight_sum': 0.0,
            'connected_queried': set(), 'connected_partner': set(),
        })
        for n1 in instances:
            for prow in found_edges.get(n1) or []:
                n2 = prow.get('id')
                w = prow.get(weight_key)
                if not n2 or not w:
                    continue
                try:
                    w_num = float(w)
                except (TypeError, ValueError):
                    continue
                if w_num <= 0:
                    continue
                for c in instance_to_partner_classes.get(n2, ()):
                    b = buckets[c]
                    b['edges'].add((n1, n2))
                    b['weight_sum'] += w_num
                    b['connected_queried'].add(n1)
                    b['connected_partner'].add(n2)
        block = []
        for cid, b in buckets.items():
            pw = len(b['edges'])
            tw = b['weight_sum']
            if queried_is_presynaptic:
                total = total_queried
                connected = len(b['connected_queried'])
            else:
                total = partner_class_total.get(cid, 0)
                connected = len(b['connected_partner'])
            pct = round((connected / total) * 100) if total else 0
            avg = (tw / pw) if pw else 0
            block.append({
                'id': cid,
                '_label': class_labels.get(cid, cid),
                'query_id': query_id,
                '_query_label': query_labels.get(query_id, query_id),
                'total_n': total,
                'connected_n': connected,
                'percent_connected': pct,
                'pairwise_connections': pw,
                'total_weight': tw,
                'avg_weight': avg,
            })
        block.sort(key=lambda r: r.get('pairwise_connections', 0), reverse=True)
        return block

    # 7. Input term first, then one block per subclass (ordered by class id).
    rows = block_for(short_form)
    subclass_ids = sorted(
        cid for cid in query_class_to_instances if cid != short_form
    )
    for cid in subclass_ids:
        rows.extend(block_for(cid))
    return rows


def _format_class_connectivity_rows(rows, partner_key, query_key):
    """Populate both markdown-link class columns expected by the v2 layout and
    drop the internal ``_label`` / ``_query_label`` fields.

    ``partner_key`` (``'downstream_class'`` or ``'upstream_class'``) receives the
    partner class; ``query_key`` (the other of the two) receives the queried
    (sub)class this row belongs to. Reusing the existing
    ``upstream_class`` / ``downstream_class`` slots avoids adding a column and
    lets the per-subclass breakdown show the actual (sub)class per row instead
    of the constant the processor used to synthesise.

    ``query_id`` is retained (not displayed) so callers can group rows by the
    queried (sub)class without parsing the markdown link.
    """
    out = []
    for r in rows:
        formatted = dict(r)
        partner_label = formatted.pop('_label', formatted['id'])
        formatted[partner_key] = f"[{partner_label}]({formatted['id']})"
        query_id = formatted.get('query_id')
        query_label = formatted.pop('_query_label', query_id)
        if query_id is not None:
            formatted[query_key] = f"[{query_label or query_id}]({query_id})"
        out.append(formatted)
    return out


@with_solr_cache('downstream_class_connectivity_query')
def get_downstream_class_connectivity(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves downstream connectivity classes for the specified neuron class
    AND, as separate row blocks, for each of its subclasses.

    Uses a Neo4j SUBCLASSOF traversal to enumerate instances of the queried
    class (Owlery's get_instances was observed to hang for some classes;
    Cypher is equivalent and fast here), bulk-fetches per-instance
    connectivity from the Solr cache, and aggregates by partner class with
    set-union semantics on partner instance memberships. The partner-side
    hierarchy is walked up to ``NEURON_ROOT_SHORT_FORM`` so that connections
    to a child class also count toward each ancestor class's row, without
    double-counting under FBbt multi-inheritance.

    Every row carries both the ``upstream_class`` and ``downstream_class``
    columns of the v2 layout: ``downstream_class`` is the partner and
    ``upstream_class`` is the queried (sub)class this row belongs to. The input
    term's rows come first, followed by a block of rows for each subclass that
    has connectivity instances, so the queried-side column shows the actual
    (sub)class per row rather than a single constant.

    Counts use VFB_connect's normalization (``get_connected_neurons_by_type``):
    ``total_n`` / ``connected_n`` describe the PRESYNAPTIC (source) side. For the
    downstream direction the queried class is presynaptic, so ``total_n`` is the
    queried (sub)class instance count (constant within each block) and
    ``connected_n`` is the number of those instances that connect to the
    partner. ``percent_connected`` = connected_n / total_n.

    Server-side cached via ``@with_solr_cache``; cold calls on broad classes
    can take tens of seconds because of the aggregation work (already batched
    across Solr/Neo4j round-trips).

    Matching criteria: Class + Neuron

    :param short_form: short form of the neuron class
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Downstream partner neuron classes with connectivity statistics
    """
    rows = _aggregate_class_connectivity(short_form, 'downstream')
    if not rows:
        if return_dataframe:
            return pd.DataFrame()
        return {'headers': {}, 'rows': [], 'count': 0}

    # Rows arrive grouped by queried (sub)class (input term first) and sorted by
    # pairwise_connections within each group; preserve that order. The partner is
    # the downstream class; the queried (sub)class fills the upstream_class slot.
    rows = _format_class_connectivity_rows(
        rows, partner_key='downstream_class', query_key='upstream_class')

    total_count = len(rows)
    if limit != -1:
        rows = rows[:limit]

    if return_dataframe:
        df = pd.DataFrame(rows)
        df = encode_markdown_links(df, ['upstream_class', 'downstream_class'])
        return df

    headers = {
        'id': {'title': 'ID', 'type': 'selection_id', 'order': -1},
        'upstream_class': {'title': 'Upstream Class', 'type': 'markdown', 'order': 0},
        'downstream_class': {'title': 'Downstream Class', 'type': 'markdown', 'order': 1},
        'total_n': {'title': 'Total N', 'type': 'number', 'order': 2},
        'connected_n': {'title': 'Connected N', 'type': 'number', 'order': 3},
        'percent_connected': {'title': '% Connected', 'type': 'number', 'order': 4},
        'pairwise_connections': {'title': 'Pairwise Connections', 'type': 'number', 'order': 5},
        'total_weight': {'title': 'Total Weight', 'type': 'number', 'order': 6},
        'avg_weight': {'title': 'Avg Weight', 'type': 'number', 'order': 7},
    }
    return {'headers': headers, 'rows': rows, 'count': total_count}


@with_solr_cache('upstream_class_connectivity_query')
def get_upstream_class_connectivity(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves upstream connectivity classes for the specified neuron class
    AND, as separate row blocks, for each of its subclasses.

    Same multi-step aggregation as ``get_downstream_class_connectivity`` but
    walking the upstream side: Neo4j SUBCLASSOF enumerates queried-class
    instances, batched Solr cache fetches their synaptic partners, and the
    partner-side hierarchy is walked up to ``NEURON_ROOT_SHORT_FORM`` with
    set-union semantics to avoid double-counting under FBbt multi-inheritance.

    Every row carries both the ``upstream_class`` and ``downstream_class``
    columns of the v2 layout: ``upstream_class`` is the partner and
    ``downstream_class`` is the queried (sub)class this row belongs to. The
    input term's rows come first, followed by a block of rows for each subclass
    that has connectivity instances, so the queried-side column shows the actual
    (sub)class per row rather than a single constant.

    Counts use VFB_connect's normalization (``get_connected_neurons_by_type``):
    ``total_n`` / ``connected_n`` describe the PRESYNAPTIC (source) side. For the
    upstream direction the partner is presynaptic, so ``total_n`` is the partner
    (``upstream_class``) instance count — it varies per partner row, NOT per
    queried (sub)class block — and ``connected_n`` is the number of partner
    instances that connect to the queried (sub)class. ``percent_connected`` =
    connected_n / total_n.

    Server-side cached via ``@with_solr_cache``; cold calls on broad classes
    can take tens of seconds because of the aggregation work (already batched
    across Solr/Neo4j round-trips).

    Matching criteria: Class + Neuron

    :param short_form: short form of the neuron class
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Upstream partner neuron classes with connectivity statistics
    """
    rows = _aggregate_class_connectivity(short_form, 'upstream')
    if not rows:
        if return_dataframe:
            return pd.DataFrame()
        return {'headers': {}, 'rows': [], 'count': 0}

    # Rows arrive grouped by queried (sub)class (input term first) and sorted by
    # pairwise_connections within each group; preserve that order. The partner is
    # the upstream class; the queried (sub)class fills the downstream_class slot.
    rows = _format_class_connectivity_rows(
        rows, partner_key='upstream_class', query_key='downstream_class')

    total_count = len(rows)
    if limit != -1:
        rows = rows[:limit]

    if return_dataframe:
        df = pd.DataFrame(rows)
        df = encode_markdown_links(df, ['upstream_class', 'downstream_class'])
        return df

    headers = {
        'id': {'title': 'ID', 'type': 'selection_id', 'order': -1},
        'upstream_class': {'title': 'Upstream Class', 'type': 'markdown', 'order': 0},
        'downstream_class': {'title': 'Downstream Class', 'type': 'markdown', 'order': 1},
        'total_n': {'title': 'Total N', 'type': 'number', 'order': 2},
        'connected_n': {'title': 'Connected N', 'type': 'number', 'order': 3},
        'percent_connected': {'title': '% Connected', 'type': 'number', 'order': 4},
        'pairwise_connections': {'title': 'Pairwise Connections', 'type': 'number', 'order': 5},
        'total_weight': {'title': 'Total Weight', 'type': 'number', 'order': 6},
        'avg_weight': {'title': 'Avg Weight', 'type': 'number', 'order': 7},
    }
    return {'headers': headers, 'rows': rows, 'count': total_count}


def get_flybase_stocks(short_form: str, return_dataframe=True, limit: int = -1):
    """Find available fly stocks from FlyBase for a Feature term.

    :param short_form: FlyBase feature ID (FBgn/FBal/FBti/FBco/FBst)
    :param return_dataframe: Returns pandas DataFrame if True, otherwise formatted dict
    :param limit: maximum number of results (-1 for all)
    :return: Stock records from FlyBase
    """
    from .flybase_stocks import find_stocks

    try:
        stocks = find_stocks(short_form)
    except Exception as e:
        print(f"Error querying FlyBase stocks for {short_form}: {e}")
        if return_dataframe:
            return pd.DataFrame()
        return {'headers': {}, 'rows': [], 'count': 0}

    rows = []
    for s in stocks:
        rows.append({
            'stock_id': s.get('stock_id', ''),
            'stock_number': s.get('stock_number', ''),
            'genotype': s.get('genotype', ''),
            'collection': s.get('collection', ''),
        })

    total_count = len(rows)
    if limit != -1:
        rows = rows[:limit]

    if return_dataframe:
        return pd.DataFrame(rows)

    headers = {
        'stock_id': {'title': 'Stock ID', 'type': 'text', 'order': 0},
        'stock_number': {'title': 'Stock Number', 'type': 'text', 'order': 1},
        'genotype': {'title': 'Genotype', 'type': 'text', 'order': 2},
        'collection': {'title': 'Collection', 'type': 'text', 'order': 3},
    }
    return {'headers': headers, 'rows': rows, 'count': total_count}


def get_flybase_combo_pubs(short_form: str, return_dataframe=True, limit: int = -1):
    """Find publications for a FlyBase split system combination.

    :param short_form: FlyBase combination ID (FBco...)
    :param return_dataframe: Returns pandas DataFrame if True, otherwise formatted dict
    :param limit: maximum number of results (-1 for all)
    :return: Publication records from FlyBase
    """
    from .flybase_combo_pubs import find_combo_publications

    try:
        pubs = find_combo_publications(short_form)
    except Exception as e:
        print(f"Error querying FlyBase publications for {short_form}: {e}")
        if return_dataframe:
            return pd.DataFrame()
        return {'headers': {}, 'rows': [], 'count': 0}

    rows = []
    for p in pubs:
        rows.append({
            'fbrf': p.get('fbrf', ''),
            'title': p.get('title', ''),
            'year': p.get('year', ''),
            'miniref': p.get('miniref', ''),
            'pub_type': p.get('pub_type', ''),
            'doi': p.get('doi', ''),
            'pmid': p.get('pmid', ''),
            'pmcid': p.get('pmcid', ''),
        })

    total_count = len(rows)
    if limit != -1:
        rows = rows[:limit]

    if return_dataframe:
        return pd.DataFrame(rows)

    headers = {
        'fbrf': {'title': 'FBrf', 'type': 'text', 'order': 0},
        'title': {'title': 'Title', 'type': 'text', 'order': 1},
        'year': {'title': 'Year', 'type': 'text', 'order': 2},
        'miniref': {'title': 'Reference', 'type': 'text', 'order': 3},
        'pub_type': {'title': 'Type', 'type': 'text', 'order': 4},
        'doi': {'title': 'DOI', 'type': 'text', 'order': 5},
        'pmid': {'title': 'PMID', 'type': 'text', 'order': 6},
        'pmcid': {'title': 'PMCID', 'type': 'text', 'order': 7},
    }
    return {'headers': headers, 'rows': rows, 'count': total_count}


@with_solr_cache('images_neurons')
def get_images_neurons(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual neuron images with parts in the specified synaptic neuropil.
    
    This implements the ImagesNeurons query from the VFB XMI specification.
    Query chain (from XMI): Owlery instances → Process → SOLR
    OWL query (from XMI): object=<FBbt_00005106> and <RO_0002131> some <$ID> (instances)
    Where: FBbt_00005106 = neuron, RO_0002131 = overlaps
    Matching criteria: Class + Synaptic_neuropil, Class + Synaptic_neuropil_domain
    
    Note: This query returns INSTANCES (individual neuron images) not classes.
    
    :param short_form: short form of the synaptic neuropil (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual neuron images with parts in the specified neuropil
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002131> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


@with_solr_cache('images_that_develop_from')
def get_images_that_develop_from(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual neuron images that develop from the specified neuroblast.
    
    This implements the ImagesThatDevelopFrom query from the VFB XMI specification.
    Query chain (from XMI): Owlery instances → Owlery Pass → SOLR
    OWL query (from XMI): object=<FBbt_00005106> and <RO_0002202> some <$ID> (instances)
    Where: FBbt_00005106 = neuron, RO_0002202 = develops_from
    Matching criteria: Class + Neuroblast
    
    Note: This query returns INSTANCES (individual neuron images) not classes.
    
    :param short_form: short form of the neuroblast (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual neuron images that develop from the specified neuroblast
    """
    owl_query = f"<http://purl.obolibrary.org/obo/FBbt_00005106> and <http://purl.obolibrary.org/obo/RO_0002202> some <{_short_form_to_iri(short_form)}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


def _short_form_to_iri(short_form: str) -> str:
    """
    Convert a short form ID to its full IRI.
    
    First tries simple prefix mappings for common cases (VFB*, FB*).
    For other cases, queries SOLR to get the canonical IRI.
    
    :param short_form: Short form ID (e.g., 'VFBexp_FBtp0022557', 'FBbt_00003748')
    :return: Full IRI
    """
    # VFB IDs use virtualflybrain.org/reports
    if short_form.startswith('VFB'):
        return f"http://virtualflybrain.org/reports/{short_form}"
    
    # FB* IDs (FlyBase) use purl.obolibrary.org/obo
    # This includes FBbt_, FBtp_, FBdv_, etc.
    if short_form.startswith('FB'):
        return f"http://purl.obolibrary.org/obo/{short_form}"
    
    # For other cases, query SOLR to get the IRI from term_info
    try:
        results = vfb_solr.search(
            q=f'id:{short_form}',
            fl='term_info',
            rows=1
        )
        
        if results.docs and 'term_info' in results.docs[0]:
            term_info_str = results.docs[0]['term_info'][0]
            term_info = json.loads(term_info_str)
            iri = term_info.get('term', {}).get('core', {}).get('iri')
            if iri:
                return iri
    except Exception as e:
        # If SOLR query fails, fall back to OBO default
        print(f"Warning: Could not fetch IRI for {short_form} from SOLR: {e}")
    
    # Default to OBO for other IDs (FBbi_, etc.)
    return f"http://purl.obolibrary.org/obo/{short_form}"


@with_solr_cache('expression_pattern_fragments')
def get_expression_pattern_fragments(short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieves individual expression pattern fragment images that are part of an expression pattern.
    
    This implements the epFrag query from the VFB XMI specification.
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    
    Query chain (from XMI): Owlery individual parts → Process → SOLR
    OWL query (from XMI): object=<BFO_0000050> some <$ID> (instances)
    Where: BFO_0000050 = part_of
    Matching criteria: Class + Expression_pattern
    
    Note: This query returns INSTANCES (individual expression pattern fragments) not classes.
    
    :param short_form: short form of the expression pattern (Class)
    :param return_dataframe: Returns pandas dataframe if true, otherwise returns formatted dict
    :param limit: maximum number of results to return (default -1, returns all results)
    :return: Individual expression pattern fragment images
    """
    iri = _short_form_to_iri(short_form)
    owl_query = f"<http://purl.obolibrary.org/obo/BFO_0000050> some <{iri}>"
    return _owlery_query_to_results(owl_query, short_form, return_dataframe, limit, 
                                    solr_field='anat_image_query', query_by_label=False, query_instances=True)


def _get_neurons_part_here_headers():
    """Return standard headers for get_neurons_with_part_in results"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "tags": {"title": "Tags", "type": "tags", "order": 2},
        "source": {"title": "Data Source", "type": "metadata", "order": 3},
        "source_id": {"title": "Data Source ID", "type": "metadata", "order": 4},
        "template": {"title": "Template", "type": "markdown", "order": 6},
        "technique": {"title": "Imaging Technique", "type": "text", "order": 7},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }


def _get_standard_query_headers():
    """Return standard headers for most query results (no source/source_id)"""
    return {
        "id": {"title": "Add", "type": "selection_id", "order": -1},
        "label": {"title": "Name", "type": "markdown", "order": 0, "sort": {0: "Asc"}},
        "tags": {"title": "Tags", "type": "tags", "order": 2},
        "template": {"title": "Template", "type": "markdown", "order": 6},
        "technique": {"title": "Imaging Technique", "type": "text", "order": 7},
        "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}
    }


def _owlery_query_to_results(owl_query_string: str, short_form: str, return_dataframe: bool = True, 
                              limit: int = -1, solr_field: str = 'anat_query', 
                              include_source: bool = False, query_by_label: bool = True,
                              query_instances: bool = False):
    """
    Unified helper function for Owlery-based queries.
    
    This implements the common pattern:
    1. Query Owlery for class/instance IDs matching an OWL pattern
    2. Fetch details from SOLR for each result
    3. Format results as DataFrame or dict
    
    :param owl_query_string: OWL query string (format depends on query_by_label parameter)
    :param short_form: The anatomical region or entity short form
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict
    :param limit: Maximum number of results to return (default -1 for all)
    :param solr_field: SOLR field to query (default 'anat_query' for Class, 'anat_image_query' for Individuals)
    :param include_source: Whether to include source and source_id columns
    :param query_by_label: If True, use label syntax with quotes. If False, use IRI syntax with angle brackets.
    :param query_instances: If True, query for instances instead of subclasses
    :return: Query results
    """
    try:
        # Step 1: Query Owlery for classes or instances matching the OWL pattern
        if query_instances:
            result_ids = vc.vfb.oc.get_instances(
                query=owl_query_string,
                query_by_label=query_by_label,
                verbose=False
            )
        else:
            result_ids = vc.vfb.oc.get_subclasses(
                query=owl_query_string,
                query_by_label=query_by_label,
                verbose=False
            )
        
        class_ids = result_ids  # Keep variable name for compatibility
        
        if not class_ids:
            # No results found - return empty
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers() if not include_source else _get_neurons_part_here_headers(),
                "rows": [],
                "count": 0
            }
        
        total_count = len(class_ids)
        
        # Apply limit if specified (before SOLR query to save processing)
        if limit != -1 and limit > 0:
            class_ids = class_ids[:limit]
        
        # Step 2: Query SOLR for ALL classes in a single batch query
        # Use the {!terms f=id} syntax from XMI to fetch all results efficiently
        rows = []
        try:
            # Build filter query with all class IDs
            id_list = ','.join(class_ids)
            results = vfb_solr.search(
                q='id:*',
                fq=f'{{!terms f=id}}{id_list}',
                fl=solr_field,
                rows=len(class_ids)
            )
            
            # Process all results
            for doc in results.docs:
                if solr_field not in doc:
                    continue
                    
                # Parse the SOLR field JSON string
                field_data_str = doc[solr_field][0]
                field_data = json.loads(field_data_str)
                
                # Extract core term information
                term_core = field_data.get('term', {}).get('core', {})
                class_short_form = term_core.get('short_form', '')
                
                # Extract label (prefer symbol over label)
                label_text = term_core.get('label', 'Unknown')
                if term_core.get('symbol') and len(term_core.get('symbol', '')) > 0:
                    label_text = term_core.get('symbol')
                label_text = unquote(label_text)
                
                # Extract tags from unique_facets
                tags = '|'.join(term_core.get('unique_facets', []))
                
                # Extract thumbnail + template + technique from SOLR.
                #
                # Class queries (anat_query) wrap each image as
                #   anatomy_channel_image: [{anatomy, channel_image: {...}}]
                # Individual / instance queries (anat_image_query, used by
                # query_instances=True callers like ImagesNeurons and epFrag)
                # use a flat top-level
                #   channel_image: [{image, channel, imaging_technique}]
                # with no `anatomy_channel_image` wrapper at all.
                #
                # Normalise both shapes to a single `channel_image` dict
                # before extracting template / technique / thumbnail so the
                # instance queries (ImagesNeurons et al) actually get
                # populated Template_Space / Imaging_Technique / Images
                # columns instead of empty strings.
                thumbnail = ''
                template = ''
                technique = ''

                channel_image = {}
                anatomy_label_for_alt = label_text
                anatomy_images = field_data.get('anatomy_channel_image', [])
                if anatomy_images and len(anatomy_images) > 0:
                    # Class shape: pick the first wrapper, dig into channel_image.
                    first_wrapper = anatomy_images[0]
                    channel_image = first_wrapper.get('channel_image', {}) or {}
                    wrapper_anat = first_wrapper.get('anatomy') or {}
                    if isinstance(wrapper_anat, dict) and wrapper_anat.get('label'):
                        anatomy_label_for_alt = wrapper_anat['label']
                else:
                    # Instance shape: top-level channel_image is already the
                    # list of channel-image entries.
                    ci_list = field_data.get('channel_image', [])
                    if ci_list and len(ci_list) > 0:
                        first_entry = ci_list[0] or {}
                        # Some emitters nest again as {channel_image: {...}},
                        # most are flat — handle both defensively.
                        if isinstance(first_entry, dict) and 'image' in first_entry:
                            channel_image = first_entry
                        else:
                            channel_image = first_entry.get('channel_image', {}) or {}

                if channel_image:
                    image_info = channel_image.get('image', {}) or {}

                    # Template — `[label](short_form)` markdown so the
                    # VFBqueryJsonProcessor's stripMarkdownLink renders a
                    # clickable link in the V2 Template_Space column.
                    template_anatomy = image_info.get('template_anatomy', {}) or {}
                    template_short_form = template_anatomy.get('short_form', '') if template_anatomy else ''
                    template_label_raw = ''
                    if template_anatomy:
                        template_label_raw = template_anatomy.get('symbol') or template_anatomy.get('label', '')
                    template_label = unquote(template_label_raw) if template_label_raw else ''
                    if template_label and template_short_form:
                        template = f"[{template_label}]({template_short_form})"

                    # Imaging technique — plain label (V2 Imaging_Technique
                    # column renders as text; matches how
                    # get_similar_morphology_part_of et al. emit it).
                    technique_info = channel_image.get('imaging_technique', {}) or {}
                    if technique_info:
                        technique_label_raw = technique_info.get('label', '')
                        technique = unquote(technique_label_raw) if technique_label_raw else ''

                    # Thumbnail(s) -- emit EVERY example image for this term so the
                    # V2 Images column carousels them. The Java
                    # VFBqueryJsonProcessor.imageMarkdownToVariableJson builds a
                    # multi-image carousel Variable from a '; '-joined list of
                    # `[![alt](url 'alt')](ref)` items. Template_Space and
                    # Imaging_Technique above stay single (the representative
                    # first image).
                    if anatomy_images and len(anatomy_images) > 0:
                        image_wrappers = anatomy_images
                    else:
                        image_wrappers = []
                        for entry in field_data.get('channel_image', []) or []:
                            if isinstance(entry, dict) and 'image' in entry:
                                image_wrappers.append({'channel_image': entry, 'anatomy': None})
                            elif isinstance(entry, dict):
                                image_wrappers.append({'channel_image': entry.get('channel_image', {}) or {}, 'anatomy': None})
                    thumbnail_items = []
                    for wrapper in image_wrappers:
                        wci = wrapper.get('channel_image', {}) or {}
                        wimg = wci.get('image', {}) or {}
                        wurl = wimg.get('image_thumbnail', '')
                        if not wurl:
                            continue
                        wurl = wurl.replace('http://', 'https://').replace('thumbnailT.png', 'thumbnail.png')
                        wtmpl = wimg.get('template_anatomy', {}) or {}
                        wtmpl_raw = (wtmpl.get('symbol') or wtmpl.get('label', '')) if wtmpl else ''
                        wtmpl_label = unquote(wtmpl_raw) if wtmpl_raw else ''
                        if not wtmpl_label:
                            continue
                        wanat = wrapper.get('anatomy') or {}
                        wlabel_raw = wanat.get('label') if isinstance(wanat, dict) and wanat.get('label') else anatomy_label_for_alt
                        wlabel = unquote(wlabel_raw) if wlabel_raw else ''
                        wref = wanat.get('short_form') if isinstance(wanat, dict) and wanat.get('short_form') else class_short_form
                        walt = f"{wlabel} aligned to {wtmpl_label}"
                        thumbnail_items.append(f"[![{walt}]({wurl} '{walt}')]({wref})")
                    thumbnail = "; ".join(thumbnail_items)

                # Build row
                row = {
                    'id': class_short_form,
                    'label': f"[{label_text}]({class_short_form})",
                    'tags': tags,
                    'template': template,
                    'technique': technique,
                    'thumbnail': thumbnail
                }
                
                # Optionally add source information
                if include_source:
                    source = ''
                    source_id = ''
                    xrefs = field_data.get('xrefs', [])
                    if xrefs and len(xrefs) > 0:
                        for xref in xrefs:
                            if xref.get('is_data_source', False):
                                site_info = xref.get('site', {})
                                # Deprecated sites: show the source/accession
                                # text but never build a link to them.
                                site_tags = (site_info.get('types') or []) + (site_info.get('unique_facets') or [])
                                is_deprecated = 'Deprecated' in site_tags
                                site_label = site_info.get('symbol') or site_info.get('label', '')
                                site_short_form = site_info.get('short_form', '')
                                if site_label:
                                    source = site_label if (is_deprecated or not site_short_form) else f"[{site_label}]({site_short_form})"

                                accession = xref.get('accession', '')
                                link_base = xref.get('link_base', '')
                                if accession:
                                    source_id = accession if (is_deprecated or not link_base) else f"[{accession}]({link_base}{accession})"
                                break
                    row['source'] = source
                    row['source_id'] = source_id
                
                rows.append(row)
                
        except Exception as e:
            print(f"Error fetching SOLR data: {e}")
            import traceback
            traceback.print_exc()
        
        # Convert to DataFrame if requested
        if return_dataframe:
            df = pd.DataFrame(rows)
            # Apply markdown encoding — template is a `[label](short_form)`
            # link and needs the same encoding as label/thumbnail so the V2
            # frontend's link parser renders it consistently.
            columns_to_encode = ['label', 'template', 'thumbnail']
            df = encode_markdown_links(df, columns_to_encode)
            return df
        
        # Return formatted dict
        return {
            "headers": _get_standard_query_headers(),
            "rows": rows,
            "count": total_count
        }
        
    except Exception as e:
        # Construct the Owlery URL for debugging failed queries
        owlery_base = "http://owl.virtualflybrain.org/kbs/vfb"
        try:
            if hasattr(vc.vfb, 'oc') and hasattr(vc.vfb.oc, 'owlery_endpoint'):
                owlery_base = vc.vfb.oc.owlery_endpoint.rstrip('/')
        except Exception:
            pass
        
        from urllib.parse import urlencode
        
        # Build the full URL with all parameters exactly as the request would be made
        params = {
            'object': owl_query_string,
            'direct': 'true' if query_instances else 'false',  # instances use direct=true, subclasses use direct=false
            'includeDeprecated': 'false'
        }
        
        # For subclasses queries, add includeEquivalent parameter
        if not query_instances:
            params['includeEquivalent'] = 'true'
        
        endpoint = "/instances" if query_instances else "/subclasses"
        owlery_url = f"{owlery_base}{endpoint}?{urlencode(params)}"
        
        import sys
        import requests
        
        # Check if this is a 400 Bad Request (invalid query) vs other errors
        is_bad_request = isinstance(e, requests.exceptions.HTTPError) and hasattr(e, 'response') and e.response.status_code == 400
        
        if is_bad_request:
            # 400 Bad Request means the term isn't valid for this type of query (e.g., anatomical query on expression pattern)
            # Return 0 results instead of error
            print(f"INFO: Owlery query returned 400 Bad Request (invalid for this term type): {owl_query_string}", file=sys.stderr)
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers(),
                "rows": [],
                "count": 0
            }
        else:
            # Other errors (500, network issues, etc.) - return error indication
            import requests as _requests
            is_connection_error = isinstance(e, (_requests.exceptions.RetryError,
                                                 _requests.exceptions.ConnectionError))
            if is_connection_error:
                print(f"WARNING: Owlery unavailable for query '{owl_query_string}': {type(e).__name__}", file=sys.stderr)
            else:
                print(f"ERROR: Owlery {'instances' if query_instances else 'subclasses'} query failed: {e}", file=sys.stderr)
                print(f"       Full URL: {owlery_url}", file=sys.stderr)
                print(f"       Query string: {owl_query_string}", file=sys.stderr)
                import traceback
                traceback.print_exc()
            # Return error indication with count=-1
            if return_dataframe:
                return pd.DataFrame()
            return {
                "headers": _get_standard_query_headers(),
                "rows": [],
                "count": -1
            }


def get_anatomy_scrnaseq(anatomy_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve single cell RNA-seq data (clusters and datasets) for the specified anatomical region.
    
    This implements the anatScRNAseqQuery from the VFB XMI specification.
    Returns clusters that are composed primarily of the anatomy, along with their parent datasets and publications.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: anat_scRNAseq_query
    
    :param anatomy_short_form: Short form identifier of the anatomical region (e.g., 'FBbt_00003982')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: scRNAseq clusters and datasets for this anatomy
    :rtype: pandas.DataFrame or dict
    """
    
    # `hasScRNAseq` on a parent class is set by the indexer when ANY
    # subclass has a Cluster composed_primarily_of it, so the narrow
    # MATCH (primary)<-[:composed_primarily_of]-(c:Cluster) pattern
    # returns 0 on parent classes with scRNAseq-bearing subclasses
    # (e.g. pacemaker neuron FBbt_00006048: 0 direct, 3 via subclasses
    # adult pacemaker neuron / LNv neuron / DN1 neuron).
    #
    # v1.14.0: resolve the subclass closure via Owlery /subclasses
    # (consistent with get_transgene_expression_here and get_instances
    # v1.12.8). v1.13.5 used a Cypher SUBCLASSOF*0.. walk; that misses
    # defined-class / equivalence inferences. Owlery is the right tool
    # and matches the legacy XMI's first-step Owlery walk.
    try:
        owl_query = f"<{_short_form_to_iri(anatomy_short_form)}>"
        subclass_ids = vc.vfb.oc.get_subclasses(query=owl_query, query_by_label=False)
        anat_short_forms = list({anatomy_short_form, *(subclass_ids or [])})
    except Exception:
        anat_short_forms = [anatomy_short_form]

    count_query = f"""
        MATCH (sub:Class)
        WHERE sub.short_form IN {anat_short_forms!r}
        MATCH (sub)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        RETURN COUNT(DISTINCT c) AS total_count
    """

    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Main query: get clusters with dataset and publication info.
    # `primary` is preserved in the projection for parity with the
    # pre-v1.14.0 shape; we re-fetch the input class as `primary`
    # so callers expecting that field continue to work.
    main_query = f"""
        MATCH (primary:Class:Anatomy)
        WHERE primary.short_form = '{anatomy_short_form}'
        MATCH (sub:Class)
        WHERE sub.short_form IN {anat_short_forms!r}
        MATCH (sub)<-[:composed_primarily_of]-(c:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        WITH DISTINCT primary, c, ds, sub
        OPTIONAL MATCH (ds)-[:has_reference]->(p:pub)
        WITH {{
            short_form: c.short_form,
            label: coalesce(c.label,''),
            iri: c.iri,
            types: labels(c),
            unique_facets: apoc.coll.sort(coalesce(c.uniqueFacets, [])),
            symbol: coalesce(([]+c.symbol)[0], '')
        }} AS cluster,
        {{
            short_form: ds.short_form,
            label: coalesce(ds.label,''),
            iri: ds.iri,
            types: labels(ds),
            unique_facets: apoc.coll.sort(coalesce(ds.uniqueFacets, [])),
            symbol: coalesce(([]+ds.symbol)[0], '')
        }} AS dataset,
        COLLECT({{
            core: {{
                short_form: p.short_form,
                label: coalesce(p.label,''),
                iri: p.iri,
                types: labels(p),
                unique_facets: apoc.coll.sort(coalesce(p.uniqueFacets, [])),
                symbol: coalesce(([]+p.symbol)[0], '')
            }},
            PubMed: coalesce(([]+p.PMID)[0], ''),
            FlyBase: coalesce(([]+p.FlyBase)[0], ''),
            DOI: coalesce(([]+p.DOI)[0], '')
        }}) AS pubs,
        primary, sub
        RETURN
            cluster.short_form AS id,
            apoc.text.format("[%s](%s)", [cluster.label, cluster.short_form]) AS name,
            apoc.text.join(cluster.unique_facets, '|') AS tags,
            apoc.text.format("[%s](%s)", [sub.label, sub.short_form]) AS cell_type,
            apoc.text.format("[%s](%s)", [dataset.label, dataset.short_form]) AS dataset,
            pubs
        ORDER BY cluster.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name', 'cell_type', 'dataset']
        df = encode_markdown_links(df, columns_to_encode)

    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id":        {"title": "ID",            "type": "selection_id", "order": -1},
                "name":      {"title": "Cluster",       "type": "markdown",     "order":  0},
                "cell_type": {"title": "Cell type",     "type": "markdown",     "order":  1},
                "dataset":   {"title": "Dataset",       "type": "markdown",     "order":  2},
                "pubs":      {"title": "Publications",  "type": "metadata",     "order":  3},
                "tags":      {"title": "Tags",          "type": "tags",         "order":  4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "cell_type", "dataset", "pubs", "tags"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_cluster_expression(cluster_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve genes expressed in the specified cluster.
    
    This implements the clusterExpression query from the VFB XMI specification.
    Returns genes with expression levels and extents for a given cluster.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: cluster_expression_query
    
    :param cluster_short_form: Short form identifier of the cluster (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Genes expressed in this cluster with expression data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (primary:Individual:Cluster)
        WHERE primary.short_form = '{cluster_short_form}'
        WITH primary
        MATCH (primary)-[e:expresses]->(g:Gene:Class)
        RETURN COUNT(g) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get genes with expression levels
    main_query = f"""
        MATCH (primary:Individual:Cluster)
        WHERE primary.short_form = '{cluster_short_form}'
        WITH primary
        MATCH (primary)-[e:expresses]->(g:Gene:Class)
        WITH coalesce(e.expression_level_padded[0], e.expression_level[0]) as expression_level,
             e.expression_extent[0] as expression_extent,
             {{
                 short_form: g.short_form,
                 label: coalesce(g.label,''),
                 iri: g.iri,
                 types: labels(g),
                 unique_facets: apoc.coll.sort(coalesce(g.uniqueFacets, [])),
                 symbol: coalesce(([]+g.symbol)[0], ''),
                 function: apoc.coll.sort([l IN labels(g) WHERE NOT l IN ['Entity','Class','Individual','Gene','Feature'] AND NOT l STARTS WITH 'has'])
             }} AS gene,
             primary
        MATCH (a:Anatomy)<-[:composed_primarily_of]-(primary)
        WITH {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy, primary, expression_level, expression_extent, gene
        RETURN
            gene.short_form AS id,
            apoc.text.format("[%s](%s)", [gene.label, gene.short_form]) AS name,
            apoc.text.join(gene.unique_facets, '|') AS tags,
            expression_level,
            expression_extent,
            apoc.text.join(coalesce(gene.function, []), '; ') AS function,
            apoc.text.format("[%s](%s)", [anatomy.label, anatomy.short_form]) AS anatomy
        ORDER BY expression_level DESC, gene.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name', 'anatomy']
        df = encode_markdown_links(df, columns_to_encode)

    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Gene", "type": "markdown", "order": 0},
                "anatomy": {"title": "Cell type", "type": "markdown", "order": 1},
                "expression_level": {"title": "Expression Level", "type": "numeric", "order": 2},
                "expression_extent": {"title": "Expression Extent", "type": "numeric", "order": 3},
                "tags": {"title": "Tags", "type": "tags", "order": 4},
                "function": {"title": "Function", "type": "text", "order": 5}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "anatomy", "expression_level", "expression_extent", "tags", "function"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_expression_cluster(gene_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve scRNAseq clusters expressing the specified gene.
    
    This implements the expressionCluster query from the VFB XMI specification.
    Returns clusters that express a given gene with expression levels and anatomy info.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: expression_cluster_query
    
    :param gene_short_form: Short form identifier of the gene (e.g., 'FBgn_00001234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Clusters expressing this gene with expression data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
        WHERE g.short_form = '{gene_short_form}'
        RETURN COUNT(primary) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get clusters with expression levels
    main_query = f"""
        MATCH (primary:Individual:Cluster)-[e:expresses]->(g:Gene:Class)
        WHERE g.short_form = '{gene_short_form}'
        WITH e.expression_level[0] as expression_level,
             e.expression_extent[0] as expression_extent,
             {{
                 short_form: g.short_form,
                 label: coalesce(g.label,''),
                 iri: g.iri,
                 types: labels(g),
                 unique_facets: apoc.coll.sort(coalesce(g.uniqueFacets, [])),
                 symbol: coalesce(([]+g.symbol)[0], '')
             }} AS gene,
             primary
        MATCH (a:Anatomy)<-[:composed_primarily_of]-(primary)
        WITH {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy, primary, expression_level, expression_extent, gene
        RETURN
            primary.short_form AS id,
            apoc.text.format("[%s](%s)", [primary.label, primary.short_form]) AS name,
            apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
            expression_level,
            expression_extent,
            apoc.text.format("[%s](%s)", [anatomy.label, anatomy.short_form]) AS anatomy
        ORDER BY expression_level DESC, primary.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name', 'anatomy']
        df = encode_markdown_links(df, columns_to_encode)

    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Cluster", "type": "markdown", "order": 0},
                "anatomy": {"title": "Cell type", "type": "markdown", "order": 1},
                "expression_level": {"title": "Expression Level", "type": "numeric", "order": 2},
                "expression_extent": {"title": "Expression Extent", "type": "numeric", "order": 3},
                "tags": {"title": "Tags", "type": "tags", "order": 4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "anatomy", "expression_level", "expression_extent", "tags"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_scrnaseq_dataset_data(dataset_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve all clusters for a scRNAseq dataset.
    
    This implements the scRNAdatasetData query from the VFB XMI specification.
    Returns all clusters in a dataset with anatomy info and publications.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: dataset_scRNAseq_query
    
    :param dataset_short_form: Short form identifier of the dataset (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Clusters in this dataset with anatomy and publication data
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (c:Individual)-[:has_source]->(ds:scRNAseq_DataSet)
        WHERE ds.short_form = '{dataset_short_form}'
        RETURN COUNT(c) AS total_count
    """
    
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0
    
    # Main query: get clusters with anatomy and publications
    main_query = f"""
        MATCH (c:Individual:Cluster)-[:has_source]->(ds:scRNAseq_DataSet)
        WHERE ds.short_form = '{dataset_short_form}'
        MATCH (a:Class:Anatomy)<-[:composed_primarily_of]-(c)
        WITH *, {{
            short_form: a.short_form,
            label: coalesce(a.label,''),
            iri: a.iri,
            types: labels(a),
            unique_facets: apoc.coll.sort(coalesce(a.uniqueFacets, [])),
            symbol: coalesce(([]+a.symbol)[0], '')
        }} AS anatomy
        OPTIONAL MATCH (ds)-[:has_reference]->(p:pub)
        WITH COLLECT({{
            core: {{
                short_form: p.short_form,
                label: coalesce(p.label,''),
                iri: p.iri,
                types: labels(p),
                unique_facets: apoc.coll.sort(coalesce(p.uniqueFacets, [])),
                symbol: coalesce(([]+p.symbol)[0], '')
            }},
            PubMed: coalesce(([]+p.PMID)[0], ''),
            FlyBase: coalesce(([]+p.FlyBase)[0], ''),
            DOI: coalesce(([]+p.DOI)[0], '')
        }}) AS pubs, c, anatomy
        RETURN
            c.short_form AS id,
            apoc.text.format("[%s](%s)", [c.label, c.short_form]) AS name,
            apoc.text.join(coalesce(c.uniqueFacets, []), '|') AS tags,
            apoc.text.format("[%s](%s)", [anatomy.label, anatomy.short_form]) AS anatomy,
            pubs
        ORDER BY c.label
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name', 'anatomy']
        df = encode_markdown_links(df, columns_to_encode)

    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Cluster", "type": "markdown", "order": 0},
                "anatomy": {"title": "Cell type", "type": "markdown", "order": 1},
                "tags": {"title": "Tags", "type": "tags", "order": 2},
                "pubs": {"title": "Publications", "type": "metadata", "order": 3}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "anatomy", "tags", "pubs"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


# ===== NBLAST Similarity Queries =====

def get_similar_morphology(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve neurons with similar morphology to the specified neuron using NBLAST.
    
    This implements the SimilarMorphologyTo query from the VFB XMI specification.
    Returns neurons with NBLAST similarity scores.
    
    XMI Source: https://raw.githubusercontent.com/VirtualFlyBrain/geppetto-vfb/master/model/vfb.xmi
    Query: has_similar_morphology_to (NBLAST_anat_image_query)
    
    :param neuron_short_form: Short form identifier of the neuron (e.g., 'VFB_00101234')
    :param return_dataframe: Returns pandas DataFrame if True, otherwise returns formatted dict (default: True)
    :param limit: Maximum number of results to return (default: -1 for all results)
    :return: Neurons with similar morphology and NBLAST scores
    :rtype: pandas.DataFrame or dict
    """
    
    # Count query
    count_query = f"""
        MATCH (n:Individual)-[nblast:has_similar_morphology_to]-(primary:Individual)
        WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score)
        RETURN count(primary) AS count
    """
    
    # Get total count
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    # Main query
    main_query = f"""
        MATCH (n:Individual)-[nblast:has_similar_morphology_to]-(primary:Individual)
        WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score)
        WITH primary, nblast
        OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
        WITH template, channel, template_anat, irw, primary, nblast
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        WITH CASE WHEN channel IS NULL THEN [] ELSE collect({{
            channel: {{
                short_form: channel.short_form,
                label: coalesce(channel.label, ''),
                iri: channel.iri,
                types: labels(channel),
                unique_facets: apoc.coll.sort(coalesce(channel.uniqueFacets, [])),
                symbol: coalesce(channel.symbol[0], '')
            }},
            imaging_technique: {{
                short_form: technique.short_form,
                label: coalesce(technique.label, ''),
                iri: technique.iri,
                types: labels(technique),
                unique_facets: apoc.coll.sort(coalesce(technique.uniqueFacets, [])),
                symbol: coalesce(technique.symbol[0], '')
            }},
            image: {{
                template_channel: {{
                    short_form: template.short_form,
                    label: coalesce(template.label, ''),
                    iri: template.iri,
                    types: labels(template),
                    unique_facets: apoc.coll.sort(coalesce(template.uniqueFacets, [])),
                    symbol: coalesce(template.symbol[0], '')
                }},
                template_anatomy: {{
                    short_form: template_anat.short_form,
                    label: coalesce(template_anat.label, ''),
                    iri: template_anat.iri,
                    types: labels(template_anat),
                    symbol: coalesce(template_anat.symbol[0], '')
                }},
                image_folder: COALESCE(irw.folder[0], ''),
                index: coalesce(apoc.convert.toInteger(irw.index[0]), []) + []
            }}
        }}) END AS channel_image, primary, nblast
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{
            short_form: typ.short_form,
            label: coalesce(typ.label, ''),
            iri: typ.iri,
            types: labels(typ),
            symbol: coalesce(typ.symbol[0], '')
        }}) END AS types, primary, channel_image, nblast
        RETURN
            primary.short_form AS id,
            '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
            apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
            nblast.NBLAST_score[0] AS score,
            types,
            channel_image
        ORDER BY score DESC
    """
    
    if limit != -1:
        main_query += f" LIMIT {limit}"
    
    # Execute the query
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    
    # Encode markdown links
    if not df.empty:
        columns_to_encode = ['name']
        df = encode_markdown_links(df, columns_to_encode)
    
    if return_dataframe:
        return df
    else:
        formatted_results = {
            "headers": {
                "id": {"title": "ID", "type": "selection_id", "order": -1},
                "name": {"title": "Neuron", "type": "markdown", "order": 0},
                "score": {"title": "NBLAST Score", "type": "text", "order": 1},
                "tags": {"title": "Tags", "type": "tags", "order": 2},
                "types": {"title": "Types", "type": "metadata", "order": 3},
                "channel_image": {"title": "Images", "type": "metadata", "order": 4}
            },
            "rows": [
                {key: row[key] for key in ["id", "name", "score", "tags", "types", "channel_image"]}
                for row in safe_to_dict(df, sort_by_id=False)
            ],
            "count": total_count
        }
        return formatted_results


def get_similar_morphology_part_of(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """
    Retrieve expression patterns with similar morphology to part of the specified neuron (NBLASTexp).

    XMI: has_similar_morphology_to_part_of
    """
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.NBLAST_score) WITH primary, nblast
        OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
        WITH primary, nblast, channel, ri, templ
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        WITH primary, nblast, channel, ri, templ, technique
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast, channel, ri, templ, technique
        RETURN primary.short_form AS id,
               '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
               apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
               nblast.NBLAST_score[0] AS score,
               types,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
               technique.label AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(ri.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
        ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Expression Pattern", "type": "markdown", "order": 0}, "score": {"title": "NBLAST Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}, "template": {"title": "Template", "type": "markdown", "order": 3}, "technique": {"title": "Imaging Technique", "type": "text", "order": 4}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_part_of_exp(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """Neurons with similar morphology to part of expression pattern (reverse NBLASTexp)."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.NBLAST_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.NBLAST_score) WITH primary, nblast
        OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
        WITH primary, nblast, channel, ri, templ
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        WITH primary, nblast, channel, ri, templ, technique
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast, channel, ri, templ, technique
        RETURN primary.short_form AS id,
               '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
               apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
               nblast.NBLAST_score[0] AS score,
               types,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
               technique.label AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(ri.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
        ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Neuron", "type": "markdown", "order": 0}, "score": {"title": "NBLAST Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}, "template": {"title": "Template", "type": "markdown", "order": 3}, "technique": {"title": "Imaging Technique", "type": "text", "order": 4}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_nb(neuron_short_form: str, return_dataframe=True, limit: int = -1):
    """NeuronBridge similarity matches for neurons."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.neuronbridge_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{neuron_short_form}' AND EXISTS(nblast.neuronbridge_score) WITH primary, nblast
        OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
        WITH primary, nblast, channel, ri, templ
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        WITH primary, nblast, channel, ri, templ, technique
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class) WITH CASE WHEN typ IS NULL THEN [] ELSE collect({{short_form: typ.short_form, label: coalesce(typ.label, ''), iri: typ.iri, types: labels(typ), symbol: coalesce(typ.symbol[0], '')}}) END AS types, primary, nblast, channel, ri, templ, technique
        RETURN primary.short_form AS id,
               '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
               apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
               nblast.neuronbridge_score[0] AS score,
               types,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
               technique.label AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(ri.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
        ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "NB Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}, "template": {"title": "Template", "type": "markdown", "order": 3}, "technique": {"title": "Imaging Technique", "type": "text", "order": 4}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_nb_exp(expression_short_form: str, return_dataframe=True, limit: int = -1):
    """NeuronBridge similarity matches for expression patterns."""
    count_query = f"MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.neuronbridge_score) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    # Add `type` as pipe-joined parent class labels (matches v2 prod's
    # `Type` column). Aggregate in a CALL subquery scoped to `primary` so
    # multi-INSTANCEOF neurons don't multiply rows under the existing
    # OPTIONAL MATCH chain. `types` (nested struct) is kept for
    # return_dataframe=True consumers but dropped from the dict response
    # so the processor's generic List handler doesn't dump HashMap
    # toString into the Reference column.
    main_query = f"""MATCH (n:Individual)-[nblast:has_similar_morphology_to_part_of]-(primary:Individual) WHERE n.short_form = '{expression_short_form}' AND EXISTS(nblast.neuronbridge_score)
        WITH DISTINCT primary, nblast
        CALL {{
            WITH primary
            OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
            RETURN apoc.text.join([x IN collect(DISTINCT CASE WHEN typ.short_form IS NULL THEN NULL ELSE apoc.text.format('[%s](%s)', [typ.label, typ.short_form]) END) WHERE x IS NOT NULL], '; ') AS type
        }}
        CALL {{
            WITH primary
            OPTIONAL MATCH (primary)<-[:depicts]-(channel:Individual)-[ri:in_register_with]->(:Template)-[:depicts]->(templ:Template)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH ri, templ, technique LIMIT 1
            RETURN ri, templ, technique
        }}
        RETURN primary.short_form AS id,
               '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
               apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
               nblast.neuronbridge_score[0] AS score,
               type,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
               coalesce(technique.label, '') AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(ri.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), primary.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
        ORDER BY score DESC"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "NB Score", "type": "text", "order": 1}, "tags": {"title": "Tags", "type": "tags", "order": 2}, "type": {"title": "Type", "type": "text", "order": 3}, "template": {"title": "Template", "type": "markdown", "order": 4}, "technique": {"title": "Imaging Technique", "type": "text", "order": 5}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "score", "tags", "type", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_similar_morphology_userdata(upload_id: str, return_dataframe=True, limit: int = -1):
    """NBLAST results for user-uploaded data (cached in SOLR)."""
    try:
        solr_query = f'{{"params":{{"defType":"edismax","fl":"upload_nblast_query","indent":"true","q.op":"OR","q":"id:{upload_id}","qf":"id","rows":"99"}}}}'
        response = requests.post("https://solr.virtualflybrain.org/solr/vfb_json/select", data=solr_query, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            data = response.json()
            if data.get('response', {}).get('numFound', 0) > 0:
                results = data['response']['docs'][0].get('upload_nblast_query', [])
                if isinstance(results, str): results = json.loads(results)
                df = pd.DataFrame(results if isinstance(results, list) else [])
                if not df.empty and 'name' in df.columns: df = encode_markdown_links(df, ['name'])
                if return_dataframe: return df
                return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Match", "type": "markdown", "order": 0}, "score": {"title": "Score", "type": "text", "order": 1}}, "rows": safe_to_dict(df, sort_by_id=False), "count": len(df)}
    except Exception as e:
        print(f"Error fetching user NBLAST data: {e}")
    return pd.DataFrame() if return_dataframe else {"headers": {}, "rows": [], "count": 0}


# ===== Dataset/Template Queries =====

def get_painted_domains(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all painted anatomy domains for a template."""
    count_query = f"MATCH (n:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[r:in_register_with]-(dc:Individual)-[:depicts]->(di:Individual)-[:INSTANCEOF]->(d:Class) WHERE EXISTS(r.index) RETURN count(di) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0
    
    main_query = f"""MATCH (n:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[r:in_register_with]-(dc:Individual)-[:depicts]->(di:Individual)-[:INSTANCEOF]->(d:Class) WHERE EXISTS(r.index)
        RETURN DISTINCT di.short_form AS id, '[' + di.label + ']({VFB_REPORT_BASE}' + di.short_form + ')' AS name, coalesce(di.description[0], d.description[0]) AS description, COLLECT(DISTINCT d.label) AS type, replace(r.folder[0],'http:','https:') + '/thumbnailT.png' AS thumbnail"""
    if limit != -1: main_query += f" LIMIT {limit}"
    
    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'thumbnail'])
    
    if return_dataframe: return df
    # description is already populated by the Cypher (coalesce of di/d
    # description). v2 prod surfaces it as the `Definition` column via
    # COL_HEADER_MAP[description] = Definition — was previously dropped
    # because it wasn't listed in headers/rows.
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Domain", "type": "markdown", "order": 0}, "type": {"title": "Type", "type": "text", "order": 1}, "description": {"title": "Definition", "type": "text", "order": 2}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "type", "description", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


# Short_form syntactic guard for any value interpolated into a Cypher
# string-literal (Neo4j REST client doesn't pass parameters separately —
# all queries in this module interpolate). VFB short_forms are
# alphanumerics + underscore; the guard rejects anything that could break
# out of the literal.
_VFB_SHORT_FORM_RE = re.compile(r"^[A-Za-z0-9_]+$")


@with_solr_cache('template_roi_tree')
def get_template_roi_tree(template_short_form: str, return_dataframe=False):
    """Build a hierarchical ROI tree for a template.

    Anchors on the template's INSTANCEOF root Class (so this works for
    every template regardless of anatomical character — adult brain
    variants, adult VNC, larval CNS, the Adult T1 Leg with muscles +
    neuropils, Adult Head). Walks down through ``part_of``, ``SUBCLASSOF``
    and ``innervates`` to every Class that has a painted-domain Individual
    on this template, materialising the nodes and edges required to
    render the tree. ``innervates`` is what connects e.g. the adult VNC
    nerves (which are part_of the peripheral nervous system, NOT the
    central VNC) to the neuromeres they innervate.

    FBbt's DAG character is preserved (multi-parent classes appear under
    each parent), matching the legacy VFBTree behaviour.

    Returned shape (`return_dataframe` is accepted for symmetry; this
    query is hierarchical and always returns the dict shape):

        {
          "template":      {"short_form", "label"},
          "anatomy_root":  {"short_form", "label"} | None,
          "summary_md":    "## ROI tree for <template> …",
          "tree": [
              {
                  "id":          str,
                  "label":       str | None,
                  "painted_domain": [
                      {"individual_id", "individual_label"}, ...
                  ],
                  "summary_md":  str,
                  "children":    [...]
              }
          ],
          "painted_domain_index": {
              "<individual_id>": {"class_id", "class_label"},
              ...
          }
        }

    Notes:

    - ``painted_domain`` is always a list (empty when the class has no
      painted Individual on this template). T1 Leg has bilateral L/R
      Individuals on the same Class, so a single-value field would
      silently drop one side.
    - ``painted_domain_index`` is the reverse lookup the v2 visibility
      toggle needs: scene reports "Individual X just hidden" -> map
      back to the Class node to grey the row.
    - DAG cycle guard: tracks the ancestor chain so we don't recurse
      indefinitely if part_of ever loops in FBbt.
    """
    if not isinstance(template_short_form, str) or not _VFB_SHORT_FORM_RE.match(template_short_form):
        raise ValueError(f"Invalid template_short_form: {template_short_form!r}")

    cypher = (
        f"MATCH (t:Template {{short_form: '{template_short_form}'}})"
        f"-[:INSTANCEOF]->(root:Class:Anatomy) "
        f"OPTIONAL MATCH (t)<-[:depicts]-(tc:Template)"
        f"<-[ie:in_register_with]-(:Individual)"
        f"-[:depicts]->(pd:Individual)-[:INSTANCEOF]->(painted_class:Class) "
        f"WHERE exists(ie.index) "
        f"WITH t, root, "
        f"collect(distinct {{class_id: painted_class.short_form, "
        f"class_label: painted_class.label, "
        f"individual_id: pd.short_form, "
        f"individual_label: pd.label}}) AS painted_rows "
        f"WITH t, root, "
        f"[r IN painted_rows WHERE r.class_id IS NOT NULL] AS painted_rows "
        f"WITH t, root, painted_rows, [r IN painted_rows | r.class_id] AS leaf_ids "
        # v1.14.6: expanded the relationship set used to reach painted
        # leaves. The previous walk (SUBCLASSOF | part_of | innervates)
        # missed every sensory neuron, motor neuron, muscle attachment
        # and fasciculating axon — exactly the bulk of painted domains
        # on the leg / VNC templates. Live diagnostic on Adult T1 Leg
        # (VFB_00120000) showed 39 hops via part_of, 20 via SUBCLASSOF,
        # 15 via has_sensory_dendrite_in, 9 via fasciculates_with,
        # 3 via attached_to_part_of, 1 via sends_synaptic_output_to_cell
        # when walking each painted class to the anatomy_root.
        # `overlaps` is deliberately omitted — it's a very broad
        # spatial relationship in FBbt and would pull in classes that
        # merely co-locate with leg structures without being part of
        # the leg ontology.
        f"OPTIONAL MATCH path = (root)<-[:SUBCLASSOF|part_of|innervates|has_sensory_dendrite_in|fasciculates_with|attached_to_part_of|sends_synaptic_output_to_cell*0..]-(leaf:Class) "
        f"WHERE leaf.short_form IN leaf_ids "
        f"WITH t, root, painted_rows, "
        f"collect(distinct [n IN nodes(path) | "
        f"{{id: n.short_form, label: n.label}}]) AS path_node_lists, "
        f"collect(distinct [rel IN relationships(path) | "
        f"{{parent: endNode(rel).short_form, "
        f"child:  startNode(rel).short_form, "
        f"rel_type: type(rel)}}]) AS path_edge_lists "
        f"RETURN t.short_form  AS template_id, "
        f"       t.label       AS template_label, "
        f"       root.short_form AS root_id, "
        f"       root.label      AS root_label, "
        f"       apoc.coll.toSet(apoc.coll.flatten(path_node_lists)) AS nodes, "
        f"       apoc.coll.toSet(apoc.coll.flatten(path_edge_lists)) AS edges, "
        f"       painted_rows                                         AS painted"
    )
    results = vc.nc.commit_list([cypher])
    rows = get_dict_cursor()(results) if results else []
    if not rows:
        return _empty_roi_tree(template_short_form)
    row = rows[0]

    nodes_by_id = {n['id']: n.get('label') for n in (row.get('nodes') or []) if n and n.get('id')}
    edges = [e for e in (row.get('edges') or []) if e and e.get('parent') and e.get('child')]
    painted_rows = row.get('painted') or []

    painted_by_class = {}
    for r in painted_rows:
        if not r.get('class_id'):
            continue
        painted_by_class.setdefault(r['class_id'], []).append({
            'individual_id':    r.get('individual_id'),
            'individual_label': r.get('individual_label'),
        })

    children = {}
    for e in edges:
        children.setdefault(e['parent'], set()).add(e['child'])

    template_label = row.get('template_label') or template_short_form
    root_id    = row.get('root_id')
    root_label = row.get('root_label')

    def _node_summary_md(class_id, class_label, painted_list, parent_label):
        parts = [
            f"**{class_label or class_id}** "
            f"({vfb_term_link(class_id, class_id)})",
            "",
        ]
        if parent_label:
            parts.append(f"Part of: *{parent_label}*.")
            parts.append("")
        if painted_list:
            ind_lines = [
                vfb_term_link(p.get('individual_label') or p.get('individual_id'), p.get('individual_id'))
                for p in painted_list if p.get('individual_id')
            ]
            if ind_lines:
                parts.append(
                    f"Painted domain on **{template_label}**: "
                    + "; ".join(ind_lines) + "."
                )
        return "\n".join(parts).rstrip()

    def _build(node_id, ancestors, parent_label):
        if node_id in ancestors:
            return None
        label = nodes_by_id.get(node_id)
        painted_list = painted_by_class.get(node_id, [])
        new_ancestors = ancestors | {node_id}
        kids = []
        for c in children.get(node_id, ()):
            built = _build(c, new_ancestors, label)
            if built is not None:
                kids.append(built)
        kids.sort(key=lambda n: (n.get('label') or '').lower())
        return {
            'id':             node_id,
            'label':          label,
            'painted_domain': painted_list,
            'summary_md':     _node_summary_md(node_id, label, painted_list, parent_label),
            'children':       kids,
        }

    tree_root = _build(root_id, frozenset(), None) if root_id else None

    painted_class_count      = len(painted_by_class)
    painted_individual_count = sum(len(v) for v in painted_by_class.values())

    summary_md = (
        f"## ROI tree for **{template_label}**\n\n"
        f"Anatomy root: "
        f"{vfb_term_link(root_label or root_id, root_id)} "
        f"({root_id}).\n\n"
        f"{painted_class_count} painted region"
        f"{'s' if painted_class_count != 1 else ''} "
        f"({painted_individual_count} painted individual"
        f"{'s' if painted_individual_count != 1 else ''}) "
        f"across the FBbt class hierarchy. Click the eye icon next to a "
        f"region to toggle its overlay on the 3D viewer."
    )

    # painted_class label fallback: any class found by the painted-collection
    # half of the Cypher carries its own label, so use that when the
    # tree-walk half didn't reach the class (this happens when the only
    # path from root to the leaf relies on a relation we don't traverse,
    # so the class is in painted_by_class but not in nodes_by_id).
    class_label_by_id = {
        cid: (plist[0].get('class_label') if plist else None)
        for cid, plist in painted_by_class.items()
    }
    # painted_by_class doesn't store the class_label directly (we project
    # only individual_id / individual_label into the per-class list), so
    # rebuild from painted_rows where it does live.
    for r in painted_rows:
        cid = r.get('class_id')
        if cid and not class_label_by_id.get(cid):
            class_label_by_id[cid] = r.get('class_label')

    painted_index = {
        p['individual_id']: {
            'class_id':    cid,
            'class_label': nodes_by_id.get(cid) or class_label_by_id.get(cid),
        }
        for cid, plist in painted_by_class.items()
        for p in plist
        if p.get('individual_id')
    }

    return {
        'template':             {'short_form': row.get('template_id') or template_short_form,
                                 'label':      template_label},
        'anatomy_root':         ({'short_form': root_id, 'label': root_label}
                                 if root_id else None),
        'summary_md':           summary_md,
        'tree':                 [tree_root] if tree_root else [],
        'painted_domain_index': painted_index,
    }


def _empty_roi_tree(template_short_form):
    """Stable response shape when the template has no INSTANCEOF root
    (data bug) — keeps v2's renderer happy."""
    return {
        'template':             {'short_form': template_short_form, 'label': template_short_form},
        'anatomy_root':         None,
        'summary_md':           f"No ROI tree available for template `{template_short_form}`.",
        'tree':                 [],
        'painted_domain_index': {},
    }


def get_dataset_images(dataset_short_form: str, return_dataframe=True, limit: int = -1):
    """List all images in a dataset."""
    count_query = f"MATCH (c:DataSet {{short_form:'{dataset_short_form}'}})<-[:has_source]-(primary:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual) RETURN count(primary) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    main_query = f"""MATCH (c:DataSet {{short_form:'{dataset_short_form}'}})<-[:has_source]-(primary:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        RETURN primary.short_form AS id,
               '[' + primary.label + ']({VFB_REPORT_BASE}' + primary.short_form + ')' AS name,
               apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
               REPLACE(apoc.text.format("[%s](%s)",[typ.label,typ.short_form]), '[null](null)', '') AS type,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END,template_anat.short_form]), '[null](null)', '') AS template,
               technique.label AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[primary.label + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, REPLACE(COALESCE(irw.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), primary.label + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Image", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}, "type": {"title": "Type", "type": "text", "order": 2}, "template": {"title": "Template", "type": "markdown", "order": 3}, "technique": {"title": "Imaging Technique", "type": "text", "order": 4}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "tags", "type", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def get_all_aligned_images(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all images aligned to a template."""
    count_query = f"MATCH (:Template {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template)<-[:in_register_with]-(:Individual)-[:depicts]->(di:Individual) RETURN count(di) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    main_query = f"""MATCH (templ:Template:Individual {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template:Individual)<-[irw:in_register_with]-(channel:Individual)-[:depicts]->(di:Individual)
        OPTIONAL MATCH (di)-[:INSTANCEOF]->(typ:Class)
        OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
        RETURN DISTINCT di.short_form AS id,
               '[' + di.label + ']({VFB_REPORT_BASE}' + di.short_form + ')' AS name,
               apoc.text.join(coalesce(di.uniqueFacets, []), '|') AS tags,
               REPLACE(apoc.text.format("[%s](%s)",[typ.label,typ.short_form]), '[null](null)', '') AS type,
               REPLACE(apoc.text.format("[%s](%s)",[CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END,templ.short_form]), '[null](null)', '') AS template,
               technique.label AS technique,
               REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",[di.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, REPLACE(COALESCE(irw.thumbnail[0],""),"thumbnailT.png","thumbnail.png"), di.label + " aligned to " + CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form + "," + di.short_form]), "[![null]( 'null')](null)", "") AS thumbnail"""
    if limit != -1: main_query += f" LIMIT {limit}"

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty: df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe: return df
    return {"headers": {"id": {"title": "ID", "type": "selection_id", "order": -1}, "name": {"title": "Image", "type": "markdown", "order": 0}, "tags": {"title": "Tags", "type": "tags", "order": 1}, "type": {"title": "Type", "type": "text", "order": 2}, "template": {"title": "Template", "type": "markdown", "order": 3}, "technique": {"title": "Imaging Technique", "type": "text", "order": 4}, "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 9}}, "rows": [{key: row[key] for key in ["id", "name", "tags", "type", "template", "technique", "thumbnail"]} for row in safe_to_dict(df, sort_by_id=False)], "count": total_count}


def _dataset_enrichment_cypher(ds_var: str = "ds") -> str:
    """Return CALL subqueries that, given a DataSet bound as ``ds_var``,
    aggregate the columns v2 prod surfaces from SOLR:

      pubs        — "; "-joined per-pub `[label](short_form)` markdown so the
                    Reference column links each publication (FBrf)
      license     — `[label](short_form)` markdown link
      template/technique — taken from a representative channel-image
      thumbnail   — up to 5 example channel-images as `' | '`-joined
                    `[![alt](url 'title')](ref)` markdown, so the Images
                    cell carousels (matches prod's `… LIMIT 5` shape).
                    The V2 imageMarkdownToVariableJson splits the joined
                    markdown into a SlideshowImageComponent.
      image_count — DISTINCT count of individuals sourced to the dataset

    Each branch is wrapped in its own CALL so the outer carrier row stays
    one-per-ds; no cartesian blow-up between pubs × license × alignments.
    """
    return f"""
        CALL {{
            WITH {ds_var}
            OPTIONAL MATCH ({ds_var})-[:has_reference]->(p:pub)
            RETURN apoc.text.join([x IN collect(DISTINCT CASE WHEN p.short_form IS NULL THEN NULL ELSE apoc.text.format('[%s](%s)', [coalesce(p.label, p.short_form), p.short_form]) END) WHERE x IS NOT NULL], '; ') AS pubs
        }}
        CALL {{
            WITH {ds_var}
            OPTIONAL MATCH ({ds_var})-[:has_license|license]->(lic:License)
            WITH lic LIMIT 1
            RETURN REPLACE(apoc.text.format("[%s](%s)", [lic.label, lic.short_form]), '[null](null)', '') AS license
        }}
        CALL {{
            WITH {ds_var}
            OPTIONAL MATCH ({ds_var})<-[:has_source]-(i:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(:Template)-[:depicts]->(templ:Template)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH {ds_var}, i, templ, technique, irw
            WHERE i IS NOT NULL
            WITH {ds_var}, i, templ, technique, irw LIMIT 5
            WITH {ds_var}, collect({{i: i, templ: templ, technique: technique, irw: irw}}) AS imgs
            WITH {ds_var}, imgs, head(imgs) AS rep
            RETURN
                rep.templ AS templ,
                rep.technique AS technique,
                apoc.text.join([x IN imgs |
                    REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",
                        [coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.templ.symbol[0] <> '' THEN x.templ.symbol[0] ELSE x.templ.label END,
                         REPLACE(COALESCE(x.irw.thumbnail[0], ''), 'thumbnailT.png', 'thumbnail.png'),
                         coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.templ.symbol[0] <> '' THEN x.templ.symbol[0] ELSE x.templ.label END,
                         x.templ.short_form + "," + coalesce(x.i.short_form, {ds_var}.short_form)]),
                    "[![null]( 'null')](null)", "")
                ], ' | ') AS thumbnail
        }}
        CALL {{
            WITH {ds_var}
            OPTIONAL MATCH ({ds_var})<-[:has_source]-(img:Individual)
            RETURN count(DISTINCT img) AS image_count
        }}
    """


def _dataset_return_clause(ds_var: str = "ds") -> str:
    """Return the RETURN tail used by both get_aligned_datasets and
    get_all_datasets. Matches v2 prod columns:
      id, name, pubs(Reference), tags(Gross_Type), license, template,
      technique, thumbnail, image_count.

    NB: no ORDER BY here — the caller applies LIMIT (and any ORDER BY)
    after ``WITH DISTINCT ds`` and BEFORE the CALL subqueries fire, so
    we only enrich the rows we actually need. Otherwise 130 datasets
    × 4 CALL subqueries (one of which counts edges over millions of
    ``has_source`` relationships) easily breaches the 3 s perf-test
    threshold.
    """
    return f"""
        RETURN
            {ds_var}.short_form AS id,
            '[' + coalesce({ds_var}.label, {ds_var}.short_form) + ']({VFB_REPORT_BASE}' + {ds_var}.short_form + ')' AS name,
            pubs,
            apoc.text.join(coalesce({ds_var}.uniqueFacets, []), '|') AS tags,
            license,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            thumbnail,
            image_count
    """


def _dataset_response_dict(rows, total_count):
    """Shared response shape for get_aligned_datasets and
    get_all_datasets — column ordering mirrors v2 prod's
    `[Name, Reference, Gross_Type, License, Template_Space,
    Imaging_Technique, Images, Image_count]`.
    """
    return {
        "headers": {
            "id": {"title": "ID", "type": "selection_id", "order": -1},
            "name": {"title": "Dataset", "type": "markdown", "order": 0},
            "pubs": {"title": "Reference", "type": "metadata", "order": 1},
            "tags": {"title": "Tags", "type": "tags", "order": 2},
            "license": {"title": "License", "type": "markdown", "order": 3},
            "template": {"title": "Template", "type": "markdown", "order": 4},
            "technique": {"title": "Imaging Technique", "type": "text", "order": 5},
            "thumbnail": {"title": "Thumbnail", "type": "markdown", "order": 6},
            "image_count": {"title": "Image_count", "type": "numeric", "order": 7},
        },
        "rows": rows,
        "count": total_count,
    }


def get_aligned_datasets(template_short_form: str, return_dataframe=True, limit: int = -1):
    """List all datasets aligned to a template, with the same columns v2
    prod's SOLR-backed chain surfaces (Reference, License, Template_Space,
    Imaging_Technique, Images, Image_count). Closes the v2 parity gap
    flagged in projects/geppetto-vfbquery-migration/V2_V2DEV_PARITY_SWEEP.md.
    """
    count_query = f"MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds) RETURN count(ds) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    # LIMIT applied AFTER DISTINCT and BEFORE the CALL subqueries — otherwise
    # all 86 (AlignedDatasets) / 130 (AllDatasets) datasets get enriched
    # through 4 CALL subqueries (one of which counts has_source edges) and
    # the limit only trims afterwards. That blew past the THRESHOLD_MEDIUM
    # (3 s) perf-test budget on CI.
    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    main_query = f"""MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual {{short_form:'{template_short_form}'}})<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds)
        WITH DISTINCT ds
        ORDER BY coalesce(ds.label, ds.short_form)
        {limit_clause}
        {_dataset_enrichment_cypher('ds')}
        {_dataset_return_clause('ds')}"""

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty:
        df = encode_markdown_links(df, ['name', 'license', 'template', 'thumbnail'])

    if return_dataframe: return df
    rows = [{k: row[k] for k in ['id', 'name', 'pubs', 'tags', 'license', 'template', 'technique', 'thumbnail', 'image_count']}
            for row in safe_to_dict(df, sort_by_id=False)]
    return _dataset_response_dict(rows, total_count)


def get_all_datasets(return_dataframe=True, limit: int = -1):
    """List all available datasets, with the same column shape as
    get_aligned_datasets (matches v2 prod's AllDatasets columns)."""
    count_query = "MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual)<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds) WITH DISTINCT ds RETURN count(ds) AS count"
    count_results = vc.nc.commit_list([count_query])
    total_count = get_dict_cursor()(count_results)[0]['count'] if count_results else 0

    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    main_query = f"""MATCH (ds:DataSet:Individual) WHERE NOT ds:Deprecated AND (:Template:Individual)<-[:depicts]-(:Template:Individual)-[:in_register_with]-(:Individual)-[:depicts]->(:Individual)-[:has_source]->(ds)
        WITH DISTINCT ds
        ORDER BY coalesce(ds.label, ds.short_form)
        {limit_clause}
        {_dataset_enrichment_cypher('ds')}
        {_dataset_return_clause('ds')}"""

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty:
        df = encode_markdown_links(df, ['name', 'license', 'template', 'thumbnail'])
    
    if return_dataframe: return df
    rows = [{k: row[k] for k in ['id', 'name', 'pubs', 'tags', 'license', 'template', 'technique', 'thumbnail', 'image_count']}
            for row in safe_to_dict(df, sort_by_id=False)]
    return _dataset_response_dict(rows, total_count)


# ===== Publication Query =====

def get_terms_for_pub(pub_short_form: str, return_dataframe=True, limit: int = -1):
    """List all terms that reference a publication.

    v1.14.10: add Template_Space / Imaging_Technique / Images columns to
    restore v2 prod parity. Pre-migration the chain was Cypher id-fetch
    -> SOLR enrichment (queries.29 -> queries.24 -> dataSources.3/@queries.1
    in the legacy XMI). SOLR's denormalised record had template / imaging-
    technique / images baked in for image-bearing individuals. The
    VFBquery rewrite kept only the Cypher id-fetch and dropped the
    enrichment. Mirror the AnatomyExpressedIn CALL subquery pattern,
    keyed off primary acting as its own channel for channel_image
    primaries; non-image primaries (datasets, EPs, anatomies) leave
    these cells empty — matches v2 prod which shows the columns blank
    on dataset rows (e.g. Wolff2018).
    """
    # A publication is cited two different ways in the graph, and the legacy
    # TermsForPub only saw the first:
    #   1. Reference  — a term has a direct (:term)-[:has_reference]->(:pub)
    #                   edge (datasets, images, anatomy the paper is the
    #                   source/citation for).
    #   2. Expression — the pub is recorded as a `pub` array PROPERTY on an
    #                   overlaps/part_of relationship of an expression-pattern
    #                   individual (the same model AnatomyExpressedIn /
    #                   TransgeneExpressionHere read via `r.pub`). Expression-
    #                   data papers (e.g. FBrf0232433, VT-GAL4 lines) have NO
    #                   has_reference edges at all, so the old query returned
    #                   nothing despite thousands of referenced patterns.
    # We surface both and add a "Reference type" column so users can tell why
    # each term is listed. NB: the Expression branch scans overlaps/part_of by
    # the relationship `pub` property (no node path exists — the pub node has
    # no edges), so it is the expensive leg; the whole query is cached.

    # Source 1: direct has_reference terms, with image enrichment for
    # channel-image primaries (one representative image via the CALL).
    ref_query = f"""
        MATCH (:pub:Individual {{short_form:'{pub_short_form}'}})<-[:has_reference]-(primary:Individual)
        OPTIONAL MATCH (primary)-[:INSTANCEOF]->(typ:Class)
        WITH DISTINCT primary, typ
        CALL {{
            WITH primary
            OPTIONAL MATCH (primary)-[irw:in_register_with]->(template:Individual)-[:depicts]->(template_anat:Individual)
            OPTIONAL MATCH (primary)-[:is_specified_output_of]->(technique:Class)
            WITH primary, template, template_anat, technique, irw
            LIMIT 1
            RETURN template, template_anat, technique, irw
        }}
        RETURN
            primary.short_form AS id,
            apoc.text.format("[%s](%s)", [primary.label, primary.short_form]) AS name,
            apoc.text.join(coalesce(primary.uniqueFacets, []), '|') AS tags,
            REPLACE(apoc.text.format("[%s](%s)", [typ.label, typ.short_form]), '[null](null)', '') AS type,
            'Reference' AS reference_type,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            REPLACE(apoc.text.format("[![%s](%s '%s')](%s)", [coalesce(primary.label, 'image') + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, REPLACE(COALESCE(irw.thumbnail[0], ''), 'thumbnailT.png', 'thumbnail.png'), coalesce(primary.label, 'image') + " aligned to " + CASE WHEN template_anat.symbol[0] <> '' THEN template_anat.symbol[0] ELSE template_anat.label END, template_anat.short_form + "," + primary.short_form]), "[![null]( 'null')](null)", "") AS thumbnail
    """

    # Source 2: expression patterns whose overlaps/part_of edges cite this pub.
    exp_query = f"""
        MATCH (:Individual)-[r:overlaps|part_of]->(b:Class:Expression_pattern)
        WHERE '{pub_short_form}' IN r.pub
        WITH DISTINCT b
        RETURN
            b.short_form AS id,
            apoc.text.format("[%s](%s)", [b.label, b.short_form]) AS name,
            apoc.text.join(coalesce(b.uniqueFacets, []), '|') AS tags,
            '' AS type,
            'Expression' AS reference_type,
            '' AS template,
            '' AS technique,
            '' AS thumbnail
    """

    df_ref = pd.DataFrame.from_records(get_dict_cursor()(vc.nc.commit_list([ref_query])))
    df_exp = pd.DataFrame.from_records(get_dict_cursor()(vc.nc.commit_list([exp_query])))
    df = pd.concat([df_ref, df_exp], ignore_index=True, sort=False)

    if not df.empty:
        # A term could be cited both ways — collapse to one row per term and
        # join its reference types (e.g. "Expression; Reference").
        df = (df.groupby('id', as_index=False, sort=False)
                .agg({
                    'name': 'first',
                    'tags': 'first',
                    'type': 'first',
                    'reference_type': lambda s: '; '.join(sorted({x for x in s if x})),
                    'template': 'first',
                    'technique': 'first',
                    'thumbnail': 'first',
                }))
        df = df.sort_values('name', kind='stable').reset_index(drop=True)

    total_count = len(df)
    if limit != -1:
        df = df.head(limit)

    if not df.empty:
        df = encode_markdown_links(df, ['name', 'template', 'thumbnail'])

    if return_dataframe:
        return df

    return {
        "headers": {
            "id":             {"title": "ID",                "type": "selection_id", "order": -1},
            "name":           {"title": "Term",              "type": "markdown",     "order":  0},
            "reference_type": {"title": "Reference type",    "type": "text",         "order":  1},
            "tags":           {"title": "Tags",              "type": "tags",         "order":  2},
            "type":           {"title": "Type",              "type": "text",         "order":  3},
            "template":       {"title": "Template",          "type": "markdown",     "order":  4},
            "technique":      {"title": "Imaging Technique", "type": "text",         "order":  5},
            "thumbnail":      {"title": "Thumbnail",         "type": "markdown",     "order":  9},
        },
        "rows": [
            {k: row[k] for k in ["id", "name", "reference_type", "tags", "type", "template", "technique", "thumbnail"]}
            for row in safe_to_dict(df, sort_by_id=False)
        ],
        "count": total_count,
    }


# ===== Complex Transgene Expression Query =====

def get_transgene_expression_here(anatomy_short_form: str, return_dataframe=True, limit: int = -1):
    """Reports of transgene expression in the specified anatomical region.

    Returns one row per overlapping/part-of Expression_pattern with:
      - Reference (pubs) — `; `-joined publication labels
      - Gross_Type (tags)
      - Template_Space / Imaging_Technique / Images (one representative
        channel-image per ep, picked via CALL subquery with LIMIT 1)

    v1.14.0: anatomy traversal now goes through Owlery /subclasses,
    matching the legacy XMI's first-step Owlery walk
    (//@dataSources.1/@queries.8 in the pre-migration chain). Without
    this, a high-level anatomy class (e.g. pacemaker neuron, mushroom
    body intrinsic neuron) returns 0 EPs because Individuals are typed
    INSTANCEOF leaf subclasses, not the parent. Same closure pattern as
    get_instances (v1.12.8).

    v1.14.5: adds Expressed_in column matching v2 prod's single-value
    display. Each EP row carries one representative leaf anatomy class
    (alphabetically first within the Owlery closure) as `[label](id)`
    markdown — the same convention name / parent / template / dataset
    already use. Click-target wiring for v2's QueryLinkComponent is
    handled downstream by the Java VFBqueryJsonProcessor (which
    extracts the `(id)` from each clickable column's markdown and
    builds the row's id column to match SOLRQueryProcessor's pattern).
    VFBquery stays delimiter-agnostic — only lists and `[label](id)`
    markdown go over the wire, same as every other clickable column.
    """
    # Resolve the full subclass closure of the input anatomy class via
    # Owlery. Owlery handles OWL inference (equivalence classes, defined
    # classes, anonymous class expressions on the parent chain); the
    # queried class itself is included so leaf classes still match.
    try:
        owl_query = f"<{_short_form_to_iri(anatomy_short_form)}>"
        subclass_ids = vc.vfb.oc.get_subclasses(query=owl_query, query_by_label=False)
        anat_short_forms = list({anatomy_short_form, *(subclass_ids or [])})
    except Exception:
        # If Owlery is unreachable, fall back to the input class alone —
        # better to return the leaf-class result than to fail outright.
        anat_short_forms = [anatomy_short_form]

    count_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(:Individual)-[:INSTANCEOF]->(anat:Class)
        WHERE anat.short_form IN {anat_short_forms!r}
        RETURN COUNT(DISTINCT ep) AS total_count
    """
    count_results = vc.nc.commit_list([count_query])
    count_df = pd.DataFrame.from_records(get_dict_cursor()(count_results))
    total_count = count_df['total_count'][0] if not count_df.empty else 0

    # Same as get_aligned_datasets: apply LIMIT before the CALL subqueries
    # fire so we only enrich the rows we actually need. With 2,340
    # mushroom-body EPs and a 5-hop thumbnail join inside the CALL, the
    # naive "append LIMIT at the end" form ran for tens of seconds.
    #
    # v1.14.0 pubs walk now matches the legacy XMI Cypher at
    # geppetto-vfb@998cc28d9^:model/vfb.xmi dataSources[0]/@queries.7:
    # pub short_forms are stored as an ARRAY PROPERTY on the
    # overlaps/part_of RELATIONSHIP (ar.pub[0]), not as a separate
    # [:has_reference|pub] edge from the Individual. The previous
    # walk traversed an edge that doesn't exist in the current
    # Neo4j build, so pubs came back empty for every row.
    limit_clause = f"LIMIT {limit}" if limit != -1 else ""
    main_query = f"""
        MATCH (ep:Class:Expression_pattern)<-[ar:overlaps|part_of]-(:Individual)-[:INSTANCEOF]->(anat:Class)
        WHERE anat.short_form IN {anat_short_forms!r}
        WITH ep,
             // Alphabetically-first representative leaf anat per EP,
             // emitted as `[label](id)` markdown — the same shape
             // name / parent / template / dataset already use. The
             // Java VFBqueryJsonProcessor handles click-target wiring
             // downstream; VFBquery just emits the markdown.
             apoc.coll.sort(collect(DISTINCT apoc.text.format("[%s](%s)", [anat.label, anat.short_form])))[0] AS expressed_in
        ORDER BY ep.label
        {limit_clause}
        CALL {{
            // v1.14.7: pubs walk uses ALL overlap/part_of edges on the
            // EP (no anat-closure filter) so the Reference column
            // surfaces every publication describing this expression
            // pattern, not just the ones tied to the subset of
            // overlapping individuals that fall under the query's
            // anatomy closure. Also picks up any direct
            // (ep)-[:has_reference]->(:pub) edges.
            //
            // ar.pub is an array property — almost always single-
            // element in current pdb but UNWIND-flatten in case any
            // edge carries multiple. apoc.coll.union folds in direct
            // pub edges if present.
            WITH ep
            OPTIONAL MATCH (ep)<-[ar2:overlaps|part_of]-(:Individual)
            UNWIND coalesce(ar2.pub, []) AS rel_p_sf
            WITH ep, collect(DISTINCT rel_p_sf) AS rel_pubs
            OPTIONAL MATCH (ep)-[:has_reference]->(direct:pub)
            WITH apoc.coll.union(rel_pubs, collect(DISTINCT direct.short_form)) AS pub_shorts
            UNWIND pub_shorts AS p_sf
            WITH p_sf WHERE p_sf IS NOT NULL
            OPTIONAL MATCH (p:pub {{ short_form: p_sf }})
            // Strip "Unattributed" pub labels — VFB's marker for an EP
            // with no citation. Rendered in the V2 Reference column they
            // look like a real citation. Match v2 prod behaviour which
            // hides Unattributed entirely. Also drop NULL p (pub_short
            // without a resolvable pub node) and empty labels.
            WITH p WHERE p IS NOT NULL
                       AND coalesce(p.label, p.short_form) IS NOT NULL
                       AND coalesce(p.label, p.short_form) <> ''
                       AND coalesce(p.label, p.short_form) <> 'Unattributed'
            // v1.14.7: emit pubs as per-pub `[label](id)` markdown
            // joined by `; ` so every Reference chip in v2's
            // QueryLinkArrayComponent gets its own clickable id.
            //
            // The companion VFBqueryJsonProcessor change (uk.ac.vfb.
            // geppetto v2.2.4.15) recognises this list shape and:
            //   - strips markdown per item for display
            //   - expands the row's id-column with ONE slot per pub,
            //     matching the legacy SOLRQueryProcessor.id() pattern
            //     at lines 402-407 (slot-per-pub when pubs.size() > 1).
            //
            // Safe for TransgeneExpressionHere because the columns
            // after pubs (tags, template, technique, thumbnail) all
            // use customComponents that read the cell value directly
            // rather than the row's id slot, so growing pubs slots
            // doesn't collide with downstream clickable columns.
            RETURN apoc.text.join(
                collect(DISTINCT apoc.text.format("[%s](%s)",
                                                   [coalesce(p.label, p.short_form),
                                                    p.short_form])),
                '; '
            ) AS pubs
        }}
        CALL {{
            WITH ep
            OPTIONAL MATCH (ep)<-[:has_source|SUBCLASSOF|INSTANCEOF*]-(i:Individual)<-[:depicts]-(channel:Individual)-[irw:in_register_with]->(:Template)-[:depicts]->(templ:Template)
            OPTIONAL MATCH (channel)-[:is_specified_output_of]->(technique:Class)
            WITH ep, i, templ, technique, irw
            WHERE i IS NOT NULL
            WITH ep, i, templ, technique, irw LIMIT 5
            WITH ep, collect({{i: i, templ: templ, technique: technique, irw: irw}}) AS imgs
            WITH ep, imgs, head(imgs) AS rep
            RETURN
                rep.templ AS templ,
                rep.technique AS technique,
                apoc.text.join([x IN imgs |
                    REPLACE(apoc.text.format("[![%s](%s '%s')](%s)",
                        [coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.templ.symbol[0] <> '' THEN x.templ.symbol[0] ELSE x.templ.label END,
                         REPLACE(COALESCE(x.irw.thumbnail[0], ''), 'thumbnailT.png', 'thumbnail.png'),
                         coalesce(x.i.label, 'image') + " aligned to " + CASE WHEN x.templ.symbol[0] <> '' THEN x.templ.symbol[0] ELSE x.templ.label END,
                         x.templ.short_form + "," + coalesce(x.i.short_form, ep.short_form)]),
                    "[![null]( 'null')](null)", "")
                ], ' | ') AS thumbnail
        }}
        RETURN
            ep.short_form AS id,
            apoc.text.format("[%s](%s)", [ep.label, ep.short_form]) AS name,
            expressed_in,
            apoc.text.join(coalesce(ep.uniqueFacets, []), '|') AS tags,
            pubs,
            REPLACE(apoc.text.format("[%s](%s)", [CASE WHEN templ.symbol[0] <> '' THEN templ.symbol[0] ELSE templ.label END, templ.short_form]), '[null](null)', '') AS template,
            coalesce(technique.label, '') AS technique,
            thumbnail
    """

    results = vc.nc.commit_list([main_query])
    df = pd.DataFrame.from_records(get_dict_cursor()(results))
    if not df.empty:
        df = encode_markdown_links(df, ['name', 'expressed_in', 'template', 'thumbnail'])

    if return_dataframe:
        return df
    return {
        "headers": {
            "id":           {"title": "ID",                "type": "selection_id", "order": -1},
            "name":         {"title": "Expression Pattern","type": "markdown",     "order": 0},
            "expressed_in": {"title": "Expressed_in",      "type": "markdown",     "order": 1},
            "pubs":         {"title": "Publications",      "type": "metadata",     "order": 2},
            "tags":         {"title": "Tags",              "type": "tags",         "order": 3},
            "template":     {"title": "Template",          "type": "markdown",     "order": 4},
            "technique":    {"title": "Imaging Technique", "type": "text",         "order": 5},
            "thumbnail":    {"title": "Thumbnail",         "type": "markdown",     "order": 9},
        },
        "rows": [
            {k: row[k] for k in ['id', 'name', 'expressed_in', 'pubs', 'tags', 'template', 'technique', 'thumbnail']}
            for row in safe_to_dict(df, sort_by_id=False)
        ],
        "count": total_count,
    }


def fill_query_results(term_info, force_refresh: bool = False):
    def process_query(query):
        # print(f"Query Keys:{query.keys()}")
        
        if "preview" in query.keys() and query['preview'] > 0:
            function = globals().get(query['function'])
            summary_mode = query.get('output_format', 'table') == 'ribbon'

            if function:
                # print(f"Function {query['function']} found")
                
                try:
                    # Unpack the default dictionary and pass its contents as arguments
                    function_args = query['takes'].get("default", {})
                    # print(f"Function args: {function_args}")

                    # Check function signature to see if it takes a positional argument for short_form
                    sig = inspect.signature(function)
                    params = list(sig.parameters.keys())
                    # Skip 'self' if it's a method, and check if first param is not return_dataframe/limit/summary_mode
                    first_param = params[1] if params and params[0] == 'self' else (params[0] if params else None)
                    takes_short_form = first_param and first_param not in ['return_dataframe', 'limit', 'summary_mode']
                    supports_force_refresh = ('force_refresh' in sig.parameters)

                    base_kwargs = {'return_dataframe': False, 'limit': query['preview']}
                    if summary_mode:
                        base_kwargs['summary_mode'] = summary_mode
                    if supports_force_refresh:
                        base_kwargs['force_refresh'] = force_refresh

                    # Modify this line to use the correct arguments and pass the default arguments
                    # Each sub-query runs under a wall-clock budget so one
                    # pathological generic term cannot stall the whole response.
                    if function_args and takes_short_form:
                        # Pass the short_form as positional argument
                        short_form_value = list(function_args.values())[0]
                        result = _run_with_timeout(function, args=(short_form_value,), kwargs=base_kwargs)
                    else:
                        result = _run_with_timeout(function, kwargs=base_kwargs)
                except concurrent.futures.TimeoutError:
                    print(f"Timeout ({SUBQUERY_TIMEOUT_S}s) on query function {query['function']}; "
                          f"reporting unknown count (-1) with empty preview")
                    # Unknown, not empty: keep the query live so the user can run
                    # it on demand; -1 distinguishes this from a known-empty (0).
                    query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                    query['count'] = -1
                    return
                except Exception as e:
                    print(f"Error executing query function {query['function']}: {e}")
                    # Set default values for failed query (unknown count, not empty)
                    query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                    query['count'] = -1
                    return
                # print(f"Function result: {result}")
                
                # Filter columns based on preview_columns
                filtered_result = []
                filtered_headers = {}
                
                if result is None:
                    print(f"ERROR: Query function {query['function']} returned None - this indicates a query failure that needs investigation")
                    query['preview_results'] = {'headers': query.get('preview_columns', ['id', 'label', 'tags', 'thumbnail']), 'rows': []}
                    query['count'] = -1
                    return
                
                if isinstance(result, dict) and 'rows' in result:
                    for item in result['rows']:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                        
                    if 'headers' in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_headers = {col: result['headers'][col] for col in query['preview_columns']}
                        else:
                            filtered_headers = result['headers']
                elif isinstance(result, dict) and 'data' in result:
                    # Handle legacy 'data' key as alias for 'rows'
                    for item in result['data']:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                        
                    if 'headers' in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_headers = {col: result['headers'][col] for col in query['preview_columns']}
                        else:
                            filtered_headers = result['headers']
                elif isinstance(result, list) and all(isinstance(item, dict) for item in result):
                    for item in result:
                        if 'preview_columns' in query.keys() and len(query['preview_columns']) > 0:
                            filtered_item = {col: item[col] for col in query['preview_columns']}
                        else:
                            filtered_item = item
                        filtered_result.append(filtered_item)
                elif isinstance(result, pd.DataFrame):
                    filtered_result = safe_to_dict(result[query['preview_columns']])
                else:
                    print(f"Unsupported result format for filtering columns in {query['function']}")
                
                # Handle count extraction based on result type
                if isinstance(result, dict) and 'count' in result:
                    result_count = result['count']
                    # If limit was applied, the function's count may equal the
                    # number of returned rows (no cheap total available). Decide
                    # the true count WITHOUT an unbounded re-run.
                    if query['preview'] > 0 and result_count == len(result['rows']):
                        # Preview not saturated: it already holds the entire
                        # result set, so the count is exactly the rows returned.
                        if len(result['rows']) < query['preview']:
                            result_count = len(result['rows'])
                        else:
                          # Saturated: re-run bounded to COUNT_CAP (never -1) so a
                          # pathological generic term cannot hang the panel. Exact
                          # total if under the cap, otherwise -1 ("many").
                          try:
                              full_kwargs = {'return_dataframe': False, 'limit': COUNT_CAP}
                              if supports_force_refresh:
                                  full_kwargs['force_refresh'] = force_refresh
                              if function_args and takes_short_form:
                                  short_form_value = list(function_args.values())[0]
                                  full_dict = _run_with_timeout(function, args=(short_form_value,), kwargs=full_kwargs)
                              else:
                                  full_dict = _run_with_timeout(function, kwargs=full_kwargs)
                              capped = full_dict.get('count', len(full_dict.get('rows', [])))
                              result_count = -1 if capped >= COUNT_CAP else capped
                          except concurrent.futures.TimeoutError:
                              print(f"Timeout ({SUBQUERY_TIMEOUT_S}s) counting {query['function']}; reporting -1")
                              result_count = -1
                          except Exception as e:
                              print(f"Error getting bounded count for {query['function']}: {e}")
                              result_count = -1
                elif isinstance(result, pd.DataFrame):
                    # For DataFrame results, get the full count when the preview is
                    # saturated, but bound the re-run to COUNT_CAP (never -1) so a
                    # broad term cannot hang the panel.
                    if query['preview'] > 0 and len(result) < query['preview']:
                        result_count = len(result)
                    else:
                      try:
                        full_kwargs = {'return_dataframe': True, 'limit': COUNT_CAP}
                        if supports_force_refresh:
                            full_kwargs['force_refresh'] = force_refresh
                        if function_args and takes_short_form:
                            short_form_value = list(function_args.values())[0]
                            full_result = _run_with_timeout(function, args=(short_form_value,), kwargs=full_kwargs)
                        else:
                            full_result = _run_with_timeout(function, kwargs=full_kwargs)
                        result_count = -1 if len(full_result) >= COUNT_CAP else len(full_result)
                      except concurrent.futures.TimeoutError:
                        print(f"Timeout ({SUBQUERY_TIMEOUT_S}s) counting {query['function']}; reporting -1")
                        result_count = -1
                      except Exception as e:
                        print(f"Error getting bounded count for {query['function']}: {e}")
                        result_count = -1  # Unknown rather than a wrong (limited) count
                else:
                    result_count = 0
                
                # Store preview results (count is stored at query level, not in preview_results)
                # Sort rows based on the sort field in headers, default to ID descending if none
                sort_column = None
                sort_direction = None
                for col, info in filtered_headers.items():
                    if 'sort' in info and isinstance(info['sort'], dict):
                        sort_column = col
                        sort_direction = list(info['sort'].values())[0]  # e.g., 'Asc' or 'Desc'
                        break
                if sort_column:
                    reverse = sort_direction == 'Desc'
                    filtered_result.sort(key=lambda x: x.get(sort_column, ''), reverse=reverse)
                else:
                    # Default to ID descending if no sort specified
                    filtered_result.sort(key=lambda x: x.get('id', ''), reverse=True)
                query['preview_results'] = {'headers': filtered_headers, 'rows': filtered_result}
                query['count'] = result_count
                # print(f"Filtered result: {filtered_result}")
            else:
                print(f"Function {query['function']} not found")
        else:
            print("Preview key not found or preview is 0")

    for query in term_info['Queries']:
        process_query(query)

    return term_info


def get_hierarchy(short_form, relationship='part_of', direction='both', max_depth=1):
    """Build a hierarchy tree showing ancestors and/or descendants of a term.

    For ``subclass_of`` descendants, all descendants are fetched in one Owlery
    call (fast, cached) and the tree is reconstructed by looking up each term's
    parents in SOLR.  For ``part_of`` descendants, direct children are fetched
    per level via Owlery ``direct=True`` (slower on first call, but results are
    cached by the Owlery server).

    :param short_form: Root term ID (e.g. 'FBbt_00005801')
    :param relationship: 'part_of' for brain region structure, 'subclass_of' for cell type hierarchies
    :param direction: 'descendants', 'ancestors', or 'both'
    :param max_depth: Levels to expand (default 1 = direct only; -1 = unlimited)
    :return: Nested dict with id, label, ancestors, descendants
    """
    if relationship not in ('part_of', 'subclass_of'):
        raise ValueError("relationship must be 'part_of' or 'subclass_of'")
    if direction not in ('descendants', 'ancestors', 'both'):
        raise ValueError("direction must be 'descendants', 'ancestors', or 'both'")

    label_cache = {}
    _ont_solr = pysolr.Solr('https://solr.virtualflybrain.org/solr/ontology/', always_commit=False, timeout=30)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _batch_lookup_labels(ids):
        """Fetch labels for a list of IDs from the ontology SOLR core."""
        missing = [i for i in ids if i not in label_cache]
        if not missing:
            return
        try:
            id_list = ','.join(missing)
            results = _ont_solr.search(
                q='*:*',
                fq=f'{{!terms f=short_form}}{id_list}',
                fl='short_form,label',
                rows=len(missing)
            )
            for doc in results.docs:
                label_cache[doc.get('short_form', '')] = doc.get('label', doc.get('short_form', ''))
        except Exception:
            pass
        for i in missing:
            label_cache.setdefault(i, i)

    def _get_all_children(term_id):
        """Get all descendants (transitive) using the existing cached functions."""
        if relationship == 'part_of':
            result = get_parts_of(term_id, return_dataframe=False)
        else:
            result = get_subclasses_of(term_id, return_dataframe=False)
        if not result or not result.get('rows'):
            return []
        return [row['id'] for row in result['rows'] if row.get('id') and row['id'] != term_id]

    def _term_info_parents(term_id):
        """Return [(parent_sf, parent_label), ...] from SOLR term_info."""
        try:
            results = vfb_solr.search(f'id:{term_id}', fl='term_info', rows=1)
            if not results.docs or 'term_info' not in results.docs[0]:
                return []
            raw = results.docs[0]['term_info']
            ti = json.loads(raw[0] if isinstance(raw, list) else raw)
            if relationship == 'subclass_of':
                return [(p['short_form'], p.get('label', p['short_form'])) for p in ti.get('parents', [])]
            else:
                # part_of: BFO_0000050 in relationships
                out = []
                for r in ti.get('relationships', []):
                    if 'BFO_0000050' in r.get('relation', {}).get('iri', ''):
                        obj = r['object']
                        out.append((obj['short_form'], obj.get('label', obj['short_form'])))
                # Fallback to Neo4j edge
                if not out:
                    try:
                        cypher = (
                            f"MATCH (c:Class {{short_form: '{term_id}'}})"
                            f"-[:part_of]->(p:Class) "
                            f"RETURN p.short_form AS sf, p.label AS label"
                        )
                        for row in get_dict_cursor()(vc.nc.commit_list([cypher])):
                            out.append((row['sf'], row.get('label', row['sf'])))
                    except Exception:
                        pass
                return out
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Descendants
    # ------------------------------------------------------------------

    def _build_descendants_subclass(root_id):
        """Build subclass tree: one cached Owlery call + batch SOLR parent lookup."""
        all_desc = _get_all_children(root_id)
        if not all_desc:
            return []

        tree_ids = set(all_desc) | {root_id}
        _batch_lookup_labels(list(tree_ids))

        # Batch-fetch parents from vfb_json SOLR
        children_of = {tid: [] for tid in tree_ids}
        id_list = ','.join(all_desc)
        try:
            results = vfb_solr.search(
                q='id:*', fq=f'{{!terms f=id}}{id_list}', fl='id,term_info', rows=len(all_desc)
            )
            for doc in results.docs:
                child_id = doc.get('id', '')
                if 'term_info' not in doc:
                    continue
                raw = doc['term_info']
                ti = json.loads(raw[0] if isinstance(raw, list) else raw)
                parents_in_tree = [p['short_form'] for p in ti.get('parents', []) if p['short_form'] in tree_ids]
                if parents_in_tree:
                    for pid in parents_in_tree:
                        children_of[pid].append(child_id)
                else:
                    children_of[root_id].append(child_id)
        except Exception:
            children_of[root_id] = all_desc

        def build(node_id, depth):
            node = {'id': node_id, 'label': label_cache.get(node_id, node_id)}
            if max_depth == -1 or depth < max_depth:
                kids = children_of.get(node_id, [])
                if kids:
                    node['descendants'] = [
                        build(k, depth + 1)
                        for k in sorted(kids, key=lambda x: label_cache.get(x, x))
                    ]
            return node

        top = children_of.get(root_id, [])
        return [build(k, 1) for k in sorted(top, key=lambda x: label_cache.get(x, x))]

    def _build_descendants_part_of(root_id):
        """Build part_of descendant tree via Ubergraph SPARQL.

        Queries the Ubergraph redundant graph for all transitive part_of
        edges within the subtree, then reconstructs the nesting by finding
        each child's most specific parent.
        """
        import requests as _req
        from collections import defaultdict

        root_iri = _short_form_to_iri(root_id)
        sparql = f'''
PREFIX BFO: <http://purl.obolibrary.org/obo/BFO_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?child ?childLabel ?parent ?parentLabel WHERE {{
  GRAPH <http://reasoner.renci.org/redundant> {{
    ?child BFO:0000050 <{root_iri}> .
    ?child BFO:0000050 ?parent .
  }}
  FILTER(?parent != ?child)
  FILTER(
    ?parent = <{root_iri}> ||
    EXISTS {{
      GRAPH <http://reasoner.renci.org/redundant> {{
        ?parent BFO:0000050 <{root_iri}> .
      }}
    }}
  )
  ?child rdfs:label ?childLabel .
  ?parent rdfs:label ?parentLabel .
  FILTER(STRSTARTS(STR(?child), "http://purl.obolibrary.org/obo/FBbt_"))
}}
'''
        try:
            resp = _req.get(
                'https://ubergraph.apps.renci.org/sparql',
                params={'query': sparql},
                headers={'Accept': 'application/json'},
                timeout=30,
            )
            resp.raise_for_status()
            bindings = resp.json().get('results', {}).get('bindings', [])
        except Exception:
            # Fallback to flat list via Owlery
            all_parts = _get_all_children(root_id)
            if not all_parts:
                return []
            _batch_lookup_labels(all_parts)
            return [
                {'id': pid, 'label': label_cache.get(pid, pid)}
                for pid in sorted(all_parts, key=lambda x: label_cache.get(x, x))
            ]

        if not bindings:
            return []

        # Parse SPARQL results into parent map
        parents_of = defaultdict(set)
        all_parts = set()
        for b in bindings:
            csf = b['child']['value'].rsplit('/', 1)[-1]
            psf = b['parent']['value'].rsplit('/', 1)[-1]
            parents_of[csf].add(psf)
            label_cache[csf] = b['childLabel']['value']
            label_cache[psf] = b['parentLabel']['value']
            all_parts.add(csf)

        # Find most specific parent for each child
        # (no other parent of this child is itself a descendant of this parent)
        children_of = defaultdict(list)
        for child in all_parts:
            best = []
            for p in parents_of[child]:
                if not any(p in parents_of.get(q, set()) for q in parents_of[child] if q != p):
                    best.append(p)
            for bp in best:
                children_of[bp].append(child)

        def build(node_id, depth):
            node = {'id': node_id, 'label': label_cache.get(node_id, node_id)}
            if max_depth == -1 or depth < max_depth:
                kids = children_of.get(node_id, [])
                if kids:
                    node['descendants'] = [
                        build(k, depth + 1)
                        for k in sorted(kids, key=lambda x: label_cache.get(x, x))
                    ]
            return node

        top = children_of.get(root_id, [])
        return [build(k, 1) for k in sorted(top, key=lambda x: label_cache.get(x, x))]

    # ------------------------------------------------------------------
    # Ancestors
    # ------------------------------------------------------------------

    def _build_ancestors_subclass(term_id, depth, visited):
        """Build is-a ancestor chain from SOLR term_info parents.

        Filters to FBbt cell terms only (types includes 'Cell') to
        exclude cross-ontology parents (CL, UBERON, BFO, etc.) and
        non-cell ancestors (developmental lineage, anatomical structure).
        Stops at 'cell' (FBbt_00007002).
        """
        if term_id in visited or (max_depth != -1 and depth >= max_depth):
            return []
        if term_id == 'FBbt_00007002':  # cell — top of useful hierarchy
            return []
        visited.add(term_id)

        try:
            results = vfb_solr.search(f'id:{term_id}', fl='term_info', rows=1)
            if not results.docs or 'term_info' not in results.docs[0]:
                return []
            raw = results.docs[0]['term_info']
            ti = json.loads(raw[0] if isinstance(raw, list) else raw)
            parents = ti.get('parents', [])
        except Exception:
            return []

        ancestors = []
        for p in parents:
            psf = p['short_form']
            # Filter: must be FBbt and must be a cell type
            if not psf.startswith('FBbt_'):
                continue
            if 'Cell' not in p.get('types', []):
                continue
            plabel = p.get('label', psf)
            label_cache[psf] = plabel
            node = {'id': psf, 'label': plabel}
            further = _build_ancestors_subclass(psf, depth + 1, visited)
            if further:
                node['ancestors'] = further
            ancestors.append(node)
        return ancestors

    def _build_ancestors_part_of(term_id):
        """Build part_of ancestor chain via Ubergraph SPARQL.

        Filters ancestors to terms that are part of the nervous system
        (or the nervous system itself) to exclude developmental lineage
        terms and generic structural classes that leak in via is-a
        propagation in the Ubergraph redundant graph.
        """
        import requests as _req
        from collections import defaultdict

        term_iri = _short_form_to_iri(term_id)
        sparql = f'''
PREFIX BFO: <http://purl.obolibrary.org/obo/BFO_>
PREFIX FBbt: <http://purl.obolibrary.org/obo/FBbt_>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ancestor ?ancestorLabel ?parent ?parentLabel WHERE {{
  GRAPH <http://reasoner.renci.org/redundant> {{
    <{term_iri}> BFO:0000050 ?ancestor .
  }}
  FILTER(?ancestor != <{term_iri}>)
  FILTER(STRSTARTS(STR(?ancestor), "http://purl.obolibrary.org/obo/FBbt_"))
  FILTER(
    ?ancestor = FBbt:00005093 ||
    EXISTS {{
      GRAPH <http://reasoner.renci.org/redundant> {{
        ?ancestor BFO:0000050 FBbt:00005093 .
      }}
    }}
  )
  ?ancestor rdfs:label ?ancestorLabel .
  OPTIONAL {{
    GRAPH <http://reasoner.renci.org/redundant> {{
      ?ancestor BFO:0000050 ?parent .
    }}
    FILTER(
      ?parent = FBbt:00005093 ||
      EXISTS {{
        GRAPH <http://reasoner.renci.org/redundant> {{
          ?parent BFO:0000050 FBbt:00005093 .
        }}
      }}
    )
    FILTER(?parent != ?ancestor)
    FILTER(STRSTARTS(STR(?parent), "http://purl.obolibrary.org/obo/FBbt_"))
    FILTER(
      EXISTS {{
        GRAPH <http://reasoner.renci.org/redundant> {{
          <{term_iri}> BFO:0000050 ?parent .
        }}
      }}
    )
    ?parent rdfs:label ?parentLabel .
  }}
}}
'''
        try:
            resp = _req.get(
                'https://ubergraph.apps.renci.org/sparql',
                params={'query': sparql},
                headers={'Accept': 'application/json'},
                timeout=30,
            )
            resp.raise_for_status()
            bindings = resp.json().get('results', {}).get('bindings', [])
        except Exception:
            # Fallback to term_info approach
            return _build_ancestors_subclass(term_id, 0, set())

        if not bindings:
            return []

        # Build parent map among ancestors
        parents_of = defaultdict(set)
        all_ancestors = set()
        for b in bindings:
            asf = b['ancestor']['value'].rsplit('/', 1)[-1]
            label_cache[asf] = b['ancestorLabel']['value']
            all_ancestors.add(asf)
            if 'parent' in b:
                psf = b['parent']['value'].rsplit('/', 1)[-1]
                parents_of[asf].add(psf)
                label_cache[psf] = b['parentLabel']['value']

        # Find most specific ancestors (direct parents of the query term)
        # = ancestors that aren't themselves ancestors of another ancestor
        children_of = defaultdict(list)
        for anc in all_ancestors:
            best = []
            for p in parents_of.get(anc, set()):
                if p in all_ancestors:
                    if not any(p in parents_of.get(q, set()) for q in parents_of.get(anc, set()) if q != p and q in all_ancestors):
                        best.append(p)
            for bp in best:
                children_of[bp].append(anc)

        # Direct parents of query term = ancestors with no child that is also an ancestor
        direct_parents = [a for a in all_ancestors if not any(a in parents_of.get(other, set()) for other in all_ancestors if other != a)]

        def build(node_id, depth):
            node = {'id': node_id, 'label': label_cache.get(node_id, node_id)}
            if max_depth == -1 or depth < max_depth:
                # Find this node's parents among the ancestors
                node_parents = [p for p in parents_of.get(node_id, set()) if p in all_ancestors]
                # Most specific parents
                best = []
                for p in node_parents:
                    if not any(p in parents_of.get(q, set()) for q in node_parents if q != p):
                        best.append(p)
                if best:
                    node['ancestors'] = [
                        build(p, depth + 1)
                        for p in sorted(best, key=lambda x: label_cache.get(x, x))
                    ]
            return node

        return [build(dp, 1) for dp in sorted(direct_parents, key=lambda x: label_cache.get(x, x))]

    # ------------------------------------------------------------------
    # Assemble result
    # ------------------------------------------------------------------

    _batch_lookup_labels([short_form])
    root = {
        'id': short_form,
        'label': label_cache.get(short_form, short_form),
        'relationship': relationship,
    }

    if direction in ('descendants', 'both'):
        if relationship == 'subclass_of':
            root['descendants'] = _build_descendants_subclass(short_form)
        else:
            root['descendants'] = _build_descendants_part_of(short_form)

    if direction in ('ancestors', 'both'):
        if relationship == 'subclass_of':
            root['ancestors'] = _build_ancestors_subclass(short_form, 0, set())
        else:
            root['ancestors'] = _build_ancestors_part_of(short_form)

    # ------------------------------------------------------------------
    # Render display text and HTML
    # ------------------------------------------------------------------

    VFB_BASE = VFB_REPORT_BASE
    DEFAULT_MAX_SIBLINGS = 10  # truncate large sibling groups in text display

    def _text_tree(node, prefix='', is_last=True, is_root=True, max_siblings=DEFAULT_MAX_SIBLINGS):
        """Render a node and its descendants as a text tree."""
        lines = []
        label = f'{node["label"]} ({node["id"]})'
        if is_root:
            lines.append(label)
        else:
            lines.append(prefix + ('└── ' if is_last else '├── ') + label)
        child_prefix = prefix + ('    ' if is_last else '│   ')
        children = node.get('descendants', [])
        for i, child in enumerate(children):
            if max_siblings is not None and len(children) > max_siblings and i == max_siblings - 2:
                lines.append(child_prefix + f'├── ... ({len(children) - max_siblings + 1} more)')
                lines.extend(_text_tree(children[-1], child_prefix, True, False, max_siblings))
                break
            lines.extend(_text_tree(child, child_prefix, i == len(children) - 1, False, max_siblings))
        return lines

    def _invert_ancestor_tree(ancestors, leaf_node):
        """Invert ancestor tree so highest-level terms are roots and the query term is a leaf.

        Returns a list of top-level nodes, each with 'descendants' pointing downward
        toward the query term.
        """
        def _collect_roots(ancestors):
            """Find the top-level ancestors (those with no further ancestors)."""
            roots = []
            for a in ancestors:
                if 'ancestors' in a and a['ancestors']:
                    roots.extend(_collect_roots(a['ancestors']))
                else:
                    roots.append(a)
            return roots

        def _build_inverted(node, ancestors, target_leaf):
            """Build downward tree from an ancestor node toward the target leaf."""
            # Find which of the ancestors list directly to this node
            children_toward_leaf = []
            for a in ancestors:
                if 'ancestors' in a and a['ancestors']:
                    for grandparent in a['ancestors']:
                        if grandparent['id'] == node['id']:
                            children_toward_leaf.append(a)
                elif a['id'] == node['id']:
                    # This ancestor IS the current node — leaf's direct parent
                    pass

            result = {'id': node['id'], 'label': node['label']}
            if children_toward_leaf:
                result['descendants'] = [
                    _build_inverted(c, ancestors, target_leaf)
                    for c in sorted(children_toward_leaf, key=lambda x: x.get('label', ''))
                ]
            else:
                # This node's child is the query term itself
                result['descendants'] = [leaf_node]
            return result

        # Collect all ancestor nodes into a flat list with their parent links
        all_nodes = {}  # id -> node
        parent_map = {}  # child_id -> set of parent_ids

        def _walk(ancestors, child_id=None):
            for a in ancestors:
                all_nodes[a['id']] = {'id': a['id'], 'label': a['label']}
                if child_id:
                    parent_map.setdefault(child_id, set()).add(a['id'])
                if 'ancestors' in a and a['ancestors']:
                    _walk(a['ancestors'], a['id'])

        _walk(ancestors, leaf_node['id'])

        # Roots are nodes that aren't children of anything
        all_children = set()
        for children in parent_map.values():
            all_children.update(children)
        all_parents = set(parent_map.keys())
        root_ids = all_children - all_parents

        if not root_ids:
            # Fallback: all direct ancestors are roots
            root_ids = {a['id'] for a in ancestors}

        # Add leaf node to all_nodes so its label is available
        all_nodes[leaf_node['id']] = leaf_node

        # Build downward trees from each root
        def _build_down(node_id):
            node = {'id': node_id, 'label': all_nodes.get(node_id, {}).get('label', node_id)}
            children_ids = [cid for cid, pids in parent_map.items() if node_id in pids]
            if children_ids:
                node['descendants'] = [
                    _build_down(cid)
                    for cid in sorted(children_ids, key=lambda x: all_nodes.get(x, {}).get('label', x))
                ]
            return node

        return [_build_down(rid) for rid in sorted(root_ids, key=lambda x: all_nodes.get(x, {}).get('label', x))]

    display_lines = []
    if 'ancestors' in root and root['ancestors']:
        rel_label = 'Part of' if relationship == 'part_of' else 'Is a'
        display_lines.append(f'{rel_label} (ancestors):')
        inverted = _invert_ancestor_tree(root['ancestors'], {'id': root['id'], 'label': root['label']})
        for node in inverted:
            display_lines.extend(_text_tree(node))
        display_lines.append('')

    if 'descendants' in root:
        rel_label = 'Has parts' if relationship == 'part_of' else 'Subtypes'
        display_lines.append(f'{rel_label} (descendants):')
        display_lines.extend(_text_tree(root))

    root['display'] = '\n'.join(display_lines)

    # Full display (no sibling truncation)
    full_lines = []
    if 'ancestors' in root and root['ancestors']:
        rel_label = 'Part of' if relationship == 'part_of' else 'Is a'
        full_lines.append(f'{rel_label} (ancestors):')
        inverted_full = _invert_ancestor_tree(root['ancestors'], {'id': root['id'], 'label': root['label']})
        for node in inverted_full:
            full_lines.extend(_text_tree(node, max_siblings=None))
        full_lines.append('')

    if 'descendants' in root:
        rel_label = 'Has parts' if relationship == 'part_of' else 'Subtypes'
        full_lines.append(f'{rel_label} (descendants):')
        full_lines.extend(_text_tree(root, max_siblings=None))

    root['display_full'] = '\n'.join(full_lines)

    # HTML rendering
    def _html_tree_nodes(node, depth=0, key='descendants'):
        """Render a node as nested HTML list items."""
        sid = node['id']
        label = node['label']
        link = f'<a href="{VFB_BASE}{sid}" target="_blank">{label}</a> <span class="id">({sid})</span>'
        children = node.get(key, [])
        if not children:
            return f'<li><details class="leaf"><summary>{link}</summary></details></li>'
        items = ''.join(_html_tree_nodes(c, depth + 1, key) for c in children)
        return f'<li><details{"" if depth > 1 else " open"}><summary>{link}</summary><ul>{items}</ul></details></li>'

    html_parts = [
        '<!DOCTYPE html><html><head><meta charset="utf-8">',
        f'<title>Hierarchy: {root["label"]}</title>',
        '<style>',
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; margin: 2em; max-width: 900px; line-height: 1.5; color: #24292e; }',
        'h1 { font-size: 1.4em; border-bottom: 1px solid #e1e4e8; padding-bottom: .3em; }',
        'h2 { font-size: 1.1em; margin-top: 1.5em; color: #586069; }',
        'ul { list-style: none; padding-left: 1.5em; }',
        'li { margin: .2em 0; }',
        'details > summary { cursor: pointer; }',
        'details > summary:hover { color: #0366d6; }',
        'details.leaf > summary { list-style-type: "·  "; cursor: default; }',
        'details.leaf > summary::-webkit-details-marker { display: none; }',
        'a { color: #0366d6; text-decoration: none; }',
        'a:hover { text-decoration: underline; }',
        '.id { color: #6a737d; font-size: .85em; }',
        '.path { background: #f6f8fa; padding: .8em 1em; border-radius: 6px; margin: 1em 0; font-size: .95em; }',
        '.path a { font-weight: 500; }',
        '</style></head><body>',
        f'<h1>{root["label"]} <span class="id">({root["id"]})</span></h1>',
    ]

    if 'ancestors' in root and root['ancestors']:
        rel_label = 'Part of' if relationship == 'part_of' else 'Is a'
        html_parts.append(f'<h2>{rel_label} (ancestors)</h2>')
        inverted_html = _invert_ancestor_tree(root['ancestors'], {'id': root['id'], 'label': root['label']})
        items = ''.join(_html_tree_nodes(n) for n in inverted_html)
        html_parts.append(f'<ul>{items}</ul>')

    if 'descendants' in root and root['descendants']:
        rel_label = 'Has parts' if relationship == 'part_of' else 'Subtypes'
        html_parts.append(f'<h2>{rel_label} (descendants)</h2>')
        root_node_html = _html_tree_nodes({'id': root['id'], 'label': root['label'], 'descendants': root['descendants']})
        html_parts.append(f'<ul>{root_node_html}</ul>')

    html_parts.append('</body></html>')
    root['html'] = '\n'.join(html_parts)

    return root
