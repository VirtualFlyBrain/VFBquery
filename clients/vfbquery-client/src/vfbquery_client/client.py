"""VfbClient — thin HTTP client over the VFB cached query API (v3-cached).

Design notes
------------
* Every method maps to an endpoint on the VFBquery ``ha_api`` service and
  returns a tidy ``pandas.DataFrame`` (or a dict for term-info).  The shaping in
  ``_to_df`` is the "typed columns -> DataFrame" adapter from the plan (C2).
* Every endpoint called here exists server-side.  ``/search`` and ``/xref`` are
  new in this branch (plan C1 and C3), so against the public deploy they answer
  404 until that VFBquery build ships.  That is not confined to ``search`` and
  ``xref``: ``get_instances``, ``get_subclasses`` and
  ``get_transcriptomic_profile`` accept a *name*, and resolving one goes through
  ``_resolve_to_id`` -> ``/search``.  Given an id they work against the service
  as deployed today; given a name they do not.  ``VFB_API_BASE`` (or
  ``base_url=``) points the client at a deploy that has them.
* There is no Solr query configuration in this file, on purpose.  Search
  construction, filtering, boosting and ranking all live server-side in
  ``/search`` (VFBquery ``search_config.py``), which is a port of the website's
  own config — so this client agrees with the website's order by construction
  rather than by another copy kept in step by hand.  Repointing the website and
  the MCP at ``/search`` as well is the remaining step and is outside this repo;
  until then ``/search`` has exactly one consumer — this one — and is a seventh
  implementation of VFB search rather than a replacement for the six that exist.
  Three consumers (website, MCP, client) is where "single source of truth"
  becomes a description.  ``docs/search-config-comparison.md`` §4 has the count.
"""
from __future__ import annotations

import collections.abc
import os
import re
import warnings
from typing import Iterable, Optional, Union

import pandas as pd
import requests

#: The public deploy, overridable from the environment. The env var is what lets
#: an unmodified script — or this package's own live tests — be pointed at a
#: staging deploy or a server started from a checkout, which is the only way to
#: exercise an endpoint that has been written but not yet released.
PUBLIC_BASE_URL = "https://v3-cached.virtualflybrain.org"


def default_base_url() -> str:
    """Resolved per call, not at import, so setting the variable in a test or a
    notebook cell takes effect without a reimport."""
    return os.getenv("VFB_API_BASE", "").strip().rstrip("/") or PUBLIC_BASE_URL


#: Kept as a module constant because it was one; it is the public deploy.
DEFAULT_BASE_URL = PUBLIC_BASE_URL

#: Candidate depth for /search.  This is a *ranking* parameter, not a page size:
#: the server's comparator can only promote what Solr returned, so asking for
#: fewer candidates can drop the best answer before ranking ever sees it.  500 is
#: what the website asks for, so it is what gives website-identical order.
DEFAULT_SEARCH_ROWS = 500

#: Minimum synapse count for /query_connectivity.  This mirrors the server's own
#: default rather than 0: the server applies *its* default when the parameter is
#: omitted, so a client default of "unfiltered" would be a promise it cannot keep.
DEFAULT_CONNECTIVITY_WEIGHT = 5

# Anything that looks like a VFB / FlyBase style short_form is treated as an id
# rather than a free-text name.
_ID_RE = re.compile(r"^(VFB_|VFBexp_|FB[a-z]{2}_?\d|FB[a-z]{2}\d)", re.IGNORECASE)

# Columns that the query schemas return as pipe-joined multi-values; split to lists.
_LIST_COLUMNS = {"tags", "templates", "dataset", "parents_label", "parents_id"}

# Friendly renames so output matches what vfb_connect users expect.
_INSTANCE_RENAMES = {"source": "data_source", "source_id": "accession"}


class VfbError(RuntimeError):
    pass


class VfbClient:
    #: Read timeout in seconds. 180 rather than 60 because of connectivity: a
    #: broad neuron type expands over its subclasses into thousands of
    #: individuals, and a cold `Tm1 -> T3` (4,915 against 5,430) has been
    #: measured at 30-60s end to end. The server caches the answer, so it is
    #: only ever the first caller who waits — but a default that times that
    #: caller out turns a slow query into an apparent outage, and the failure
    #: lands on whoever asked the broad question first, which in a workshop is
    #: everyone at once.
    DEFAULT_TIMEOUT = 180

    def __init__(self, base_url: Optional[str] = None,
                 timeout: int = DEFAULT_TIMEOUT,
                 session: Optional[requests.Session] = None):
        self.base_url = (base_url or default_base_url()).rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    # ---- low level -------------------------------------------------------
    def _get(self, path: str, **params) -> Union[dict, list]:
        params = {k: v for k, v in params.items() if v is not None}
        r = self.session.get(f"{self.base_url}/{path.lstrip('/')}",
                             params=params, timeout=self.timeout)
        if r.status_code == 503:
            raise VfbError("Service busy (queue full) — retry shortly.")
        if 400 <= r.status_code < 500:
            # A 4xx from this service is a message written for the person who
            # made the request — which expression failed to parse, which operand
            # was truncated, which name was never defined. `raise_for_status`
            # would throw all of that away and report "400 Client Error", which
            # for /combine in particular is the difference between a fixable
            # mistake and an opaque one. 5xx deliberately still raises the
            # transport's own error: that is not the caller's to fix.
            detail = None
            try:
                body = r.json()
                if isinstance(body, dict):
                    detail = body.get("error")
            except ValueError:
                pass
            if detail:
                raise VfbError(detail)
        r.raise_for_status()
        payload = r.json()
        self._raise_server_warnings(path, payload)
        return payload

    @staticmethod
    def _raise_server_warnings(path: str, payload) -> None:
        """Re-raise a payload's ``warnings`` as Python warnings.

        The service uses a top-level ``warnings`` list to say that a 200 is
        *incomplete* — a connectivity type it could not resolve, or an instance
        list served from the SOLR fallback because Neo4j was down. Nothing in the
        rows distinguishes those from a genuinely empty or genuinely complete
        answer, so dropping the list turns a degraded service into a confident
        wrong result. Handled here rather than per-method: any endpoint can
        degrade, and one that starts emitting warnings later should not have to
        remember to opt in.

        ``stacklevel=3`` puts the warning on the ``VfbClient`` method the caller
        actually invoked (caller -> method -> ``_get`` -> here). Calls that reach
        the network via ``_resolve_to_id`` are one frame deeper and will point at
        that helper instead; the message names the endpoint either way.

        A consequence of pointing at the caller worth knowing in a notebook:
        Python's default ``"default"`` filter shows a given message **once per
        source location**, so a loop that hits the same degraded endpoint fifty
        times warns once, and re-running the same cell may not warn at all. The
        warning means "this answer may be partial", never "this is the only
        answer that was". ``warnings.simplefilter("always")`` if that matters.
        """
        if not isinstance(payload, dict):
            return
        for message in payload.get("warnings") or []:
            warnings.warn(f"{path.lstrip('/')}: {message}", stacklevel=3)

    #: Keys under which an endpoint returns its row list. ``run_query``, ``/search``
    #: and ``/xref`` all use ``rows``; ``/query_connectivity`` predates them and
    #: uses ``connections``. Without the second name its envelope falls through to
    #: the "a dict is one row" branch below and the caller gets a 1x3 frame of
    #: nested lists instead of the connectivity table.
    _ROW_KEYS = ("rows", "connections")

    @classmethod
    def _to_df(cls, payload) -> pd.DataFrame:
        """Normalise a query response into a DataFrame (the C2 adapter)."""
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = next((payload[k] for k in cls._ROW_KEYS
                         if isinstance(payload.get(k), list)), None)
            if rows is None:
                rows = [payload]        # a bare object is a single row
        else:
            rows = []
        df = pd.DataFrame(rows)
        for col in _LIST_COLUMNS & set(df.columns):
            df[col] = df[col].apply(
                lambda v: v.split("|") if isinstance(v, str) and "|" in v else v)
        return df

    def _resolve_to_id(self, query: str) -> str:
        """Return a short_form for a name/symbol via ``/search``, or pass an id through.

        Uses the ranked term search (``search()`` -> ``GET /search``), NOT
        resolve_entity — the latter is FlyBase-Chado resolution and won't resolve
        ontology/anatomy term names.
        """
        if _ID_RE.match(query):
            return query
        # limit=1, not rows=1: take the top of a fully-ranked list rather than
        # asking Solr for a single unranked candidate.
        hits = self.search(query, limit=1)
        if len(hits):
            row = hits.iloc[0]
            return row.get("short_form") or row.get("id") or query
        raise VfbError(f"No term matched {query!r}.")

    # ---- term info -------------------------------------------------------
    def term(self, term: str) -> dict:
        """Full TermInfo for one id (GET /get_term_info)."""
        return self._get("get_term_info", id=term)

    def terms(self, terms: Iterable[str]) -> list:
        return [self.term(t) for t in terms]

    # ---- discovery -------------------------------------------------------
    def search(self, query: str, limit: Optional[int] = 50,
               rows: int = DEFAULT_SEARCH_ROWS,
               filter_types: Optional[Iterable[str]] = None,
               exclude_types: Optional[Iterable[str]] = None,
               boost_types: Optional[Iterable[str]] = None,
               demote_types: Optional[Iterable[str]] = None) -> pd.DataFrame:
        """Free-text term search (GET /search) — the website's own ranked results.

        Ranked, fuzzy, synonym/autosuggest-aware ('DA1 lPN', 'kenyon', partials, bare
        hemibrain bodyIds). This is the discovery entry point; see ``_resolve_to_id``
        on why not resolve_entity.

        Rows come back in the order the website shows them, because the server runs the
        website's own query construction and comparator — with one deliberate
        difference. ``/search`` always adds an exact-label boost the website has no
        counterpart for, and there is no parameter to turn it off. It fixes a real
        website recall bug (searching ``neuron`` does not retrieve *neuron* into the
        candidate set at all), and it only ever lifts a term whose label **is** the
        query, so it changes retrieval rather than relative order: the recall gate
        holds top-10 churn at exactly zero. Treat "website order" as true of every
        query except one whose exact-label match the website was losing. Each row carries
        ``short_form``, a display ``label``
        ("synonym (label)" or "label (short_form)"), ``original_label``, ``id``,
        ``facets_annotation`` and ``unique_facets``.

        Args:
            limit: how many ranked rows to return (None for all).
            rows:  how many candidates the server asks Solr for. A *ranking* knob —
                   lowering it can drop the best answer before ranking sees it.
            filter_types / exclude_types: keep / drop by facet (e.g. "Class",
                   "Individual", "Neuron").
            boost_types / demote_types:   nudge facets up / down the ranking.
        """
        params = {"query": query, "rows": rows}
        if limit is not None:
            params["limit"] = limit
        for name, value in (("filter_types", filter_types),
                            ("exclude_types", exclude_types),
                            ("boost_types", boost_types),
                            ("demote_types", demote_types)):
            if value:
                params[name] = ",".join(value)
        return self._to_df(self._get("search", **params))

    def get_instances(self, class_expression: str) -> pd.DataFrame:
        """Individuals of a type across all datasets (run_query ListAllAvailableImages)."""
        short_form = self._resolve_to_id(class_expression)
        df = self._to_df(self._get("run_query", id=short_form,
                                    query_type="ListAllAvailableImages"))
        return df.rename(columns={k: v for k, v in _INSTANCE_RENAMES.items()
                                  if k in df.columns})

    def get_subclasses(self, class_expression: str) -> pd.DataFrame:
        return self._to_df(self._get("run_query",
                                     id=self._resolve_to_id(class_expression),
                                     query_type="SubclassesOf"))

    # ---- connectivity ----------------------------------------------------
    def get_connected_neurons_by_type(self, upstream_type: Optional[str] = None,
                                       downstream_type: Optional[str] = None,
                                       weight: int = DEFAULT_CONNECTIVITY_WEIGHT,
                                       group_by_class: bool = False,
                                       exclude_dbs: Optional[Iterable[str]] = None,
                                       ) -> pd.DataFrame:
        """Type -> type synaptic connections (GET /query_connectivity).

        Either side may be omitted, which asks the open-ended question:
        everything downstream of a type, or everything upstream of it.

        **A type includes its subclasses.** ``"Kenyon cell"`` finds Kenyon
        cells, though none of the ~16,000 of them is typed to that class — they
        hang off its subclasses. The server does the expansion and reports what
        it covered.

        ``weight`` is the minimum synapse count and is applied **server-side**;
        the default matches the server's own so the threshold in the signature is
        the threshold that ran. Filtering here instead would be a second, weaker
        filter on top of an unstated one.

        ``group_by_class`` aggregates to one row per class pair, with
        ``percent_connected`` and ``average_weight``, rather than one row per
        pair of neurons.

        ``exclude_dbs`` names connectome datasets to leave out, by symbol. The
        default — ``None``, meaning the server's own — drops ``hb`` and
        ``fafb``, which **double-count** against datasets that are kept rather
        than being poor data: FAFB and FlyWire reconstruct the same EM volume,
        and hemibrain overlaps in type with FlyWire and male-CNS. Pass ``[]``
        for every dataset, or exclude the others to isolate one; reproducing a
        published hemibrain figure needs that.

        A type the server could not resolve comes back as a warning rather than
        an error, and an unresolved type is indistinguishable from a genuinely
        unconnected pair by looking at the rows — so warnings are re-raised as
        Python warnings instead of being dropped. That happens in ``_get`` for
        every endpoint, not here.
        """
        if upstream_type is None and downstream_type is None:
            raise ValueError(
                "At least one of upstream_type or downstream_type is required.")
        # An empty list has to reach the server as an empty value rather than be
        # dropped as absent: "exclude nothing" and "use your default" are
        # different requests, and _get drops only None.
        dbs = None if exclude_dbs is None else ",".join(exclude_dbs)
        return self._to_df(self._get("query_connectivity",
                                     upstream_type=upstream_type,
                                     downstream_type=downstream_type,
                                     weight=weight,
                                     group_by_class=str(group_by_class).lower(),
                                     exclude_dbs=dbs))

    def get_neuron_connectivity(self, neuron_id: str) -> pd.DataFrame:
        """Per-individual partners (run_query NeuronNeuronConnectivityQuery)."""
        return self._to_df(self._get("run_query", id=neuron_id,
                                     query_type="NeuronNeuronConnectivityQuery"))

    # ---- similarity ------------------------------------------------------
    def get_similar_neurons(self, neuron_id: str) -> pd.DataFrame:
        """NBLAST morphological matches (run_query SimilarMorphologyTo)."""
        df = self._to_df(self._get("run_query", id=neuron_id,
                                    query_type="SimilarMorphologyTo"))
        if "score" in df.columns:
            df = df.sort_values("score", ascending=False)
        return df

    # ---- transcriptomics -------------------------------------------------
    def get_transcriptomic_profile(self, term: str) -> pd.DataFrame:
        """scRNAseq profile for an anatomy term (run_query anatScRNAseqQuery)."""
        return self._to_df(self._get("run_query", id=self._resolve_to_id(term),
                                     query_type="anatScRNAseqQuery"))

    # ---- datasets & xref -------------------------------------------------
    def list_connectome_datasets(self) -> pd.DataFrame:
        return self._to_df(self._get("list_connectome_datasets"))

    def xref(self, id: Optional[str] = None, accession: Optional[str] = None,
             db: Optional[str] = None) -> pd.DataFrame:
        """VFB id <-> external accession, both ways (GET /xref).

        Pass exactly one of ``id`` (VFB id -> every accession that term carries)
        or ``accession`` (external id -> the VFB term that carries it).  ``db``
        optionally narrows to one site and accepts its symbol ("hb"), short_form
        ("neuprint_JRC_Hemibrain_1point2point1") or label.

        Columns: ``id``, ``label``, ``db``, ``db_label``, ``site_id``,
        ``accession``, ``is_data_source``, ``link``.

        The reverse direction is confirmed, not guessed: the server checks each
        candidate's own xref list and returns a row only on an exact accession
        match.  An accession that appears nowhere in VFB's indexed text is
        therefore an empty frame rather than a plausible wrong neuron.
        """
        if bool(id) == bool(accession):
            raise ValueError("Provide exactly one of id= or accession= (+ optional db=).")
        return self._to_df(self._get("xref", id=id, accession=accession, db=db))

    # ---- set algebra over queries ----------------------------------------
    #: Query-string keys ``/combine`` uses for itself. An operand named one of
    #: these would be read as a parameter and silently vanish from the
    #: expression, so it is refused here — before a request that would come back
    #: as a puzzling "unknown name" 400, or worse, as a plausible answer to a
    #: different question.
    _COMBINE_RESERVED = frozenset({
        "expr", "expression", "q", "universe", "limit", "offset",
        "require_complete", "explain_only", "order_by", "force_refresh",
    })

    @classmethod
    def _combine_params(cls, expr, operands, universe=None):
        if not operands:
            raise ValueError(
                "combine() needs operands: a dict mapping each name in the "
                "expression to a query, e.g. "
                "{'calyx': 'NeuronsPartHere:FBbt_00007401'}")
        params = {"expr": expr}
        for name, spec in operands.items():
            if name in cls._COMBINE_RESERVED:
                raise ValueError(
                    f"{name!r} cannot be used as an operand name — /combine uses "
                    f"it for itself. Reserved: {', '.join(sorted(cls._COMBINE_RESERVED))}.")
            params[name] = cls._combine_spec(spec)
        if universe is not None:
            params["universe"] = cls._combine_spec(universe)
        return params

    @staticmethod
    def _combine_spec(spec) -> str:
        """Accept the three shapes a caller naturally has to hand.

        A string is passed through as written. A ``(query_type, id)`` pair spares
        the caller a bit of string joining. An iterable of ids becomes ``ids:``,
        which is the important one: it is how the output of one combination — or
        a column of a DataFrame, or a list from a paper's supplementary table —
        goes back in as the input to the next.
        """
        if isinstance(spec, str):
            return spec
        if isinstance(spec, tuple) and len(spec) == 2:
            return f"{spec[0]}:{spec[1]}"
        if isinstance(spec, pd.Series):
            spec = spec.tolist()
        if isinstance(spec, collections.abc.Iterable):
            ids = [str(i) for i in spec if str(i).strip()]
            if not ids:
                raise ValueError("An id list operand cannot be empty.")
            return "ids:" + ",".join(ids)
        raise TypeError(
            f"Cannot read {spec!r} as a query. Give a string "
            "('NeuronsPartHere:FBbt_00007401', 'search:kenyon cell', "
            "'ids:VFB_1,VFB_2'), a (query_type, id) pair, or a list of ids.")

    def combine(self, expr: str, operands: Optional[dict] = None,
                universe=None, limit: Optional[int] = None,
                require_complete: bool = False) -> pd.DataFrame:
        """Set algebra over the results of several queries (GET /combine).

        Each name in ``expr`` is a query; the expression says how to combine
        their results. Rows are matched on each result's own term-id column, so
        tables with completely different shapes still compare correctly::

            vfb.combine("calyx AND lh", {
                "calyx": "NeuronsPartHere:FBbt_00007401",
                "lh":    "NeuronsPartHere:FBbt_00007053"})

        Operators: ``OR AND NOT XOR NAND NOR XNOR``, unary ``NOT``, brackets
        (``[]``, ``()`` or ``{}``), symbols (``| & - ^``) and plain-English
        aliases ("but not", "in both", "either but not both"). Precedence,
        loosest binding first: OR/NOR, then XOR/XNOR, then AND/NAND/NOT — all
        left-associative. Bracket anything you would otherwise have to think
        about.

        No column from any operand is dropped: the returned frame carries the
        union of every operand's columns, plus ``found_in`` (which operands the
        row came from) and ``found_in_count``. Where two operands disagree about
        the value of a shared column, both are kept, the second suffixed with
        its operand name.

        The explanation travels with the frame in ``df.attrs``:
        ``as_read`` (the grouping actually used — check it), ``plain_english``,
        ``steps`` (every intermediate set size), ``operands``, ``universe`` and
        ``count`` (the full size, which differs from ``len(df)`` when ``limit``
        is set). Anything the server thinks is misleading — a truncated operand,
        two sides that can never intersect, a complement against an implicit
        universe — arrives as a Python warning.

        Args:
            expr: the expression.
            operands: ``{name: query}``. A query is a string
                (``'<QueryType>:<id>'``, ``'search:<text>'``, ``'ids:<id>,<id>'``),
                a ``(query_type, id)`` pair, or any iterable of ids (a list, a
                set, a DataFrame column) — which is how one combination's output
                becomes the next one's input.
            universe: what "everything" means, for NOT/NOR/NAND/XNOR. Same forms
                as an operand. Without it the universe is whatever the operands
                between them returned, which makes ``NOR`` always empty — the
                server warns when that matters.
            limit: return at most this many rows (``attrs['count']`` still
                reports the full size).
            require_complete: fail with :class:`VfbError` rather than warn if any
                operand came back truncated. Use it when the number is going in
                a paper.
        """
        params = self._combine_params(expr, operands, universe)
        if limit is not None:
            params["limit"] = limit
        if require_complete:
            params["require_complete"] = "true"
        payload = self._get("combine", **params)
        df = self._to_df(payload)
        # attrs rather than extra columns or a bespoke result class: the frame
        # stays a plain DataFrame that every downstream tool already understands,
        # and the explanation is one attribute away instead of being lost.
        for key in ("expression", "as_read", "plain_english", "steps",
                    "operands", "universe", "count", "capped"):
            if key in payload:
                df.attrs[key] = payload[key]
        return df

    def explain_combination(self, expr: str, operands: Optional[dict] = None,
                            universe=None) -> dict:
        """How ``/combine`` would read an expression — without running anything.

        Returns ``as_read`` (the bracketing that would be used) and
        ``plain_english`` (a sentence naming the actual queries). Cheap, because
        no query is run: worth calling first on any expression whose grouping you
        would otherwise be assuming.
        """
        params = self._combine_params(expr, operands, universe)
        params["explain_only"] = "true"
        return self._get("combine", **params)

    # ---- links (client-side, no endpoint) --------------------------------
    @staticmethod
    def get_vfb_link(ids: Union[str, Iterable[str]], template: Optional[str] = None) -> str:
        """Build a virtualflybrain.org link that opens with these IDs loaded."""
        if isinstance(ids, str):
            ids = [ids]
        id_list = ",".join(ids)
        url = f"https://virtualflybrain.org/?id={id_list}"
        if template:
            url += f"&t={template}"
        return url
