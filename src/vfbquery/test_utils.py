import pandas as pd
from typing import Any, Dict, Union

def safe_extract_row(result: Any, index: int = 0) -> Dict:
    """
    Safely extract a row from a pandas DataFrame or return the object itself if not a DataFrame.
    
    :param result: Result to extract from (DataFrame or other object)
    :param index: Index of the row to extract (default: 0)
    :return: Extracted row as dict or original object
    """
    if isinstance(result, pd.DataFrame):
        if not result.empty and len(result.index) > index:
            return result.iloc[index].to_dict()
        else:
            return {}
    return result

def patch_vfb_connect_query_wrapper():
    """
    Apply monkey patches to VfbConnect.neo_query_wrapper to make it handle DataFrame results safely.
    Call this function in test setup if tests are expecting dictionary results from neo_query_wrapper methods.
    """
    try:
        from vfb_connect.neo.query_wrapper import NeoQueryWrapper
        original_get_term_info = NeoQueryWrapper._get_TermInfo
        
        def patched_get_term_info(self, terms, *args, **kwargs):
            result = original_get_term_info(self, terms, *args, **kwargs)
            if isinstance(result, pd.DataFrame):
                # Return list of row dictionaries instead of DataFrame
                return [row.to_dict() for i, row in result.iterrows()]
            return result
            
        NeoQueryWrapper._get_TermInfo = patched_get_term_info
        
        print("VfbConnect query wrapper patched for testing")
    except ImportError:
        print("Could not patch VfbConnect - module not found")
