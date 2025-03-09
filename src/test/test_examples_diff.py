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
        return [remove_nulls(item) for item in data if remove_nulls(item) not in [None, {}, []]]
    return data

def main():
    init(autoreset=True)
    
    # Import the results from generated files
    try:
        from test_results import results as json_blocks
        from test_examples import results as python_blocks
    except ImportError as e:
        print(f"{Fore.RED}Error importing test files: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f'Found {len(python_blocks)} Python code blocks')
    print(f'Found {len(json_blocks)} JSON blocks')
    
    if len(python_blocks) != len(json_blocks):
        print(f"{Fore.RED}Error: Number of Python blocks ({len(python_blocks)}) doesn't match JSON blocks ({len(json_blocks)}){Style.RESET_ALL}")
        sys.exit(1)
    
    failed = False
    
    for i, (python_code, expected_json) in enumerate(zip(python_blocks, json_blocks)):
        python_code = stringify_numeric_keys(python_code)
        expected_json = stringify_numeric_keys(expected_json)
        
        # Apply remove_nulls to both dictionaries before diffing
        python_code_filtered = remove_nulls(python_code)
        expected_json_filtered = remove_nulls(expected_json)
        diff = DeepDiff(expected_json_filtered, python_code_filtered, 
                        ignore_order=True, 
                        ignore_numeric_type_changes=True,
                        report_repetition=True,
                        verbose_level=2)
        
        if diff:
            failed = True
            print(f'\n{Fore.RED}Error in example #{i+1}:{Style.RESET_ALL}')
            
            # Print a cleaner diff output with context
            if 'dictionary_item_added' in diff:
                print(f'\n{Fore.GREEN}Added keys:{Style.RESET_ALL}')
                for item in diff['dictionary_item_added']:
                    key = item.replace('root', '')
                    path_parts = key.strip('[]').split('][')
                    
                    # Get the actual value that was added
                    current = python_code
                    for part in path_parts:
                        if part.startswith("'") and part.endswith("'"):
                            part = part.strip("'")
                        elif part.startswith('"') and part.endswith('"'):
                            part = part.strip('"')
                        try:
                            if part.startswith('number:'):
                                part = float(part.split(':')[1])
                            current = current[part]
                        except (KeyError, TypeError):
                            current = '[Unable to access path]'
                            break
                    
                    # Show the key and a brief representation of its value
                    print(f'  {Fore.GREEN}+{key}: {get_brief_dict_representation(current)}{Style.RESET_ALL}')
            
            if 'dictionary_item_removed' in diff:
                print(f'\n{Fore.RED}Removed keys:{Style.RESET_ALL}')
                for item in diff['dictionary_item_removed']:
                    key = item.replace('root', '')
                    path_parts = key.strip('[]').split('][')
                    
                    # Get the actual value that was removed
                    current = expected_json
                    for part in path_parts:
                        if part.startswith("'") and part.endswith("'"):
                            part = part.strip("'")
                        elif part.startswith('"') and part.endswith('"'):
                            part = part.strip('"')
                        try:
                            if part.startswith('number:'):
                                part = float(part.split(':')[1])
                            current = current[part]
                        except (KeyError, TypeError):
                            current = '[Unable to access path]'
                            break
                    
                    print(f'  {Fore.RED}-{key}: {get_brief_dict_representation(current)}{Style.RESET_ALL}')
            
            if 'values_changed' in diff:
                print(f'\n{Fore.YELLOW}Changed values:{Style.RESET_ALL}')
                for key, value in diff['values_changed'].items():
                    path = key.replace('root', '')
                    old_val = value.get('old_value', 'N/A')
                    new_val = value.get('new_value', 'N/A')
                    print(f'  {Fore.YELLOW}{path}:{Style.RESET_ALL}')
                    print(f'    {Fore.RED}- {old_val}{Style.RESET_ALL}')
                    print(f'    {Fore.GREEN}+ {new_val}{Style.RESET_ALL}')
            
            if 'iterable_item_added' in diff:
                print(f'\n{Fore.GREEN}Added list items:{Style.RESET_ALL}')
                for key, value in diff['iterable_item_added'].items():
                    path = key.replace('root', '')
                    # Show the actual content for complex items
                    if isinstance(value, (dict, list)):
                        print(f'  {Fore.GREEN}+{path}:{Style.RESET_ALL}')
                        if isinstance(value, dict):
                            for k, v in value.items():
                                brief_v = get_brief_dict_representation(v)
                                print(f'    {Fore.GREEN}+{k}: {brief_v}{Style.RESET_ALL}')
                        else:
                            # Fixed the problematic line by breaking it into simpler parts
                            items = value[:3]
                            items_str = ", ".join([get_brief_dict_representation(item) for item in items])
                            ellipsis = "..." if len(value) > 3 else ""
                            print(f'    {Fore.GREEN}[{items_str}{ellipsis}]{Style.RESET_ALL}')
                    else:
                        print(f'  {Fore.GREEN}+{path}: {value}{Style.RESET_ALL}')
            
            if 'iterable_item_removed' in diff:
                print(f'\n{Fore.RED}Removed list items:{Style.RESET_ALL}')
                for key, value in diff['iterable_item_removed'].items():
                    path = key.replace('root', '')
                    # Show the actual content for complex items
                    if isinstance(value, (dict, list)):
                        print(f'  {Fore.RED}-{path}:{Style.RESET_ALL}')
                        if isinstance(value, dict):
                            for k, v in value.items():
                                brief_v = get_brief_dict_representation(v)
                                print(f'    {Fore.RED}-{k}: {brief_v}{Style.RESET_ALL}')
                        else:
                            # Fixed the problematic line by breaking it into simpler parts
                            items = value[:3]
                            items_str = ", ".join([get_brief_dict_representation(item) for item in items])
                            ellipsis = "..." if len(value) > 3 else ""
                            print(f'    {Fore.RED}[{items_str}{ellipsis}]{Style.RESET_ALL}')
                    else:
                        print(f'  {Fore.RED}-{path}: {value}{Style.RESET_ALL}')
                    
            # For comparing complex row objects that have significant differences
            if 'iterable_item_added' in diff and 'iterable_item_removed' in diff:
                added_rows = [(k, v) for k, v in diff['iterable_item_added'].items() if 'rows' in k]
                removed_rows = [(k, v) for k, v in diff['iterable_item_removed'].items() if 'rows' in k]
                
                if added_rows and removed_rows:
                    print(f'\n{Fore.YELLOW}Row differences (sample):{Style.RESET_ALL}')
                    # Compare up to 2 rows to show examples of the differences
                    for i in range(min(2, len(added_rows), len(removed_rows))):
                        added_key, added_val = added_rows[i]
                        removed_key, removed_val = removed_rows[i]
                        
                        if isinstance(added_val, dict) and isinstance(removed_val, dict):
                            # Compare the two row objects and show key differences
                            row_diff = compare_objects(removed_val, added_val, f'Row {i}')
                            if row_diff:
                                print(f'  {Fore.YELLOW}Row {i} differences:{Style.RESET_ALL}')
                                for line in row_diff:
                                    print(f'  {line}')
            
            if 'type_changes' in diff:
                print(f'\n{Fore.YELLOW}Type changes:{Style.RESET_ALL}')
                for key, value in diff['type_changes'].items():
                    path = key.replace('root', '')
                    old_type = type(value.get('old_value', 'N/A')).__name__
                    new_type = type(value.get('new_value', 'N/A')).__name__
                    old_val = value.get('old_value', 'N/A')
                    new_val = value.get('new_value', 'N/A')
                    print(f'  {Fore.YELLOW}{path}:{Style.RESET_ALL}')
                    print(f'    {Fore.RED}- {old_type}: {str(old_val)[:100] + "..." if len(str(old_val)) > 100 else old_val}{Style.RESET_ALL}')
                    print(f'    {Fore.GREEN}+ {new_type}: {str(new_val)[:100] + "..." if len(str(new_val)) > 100 else new_val}{Style.RESET_ALL}')
      
            # Print a summary of the differences
            print(f'\n{Fore.YELLOW}Summary of differences:{Style.RESET_ALL}')
            add_keys = len(diff.get('dictionary_item_added', []))
            add_items = len(diff.get('iterable_item_added', {}))
            rem_keys = len(diff.get('dictionary_item_removed', []))
            rem_items = len(diff.get('iterable_item_removed', {}))
            changed_vals = len(diff.get('values_changed', {}))
            type_changes = len(diff.get('type_changes', {}))
            
            print(f'  {Fore.GREEN}Added:{Style.RESET_ALL} {add_keys} keys, {add_items} list items')
            print(f'  {Fore.RED}Removed:{Style.RESET_ALL} {rem_keys} keys, {rem_items} list items')
            print(f'  {Fore.YELLOW}Changed:{Style.RESET_ALL} {changed_vals} values, {type_changes} type changes')

            # After printing the summary, add the formatted output for README
            print(f'\n{Fore.CYAN}Suggested README update for example #{i+1}:{Style.RESET_ALL}')
            
            # Mark a clear copy-paste section
            print(f'\n{Fore.CYAN}--- COPY FROM HERE ---{Style.RESET_ALL}')
            print(format_for_readme(python_code).replace('\033[36m', '').replace('\033[0m', ''))
            print(f'{Fore.CYAN}--- END COPY ---{Style.RESET_ALL}')
      
        else:
            print(f'\n{Fore.GREEN}Example #{i+1}: ✓ PASS{Style.RESET_ALL}')
      
    if failed:
        print(f'\n{Fore.RED}Some examples failed. Please check the differences above.{Style.RESET_ALL}')
        sys.exit(1)
    else:
        print(f'\n{Fore.GREEN}All examples passed!{Style.RESET_ALL}')

if __name__ == "__main__":
    main()
