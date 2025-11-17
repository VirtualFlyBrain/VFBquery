"""
Simple Owlery REST API client to replace VFBConnect dependency.

This module provides direct HTTP access to the Owlery OWL reasoning service,
eliminating the need for vfb_connect which has problematic GUI dependencies.
"""

import requests
import json
import pandas as pd
import re
from urllib.parse import quote
from typing import List, Optional, Dict, Any, Union
import concurrent.futures


def short_form_to_iri(short_form: str) -> str:
    """
    Convert a short form (e.g., 'FBbt_00003748', 'VFBexp_FBtp0022557') to full IRI.
    
    Handles common ID prefixes:
    - VFB* -> http://virtualflybrain.org/reports/
    - FB* -> http://purl.obolibrary.org/obo/
    - Other -> http://purl.obolibrary.org/obo/ (default)
    
    :param short_form: Short form like 'FBbt_00003748' or 'VFBexp_FBtp0022557'
    :return: Full IRI
    """
    # VFB IDs use virtualflybrain.org/reports
    if short_form.startswith('VFB'):
        return f"http://virtualflybrain.org/reports/{short_form}"
    
    # FB* IDs (FlyBase) use purl.obolibrary.org/obo
    if short_form.startswith('FB'):
        return f"http://purl.obolibrary.org/obo/{short_form}"
    
    # Default to OBO for other IDs
    return f"http://purl.obolibrary.org/obo/{short_form}"


def gen_short_form(iri: str) -> str:
    """
    Generate short_form from an IRI string (VFBConnect compatible).
    Splits by '/' or '#' and takes the last part.
    
    :param iri: An IRI string
    :return: short_form
    """
    return re.split('/|#', iri)[-1]


class OwleryClient:
    """
    Simple client for Owlery OWL reasoning service.
    
    Provides minimal interface matching VFBConnect's OWLeryConnect functionality
    for subclass queries needed by VFBquery.
    """
    
    def __init__(self, owlery_endpoint: str = "http://owl.virtualflybrain.org/kbs/vfb"):
        """
        Initialize Owlery client.
        
        :param owlery_endpoint: Base URL for Owlery service (default: VFB public instance)
        """
        self.owlery_endpoint = owlery_endpoint.rstrip('/')
    
    def get_subclasses(self, query: str, query_by_label: bool = True, 
                      verbose: bool = False, direct: bool = False) -> List[str]:
        """
        Query Owlery for subclasses matching an OWL class expression.
        
        This replicates the VFBConnect OWLeryConnect.get_subclasses() method.
        Based on: https://github.com/VirtualFlyBrain/VFB_connect/blob/master/src/vfb_connect/owl/owlery_query_tools.py
        
        :param query: OWL class expression query string (with short forms like '<FBbt_00003748>')
        :param query_by_label: If True, query uses label syntax (quotes). 
                               If False, uses IRI syntax (angle brackets).
        :param verbose: If True, print debug information
        :param direct: Return direct subclasses only. Default False.
        :return: List of class IDs (short forms like 'FBbt_00003748')
        """
        try:
            # Convert short forms in query to full IRIs
            # Pattern: <FBbt_00003748> -> <http://purl.obolibrary.org/obo/FBbt_00003748>
            # Match angle brackets with content that looks like a short form (alphanumeric + underscore)
            import re
            def convert_short_form_to_iri(match):
                short_form = match.group(1)  # Extract content between < >
                # Only convert if it looks like a short form (contains underscore, no slashes)
                if '_' in short_form and '/' not in short_form:
                    return f"<{short_form_to_iri(short_form)}>"
                else:
                    # Already an IRI or other syntax, leave as-is
                    return match.group(0)
            
            # Replace all <SHORT_FORM> patterns with <FULL_IRI>
            iri_query = re.sub(r'<([^>]+)>', convert_short_form_to_iri, query)
            
            if verbose:
                print(f"Original query: {query}")
                print(f"IRI query: {iri_query}")
            
            # Build Owlery subclasses endpoint URL
            # Based on VFBConnect's query() method
            params = {
                'object': iri_query,
                'direct': 'false',  # Always use indirect (transitive) queries
                'includeDeprecated': 'false',  # Exclude deprecated terms
                'includeEquivalent': 'true'  # Include equivalent classes
            }
            
            # Make HTTP GET request with longer timeout for complex queries (40 minutes for OWL reasoning)
            # Add retry logic for connection resets (common with long-running queries)
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry_strategy = Retry(
                total=3,  # Total number of retries
                backoff_factor=2,  # Wait 2s, 4s, 8s between retries
                status_forcelist=[500, 502, 503, 504],  # Retry on server errors
                allowed_methods=["GET"]  # Only retry GET requests
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.get(
                f"{self.owlery_endpoint}/subclasses",
                params=params,
                timeout=2400
            )
            
            if verbose:
                print(f"Owlery query: {response.url}")
            
            response.raise_for_status()
            
            # Parse JSON response
            # Owlery returns: {"superClassOf": ["IRI1", "IRI2", ...]}
            # Based on VFBConnect: return_type='superClassOf' for subclasses
            data = response.json()
            
            if verbose:
                print(f"Response keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
            
            # Extract IRIs from response using VFBConnect's key
            iris = []
            if isinstance(data, dict) and 'superClassOf' in data:
                iris = data['superClassOf']
            elif isinstance(data, list):
                # Fallback: simple list response
                iris = data
            else:
                if verbose:
                    print(f"Unexpected Owlery response format: {type(data)}")
                    print(f"Response: {data}")
                return []
            
            if not isinstance(iris, list):
                if verbose:
                    print(f"Warning: No results! This is likely due to a query error")
                    print(f"Query: {query}")
                return []
            
            # Convert IRIs to short forms using gen_short_form logic from VFBConnect
            # gen_short_form splits by '/' or '#' and takes the last part
            import re
            def gen_short_form(iri):
                """Generate short_form from an IRI string (VFBConnect compatible)"""
                return re.split('/|#', iri)[-1]
            
            short_forms = list(map(gen_short_form, iris))
            
            if verbose:
                print(f"Found {len(short_forms)} subclasses")
            
            return short_forms
            
        except requests.RequestException as e:
            print(f"ERROR: Owlery request failed: {e}")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error in Owlery query: {e}")
            raise
    
    def get_instances(self, query: str, query_by_label: bool = True, 
                     verbose: bool = False, direct: bool = False) -> List[str]:
        """
        Query Owlery for instances matching an OWL class expression.
        
        Similar to get_subclasses but returns individuals/instances instead of classes.
        Used for queries like ImagesNeurons that need individual images rather than classes.
        
        :param query: OWL class expression query string (with short forms like '<FBbt_00003748>')
        :param query_by_label: If True, query uses label syntax (quotes). 
                               If False, uses IRI syntax (angle brackets).
        :param verbose: If True, print debug information
        :param direct: Return direct instances only. Default False.
        :return: List of instance IDs (short forms like 'VFB_00101567')
        """
        try:
            # Convert short forms in query to full IRIs
            import re
            def convert_short_form_to_iri(match):
                short_form = match.group(1)
                if '_' in short_form and '/' not in short_form:
                    return f"<{short_form_to_iri(short_form)}>"
                else:
                    return match.group(0)
            
            iri_query = re.sub(r'<([^>]+)>', convert_short_form_to_iri, query)
            
            if verbose:
                print(f"Original query: {query}")
                print(f"IRI query: {iri_query}")
            
            # Build Owlery instances endpoint URL
            params = {
                'object': iri_query,
                'direct': 'true' if direct else 'false',
                'includeDeprecated': 'false'
            }
            
            # Build full URL for debugging
            full_url = f"{self.owlery_endpoint}/instances"
            prepared_request = requests.Request('GET', full_url, params=params).prepare()
            
            if verbose:
                print(f"Owlery instances URL: {prepared_request.url}")
            
            # Make HTTP GET request to instances endpoint (40 minutes for OWL reasoning)
            # Add retry logic for connection resets (common with long-running queries)
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry_strategy = Retry(
                total=3,  # Total number of retries
                backoff_factor=2,  # Wait 2s, 4s, 8s between retries
                status_forcelist=[500, 502, 503, 504],  # Retry on server errors
                allowed_methods=["GET"]  # Only retry GET requests
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            response = session.get(
                f"{self.owlery_endpoint}/instances",
                params=params,
                timeout=2400
            )
            
            response.raise_for_status()
            
            # Parse JSON response
            # KEY DIFFERENCE: Owlery returns {"hasInstance": ["IRI1", "IRI2", ...]} for instances
            # whereas subclasses returns {"superClassOf": [...]}
            data = response.json()
            
            if verbose:
                print(f"Response keys: {data.keys() if isinstance(data, dict) else 'not a dict'}")
            
            # Extract IRIs from response using correct key
            iris = []
            if isinstance(data, dict) and 'hasInstance' in data:
                iris = data['hasInstance']
            elif isinstance(data, list):
                iris = data
            else:
                if verbose:
                    print(f"Unexpected Owlery response format: {type(data)}")
                    print(f"Response: {data}")
                return []
            
            if not isinstance(iris, list):
                if verbose:
                    print(f"Warning: No results! This is likely due to a query error")
                    print(f"Query: {query}")
                return []
            
            # Convert IRIs to short forms
            def gen_short_form(iri):
                return re.split('/|#', iri)[-1]
            
            short_forms = list(map(gen_short_form, iris))
            
            if verbose:
                print(f"Found {len(short_forms)} instances")
                if short_forms:
                    print(f"Sample instances: {short_forms[:5]}")
            
            return short_forms
            
        except requests.RequestException as e:
            # Show the full URL that was attempted
            try:
                full_url = f"{self.owlery_endpoint}/instances"
                prepared_request = requests.Request('GET', full_url, params=params).prepare()
                print(f"ERROR: Owlery instances request failed: {e}")
                print(f"       Test URL: {prepared_request.url}")
            except:
                print(f"ERROR: Owlery instances request failed: {e}")
            raise
        except Exception as e:
            print(f"ERROR: Unexpected error in Owlery instances query: {e}")
            raise


class MockNeo4jClient:
    """
    Mock Neo4j client that raises NotImplementedError for all queries.
    Used when Neo4j is not available or connection fails.
    """
    def commit_list(self, statements):
        raise NotImplementedError(
            "Neo4j queries are not available. "
            "Either Neo4j server is unavailable or connection failed."
        )


class SimpleVFBConnect:
    """
    Minimal replacement for VFBConnect that works in headless environments.
    
    Provides:
    - Owlery client (vc.vfb.oc) for OWL reasoning queries
    - Neo4j client (vc.nc) - tries real Neo4j first, falls back to mock
    - SOLR term info fetcher (vc.get_TermInfo) for term metadata
    
    This eliminates the need for vfb_connect which requires GUI libraries
    (vispy, Quartz.framework on macOS) that aren't available in all dev environments.
    """
    
    def __init__(self, solr_url: str = "https://solr.virtualflybrain.org/solr/vfb_json"):
        """
        Initialize simple VFB connection with Owlery and SOLR access.
        Attempts to use real Neo4j if available, falls back to mock otherwise.
        
        :param solr_url: Base URL for SOLR server (default: VFB public instance)
        """
        self._vfb = None
        self._nc = None
        self._nc_available = None  # Cache whether Neo4j is available
        self.solr_url = solr_url
    
    @property
    def vfb(self):
        """Get VFB object with Owlery client."""
        if self._vfb is None:
            # Create simple object with oc (Owlery client) property
            class VFBObject:
                def __init__(self):
                    self.oc = OwleryClient()
            self._vfb = VFBObject()
        return self._vfb
    
    @property
    def nc(self):
        """
        Get Neo4j client - tries real Neo4j first, falls back to mock.
        
        Attempts to connect to Neo4j using our lightweight client.
        If unavailable (server down, network issues), returns mock client.
        """
        if self._nc is None:
            # Try to connect to real Neo4j
            if self._nc_available is None:
                try:
                    from .neo4j_client import Neo4jConnect
                    # Try to initialize - this will fail if Neo4j server unreachable
                    self._nc = Neo4jConnect()
                    self._nc_available = True
                    print("✅ Neo4j connection established")
                except Exception as e:
                    # Fall back to mock client
                    self._nc = MockNeo4jClient()
                    self._nc_available = False
                    print(f"ℹ️  Neo4j unavailable ({type(e).__name__}), using Owlery-only mode")
            elif self._nc_available:
                from .neo4j_client import Neo4jConnect
                self._nc = Neo4jConnect()
            else:
                self._nc = MockNeo4jClient()
        return self._nc
    
    def get_TermInfo(self, short_forms: List[str], 
                    return_dataframe: bool = False, 
                    summary: bool = False) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Fetch term info from SOLR directly.
        
        This replicates VFBConnect's get_TermInfo method using direct SOLR queries.
        
        :param short_forms: List of term IDs to fetch (e.g., ['FBbt_00003748'])
        :param return_dataframe: If True, return as pandas DataFrame
        :param summary: If True, return summarized version (currently ignored)
        :return: List of term info dictionaries or DataFrame
        """
        # Fetch term info entries in parallel to speed up multiple short_form requests.
        # We preserve input order in the returned list.
        results_map = {}

        def fetch(short_form: str):
            try:
                url = f"{self.solr_url}/select"
                params = {
                    "indent": "true",
                    "fl": "term_info",
                    "q.op": "OR",
                    "q": f"id:{short_form}"
                }

                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                docs = data.get("response", {}).get("docs", [])

                if not docs:
                    # no result for this id
                    return None

                if "term_info" not in docs[0] or not docs[0]["term_info"]:
                    return None

                term_info_str = docs[0]["term_info"][0]
                term_info_obj = json.loads(term_info_str)
                return term_info_obj

            except requests.RequestException as e:
                print(f"ERROR: Error fetching data from SOLR for {short_form}: {e}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Error decoding JSON for {short_form}: {e}")
            except Exception as e:
                print(f"ERROR: Unexpected error for {short_form}: {e}")
            return None

        max_workers = min(10, max(1, len(short_forms)))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as exc:
            # map preserves order of input keys in Python 3.9+ when using as_completed we reassemble
            future_to_sf = {exc.submit(fetch, sf): sf for sf in short_forms}
            for fut in concurrent.futures.as_completed(future_to_sf):
                sf = future_to_sf[fut]
                try:
                    res = fut.result()
                    results_map[sf] = res
                except Exception as e:
                    print(f"ERROR: Exception while fetching {sf}: {e}")

        # Build results list in the same order as short_forms input, skipping None results
        results = [results_map[sf] for sf in short_forms if sf in results_map and results_map[sf] is not None]
        
        # Convert to DataFrame if requested
        if return_dataframe and results:
            try:
                return pd.json_normalize(results)
            except Exception as e:
                print(f"ERROR: Error converting to DataFrame: {e}")
                return results
        
        return results
