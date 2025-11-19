import sys
import json
import vfbquery as vfb
from deepdiff import DeepDiff
from io import StringIO
from colorama import Fore, Back, Style, init
import numpy as np

# Custom JSON encoder to handle NumPy types
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
        return super(NumpyEncoder, self).default(obj)

def get_brief_dict_representation(d, max_items=3, max_len=50):
    '''Create a brief representation of a dictionary'''
    if not isinstance(d, dict):
        return str(d)[:max_len] + '...' if len(str(d)) > max_len else str(d)
    
    items = list(d.items())[:max_items]
    brief = '{' + ', '.join(f"'{k}': {get_brief_dict_representation(v)}" for k, v in items)
    if len(d) > max_items:
        brief += ', ...'
    brief += '}'
    return brief[:max_len] + '...' if len(brief) > max_len else brief

def compare_objects(obj1, obj2, path=''):
    '''Compare two complex objects and return a human-readable diff'''
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        result = []
        all_keys = set(obj1.keys()) | set(obj2.keys())
        
        for k in all_keys:
            key_path = f'{path}.{k}' if path else k
            if k not in obj1:
                result.append(f'  {Fore.GREEN}+ {key_path}: {get_brief_dict_representation(obj2[k])}{Style.RESET_ALL}')
            elif k not in obj2:
                result.append(f'  {Fore.RED}- {key_path}: {get_brief_dict_representation(obj1[k])}{Style.RESET_ALL}')
            else:
                if obj1[k] != obj2[k]:
                    sub_diff = compare_objects(obj1[k], obj2[k], key_path)
                    if sub_diff:
                        result.extend(sub_diff)
        return result
    elif isinstance(obj1, list) and isinstance(obj2, list):
        if len(obj1) != len(obj2) or obj1 != obj2:
            return [f'  {Fore.YELLOW}~ {path}: Lists differ in length or content{Style.RESET_ALL}',
                    f'    {Fore.RED}- List 1: {len(obj1)} items{Style.RESET_ALL}',
                    f'    {Fore.GREEN}+ List 2: {len(obj2)} items{Style.RESET_ALL}']
        return []
    else:
        if obj1 != obj2:
            return [f'  {Fore.YELLOW}~ {path}:{Style.RESET_ALL}',
                    f'    {Fore.RED}- {obj1}{Style.RESET_ALL}',
                    f'    {Fore.GREEN}+ {obj2}{Style.RESET_ALL}']
        return []

def stringify_numeric_keys(obj):
    """Convert numeric dictionary keys to strings in nested objects"""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # Convert numeric keys to strings
            if isinstance(k, (int, float)):
                key = str(k)
            else:
                key = k
            # Recursively process nested structures
            result[key] = stringify_numeric_keys(v)
        return result
    elif isinstance(obj, list):
        return [stringify_numeric_keys(item) for item in obj]
    else:
        return obj

def format_for_readme(data):
    """Format data as nicely formatted JSON for README.md"""
    try:
        # First stringify any numeric dictionary keys
        data_with_string_keys = stringify_numeric_keys(data)
        
        # Remove keys with null values
        data_filtered = remove_nulls(data_with_string_keys)
        
        # Use json.dumps with indentation for pretty printing
        # Use custom encoder to handle NumPy types
        formatted = json.dumps(data_filtered, indent=3, cls=NumpyEncoder)
        
        # Replace 'true' and 'false' with 'True' and 'False' for Python compatibility
        formatted = formatted.replace('true', 'True').replace('false', 'False')
        
        # Format as markdown code block
        result = "```json\n" + formatted + "\n```"
        return result
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"

def sort_rows_in_data(data):
    """Sort rows in data structures by id to ensure consistent ordering"""
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k == 'rows' and isinstance(v, list):
                # Sort rows by id if they have id field
                try:
                    sorted_rows = sorted(v, key=lambda x: x.get('id', '') if isinstance(x, dict) else str(x))
                    result[k] = sorted_rows
                except (TypeError, AttributeError):
                    result[k] = v
            else:
                result[k] = sort_rows_in_data(v)
        return result
    elif isinstance(data, list):
        return [sort_rows_in_data(item) for item in data]
    else:
        return data

def remove_nulls(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            cleaned = remove_nulls(v)
            # Skip None, empty dicts or empty lists
            if cleaned is None or cleaned == {} or cleaned == []:
                continue
            new_dict[k] = cleaned
        return new_dict
    elif isinstance(data, list):
        filtered = []
        for item in data:
            cleaned_item = remove_nulls(item)
            if cleaned_item is not None and cleaned_item != {} and cleaned_item != []:
                filtered.append(cleaned_item)
        return filtered
    return data

def main():
    init(autoreset=True)
    
    # Import the python code blocks
    try:
        from .test_examples_code import results as python_blocks
    except ImportError as e:
        print(f"{Fore.RED}Error importing test files: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f'Found {len(python_blocks)} Python code blocks')
    
    failed = False
    
    for i, python_code in enumerate(python_blocks):
        
        print(f'\n{Fore.CYAN}Example #{i+1}:{Style.RESET_ALL}')
        print(f'  README query: {python_code}')
        
        # Execute the python code and get result
        try:
            # Evaluate the code to get the result
            result = eval(python_code)
            
            # Validate structure based on function
            if 'get_term_info' in python_code:
                # Should be a dict with specific keys
                if not isinstance(result, dict):
                    print(f'{Fore.RED}get_term_info should return a dict{Style.RESET_ALL}')
                    failed = True
                    continue
                
                expected_keys = ['IsIndividual', 'IsClass', 'Images', 'Examples', 'Domains', 'Licenses', 'Publications', 'Synonyms']
                for key in expected_keys:
                    if key not in result:
                        print(f'{Fore.RED}Missing key: {key}{Style.RESET_ALL}')
                        failed = True
                    elif key in ['IsIndividual', 'IsClass'] and not isinstance(result[key], bool):
                        print(f'{Fore.RED}Key {key} is not bool: {type(result[key])}{Style.RESET_ALL}')
                        failed = True
                
                if 'SuperTypes' in result and not isinstance(result['SuperTypes'], list):
                    print(f'{Fore.RED}SuperTypes is not list{Style.RESET_ALL}')
                    failed = True
                
                if 'Queries' in result and not isinstance(result['Queries'], list):
                    print(f'{Fore.RED}Queries is not list{Style.RESET_ALL}')
                    failed = True
            
            elif 'get_instances' in python_code:
                # Should be a list of dicts or a dict with rows
                if isinstance(result, list):
                    if len(result) > 0 and not isinstance(result[0], dict):
                        print(f'{Fore.RED}get_instances items should be dicts{Style.RESET_ALL}')
                        failed = True
                elif isinstance(result, dict):
                    # Check if it has 'rows' key
                    if 'rows' not in result:
                        print(f'{Fore.RED}get_instances dict should have "rows" key{Style.RESET_ALL}')
                        failed = True
                    elif not isinstance(result['rows'], list):
                        print(f'{Fore.RED}get_instances "rows" should be list{Style.RESET_ALL}')
                        failed = True
                else:
                    print(f'{Fore.RED}get_instances should return a list or dict, got {type(result)}{Style.RESET_ALL}')
                    failed = True
                    continue
            
            elif 'get_templates' in python_code:
                # Should be a dict with rows
                if not isinstance(result, dict):
                    print(f'{Fore.RED}get_templates should return a dict{Style.RESET_ALL}')
                    failed = True
                    continue
                
                if 'rows' not in result:
                    print(f'{Fore.RED}get_templates dict should have "rows" key{Style.RESET_ALL}')
                    failed = True
                elif not isinstance(result['rows'], list):
                    print(f'{Fore.RED}get_templates "rows" should be list{Style.RESET_ALL}')
                    failed = True
            
            else:
                print(f'{Fore.RED}Unknown function in code{Style.RESET_ALL}')
                failed = True
                continue
            
            if not failed:
                print(f'{Fore.GREEN}Structure validation passed{Style.RESET_ALL}')
            
        except Exception as e:
            print(f'{Fore.RED}Error executing code: {e}{Style.RESET_ALL}')
            failed = True
    
    if failed:
        print(f'\n{Fore.RED}Some tests failed{Style.RESET_ALL}')
        sys.exit(1)
    else:
        print(f'\n{Fore.GREEN}All tests passed{Style.RESET_ALL}')

if __name__ == "__main__":
    main()
