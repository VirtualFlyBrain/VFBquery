"""VfbClient — thin HTTP client over the VFB cached query API (v3-cached).

Design notes
------------
* Every method maps to an existing (or planned) endpoint on the VFBquery
  ``ha_api`` service and returns a tidy ``pandas.DataFrame`` (or a dict for
  term-info).  The shaping in ``_to_df`` is the "typed columns -> DataFrame"
  adapter from the plan (C2).
* Endpoints marked ``[NEW]`` below (``/search``, ``/xref``) are part of the same
  plan (C1, C3) and are expected to exist server-side; the client already calls
  them so it is complete the moment they ship.  Everything else works against
  the live service today.
"""
from __future__ import annotations

import re
from typing import Iterable, Optional, Union

import pandas as pd
import requests

DEFAULT_BASE_URL = "https://v3-cached.virtualflybrain.org"

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
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 60,
                 session: Optional[requests.Session] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    # ---- low level -------------------------------------------------------
    def _get(self, path: str, **params) -> Union[dict, list]:
        params = {k: v for k, v in params.items() if v is not None}
        r = self.session.get(f"{self.base_url}/{path.lstrip('/')}",
                             params=params, timeout=self.timeout)
        if r.status_code == 503:
            raise VfbError("Service busy (queue full) — retry shortly.")
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _to_df(payload) -> pd.DataFrame:
        """Normalise a query response into a DataFrame (the C2 adapter)."""
        if isinstance(payload, dict) and "rows" in payload:
            rows = payload["rows"]
        elif isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = [payload]
        else:
            rows = []
        df = pd.DataFrame(rows)
        for col in _LIST_COLUMNS & set(df.columns):
            df[col] = df[col].apply(
                lambda v: v.split("|") if isinstance(v, str) and "|" in v else v)
        return df

    def _resolve_to_id(self, query: str) -> str:
        """Return a short_form for a name/symbol, or pass an id straight through."""
        if _ID_RE.match(query):
            return query
        # Prefer /search (C1). Fall back to /resolve_entity which exists today.
        try:
            hits = self.search(query, rows=1)
            if len(hits):
                return hits.iloc[0].get("short_form") or hits.iloc[0].get("id")
        except requests.HTTPError:
            pass
        res = self._get("resolve_entity", query=query)
        if isinstance(res, dict):
            return res.get("short_form") or res.get("id") or query
        return query

    # ---- term info -------------------------------------------------------
    def term(self, term: str) -> dict:
        """Full TermInfo for one id (GET /get_term_info)."""
        return self._get("get_term_info", id=term)

    def terms(self, terms: Iterable[str]) -> list:
        return [self.term(t) for t in terms]

    # ---- discovery -------------------------------------------------------
    def search(self, query: str, rows: int = 50, filters: Optional[str] = None) -> pd.DataFrame:
        """Free-text term search.  [NEW /search — plan C1]"""
        return self._to_df(self._get("search", query=query, rows=rows, filters=filters))

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
    def get_connected_neurons_by_type(self, upstream_type: str, downstream_type: str,
                                       weight: int = 0) -> pd.DataFrame:
        """Type -> type synaptic connections (GET /query_connectivity)."""
        df = self._to_df(self._get("query_connectivity",
                                    upstream_type=upstream_type,
                                    downstream_type=downstream_type))
        if weight and "weight" in df.columns:
            df = df[df["weight"] >= weight]
        return df

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
        """VFB id <-> external accession, both ways.  [NEW /xref — plan C3]"""
        if not id and not accession:
            raise ValueError("Provide either id= or accession=(+db=).")
        return self._to_df(self._get("xref", id=id, accession=accession, db=db))

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
