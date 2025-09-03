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

def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize any data structure to make it JSON serializable.
    Converts numpy types, pandas types, and other non-serializable types to native Python types.
    
    :param obj: Object to sanitize
    :return: JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif hasattr(obj, 'item'):  # Handle pandas scalar types
        return obj.item()
    elif isinstance(obj, pd.DataFrame):
        return safe_to_dict(obj)
    elif hasattr(obj, '__dict__'):  # Handle custom objects
        return sanitize_for_json(obj.__dict__)
    else:
        return obj

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize any object to JSON string, handling numpy and pandas types.
    
    :param obj: Object to serialize
    :param kwargs: Additional arguments to pass to json.dumps
    :return: JSON string
    """
    # Set default arguments
    default_kwargs = {'indent': 2, 'ensure_ascii': False, 'cls': NumpyEncoder}
    default_kwargs.update(kwargs)
    
    try:
        # First try with the NumpyEncoder
        return json.dumps(obj, **default_kwargs)
    except (TypeError, ValueError):
        # If that fails, sanitize the object first
        sanitized_obj = sanitize_for_json(obj)
        return json.dumps(sanitized_obj, **default_kwargs)

def pretty_print_vfb_result(result: Any, max_length: int = 1000) -> None:
    """
    Pretty print any VFB query result in a safe, readable format.
    
    :param result: Result from any VFB query function
    :param max_length: Maximum length of output (truncates if longer)
    """
    try:
        json_str = safe_json_dumps(result)
        if len(json_str) > max_length:
            print(json_str[:max_length] + f'\n... (truncated, full length: {len(json_str)} characters)')
        else:
            print(json_str)
    except Exception as e:
        print(f'Error printing result: {e}')
        print(f'Result type: {type(result)}')
        if hasattr(result, '__dict__'):
            print(f'Result attributes: {list(result.__dict__.keys())}')
        else:
            print(f'Result: {str(result)[:max_length]}...')

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
