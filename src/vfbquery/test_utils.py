import pandas as pd
import json
import numpy as np
from typing import Any, Dict, Union

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

def safe_to_dict(df):
    """Convert DataFrame to dict with numpy types converted to native Python types"""
    if isinstance(df, pd.DataFrame):
        # Convert numpy dtypes to native Python types
        df_copy = df.copy()
        for col in df_copy.columns:
            if df_copy[col].dtype.name.startswith('int'):
                df_copy[col] = df_copy[col].astype('object')
            elif df_copy[col].dtype.name.startswith('float'):
                df_copy[col] = df_copy[col].astype('object')
        return df_copy.to_dict("records")
    return df

def safe_extract_row(result: Any, index: int = 0) -> Dict:
    """
    Safely extract a row from a pandas DataFrame or return the object itself if not a DataFrame.
    
    :param result: Result to extract from (DataFrame or other object)
    :param index: Index of the row to extract (default: 0)
    :return: Extracted row as dict or original object
    """
    if isinstance(result, pd.DataFrame):
        if not result.empty and len(result.index) > index:
            # Convert to dict using safe method to handle numpy types
            row_series = result.iloc[index]
            return {col: (val.item() if hasattr(val, 'item') else val) for col, val in row_series.items()}
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
                # Return list of row dictionaries instead of DataFrame using safe conversion
                return safe_to_dict(result)
            return result
            
        NeoQueryWrapper._get_TermInfo = patched_get_term_info
        
        print("VfbConnect query wrapper patched for testing")
    except ImportError:
        print("Could not patch VfbConnect - module not found")
