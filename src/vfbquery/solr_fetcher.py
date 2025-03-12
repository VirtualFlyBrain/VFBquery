import requests
import json
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from vfb_connect import vfb

class SolrTermInfoFetcher:
    """Fetches term information directly from the Solr server instead of using VfbConnect"""
    
    def __init__(self, solr_url: str = "https://solr.virtualflybrain.org/solr/vfb_json"):
        """Initialize with the Solr server URL"""
        self.solr_url = solr_url
        self.logger = logging.getLogger(__name__)
        self.vfb = vfb
    
    def get_TermInfo(self, short_forms: List[str], 
                    return_dataframe: bool = False, 
                    summary: bool = False) -> Union[List[Dict[str, Any]], pd.DataFrame]:
        """
        Fetch term info from Solr directly, mimicking VFBconnect's interface
        
        Args:
            short_forms: List of term IDs to fetch
            return_dataframe: If True, return as pandas DataFrame
            summary: If True, return summarized version
            
        Returns:
            List of term info dictionaries or DataFrame
        """
        results = []
        
        for short_form in short_forms:
            try:
                url = f"{self.solr_url}/select"
                params = {
                    "indent": "true",
                    "fl": "term_info",
                    "q.op": "OR",
                    "q": f"id:{short_form}"
                }
                
                self.logger.debug(f"Querying Solr for {short_form}")
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                
                if not docs:
                    self.logger.warning(f"No results found for {short_form}")
                    continue
                    
                if "term_info" not in docs[0] or not docs[0]["term_info"]:
                    self.logger.warning(f"No term_info found for {short_form}")
                    continue
                
                # Extract and parse the term_info string which is itself JSON
                term_info_str = docs[0]["term_info"][0]
                term_info_obj = json.loads(term_info_str)
                results.append(term_info_obj)
                
            except requests.RequestException as e:
                self.logger.error(f"Error fetching data from Solr: {e}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON for {short_form}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error for {short_form}: {e}")
        
        # Convert to DataFrame if requested
        if return_dataframe and results:
            try:
                return pd.json_normalize(results)
            except Exception as e:
                self.logger.error(f"Error converting to DataFrame: {e}")
                return results
            
        return results
    
    # Pass through any non-implemented methods to VFBconnect
    def __getattr__(self, name):
        """
        Automatically pass through any non-implemented methods to VFBconnect
        
        This allows us to use this class as a drop-in replacement for VfbConnect
        while only implementing the methods we want to customize.
        """
        self.logger.debug(f"Passing through method call: {name}")
        return getattr(self.vfb, name)