import requests
import json
import logging
from typing import List, Dict, Any, Optional

class SolrTermInfoFetcher:
    """Fetches term information directly from the Solr server instead of using VfbConnect"""
    
    def __init__(self, solr_url: str = "https://solr.virtualflybrain.org/solr/vfb_json"):
        """Initialize with the Solr server URL"""
        self.solr_url = solr_url
        self.logger = logging.getLogger(__name__)
    
    def get_TermInfo(self, short_forms: List[str], 
                    return_dataframe: bool = False, 
                    summary: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch term info from Solr directly, mimicking VFBconnect's interface
        
        Args:
            short_forms: List of term IDs to fetch
            return_dataframe: If True, return as pandas DataFrame (not fully implemented)
            summary: If True, return summarized version
            
        Returns:
            List of term info dictionaries
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
                # No need to handle escapes - json.loads does that automatically
                term_info_obj = json.loads(term_info_str)
                results.append(term_info_obj)
                
            except requests.RequestException as e:
                self.logger.error(f"Error fetching data from Solr: {e}")
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON for {short_form}: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error for {short_form}: {e}")
        
        # Handle dataframe conversion if needed (this would need to be implemented)
        if return_dataframe:
            self.logger.warning("return_dataframe=True not fully implemented")
            # You would need to implement pandas DataFrame conversion logic here
            
        return results