import re
import json
import os.path

def extract_code_blocks(readme_path):
    """
    Extracts Python code blocks and JSON blocks from a README.md file
    and returns them as separate lists.
    """
    if not os.path.isfile(readme_path):
        raise FileNotFoundError(f"README file not found at {readme_path}")
        
    with open(readme_path, 'r') as f:
        content = f.read()
    
    # Extract Python code blocks with proper anchoring to avoid nested confusion
    python_pattern = r'```python\s*(.*?)\s*```'
    python_blocks = re.findall(python_pattern, content, re.DOTALL)
    
    # Extract JSON code blocks with proper anchoring
    json_pattern = r'```json\s*(.*?)\s*```'
    json_blocks = re.findall(json_pattern, content, re.DOTALL)
    
    # Process Python blocks to extract vfb calls
    processed_python_blocks = []
    for block in python_blocks:
        # Look for vfb.* calls and extract them
        vfb_calls = re.findall(r'(vfb\.[^)]*\))', block)
        if vfb_calls:
            processed_python_blocks.extend(vfb_calls)
    
    # Process JSON blocks
    processed_json_blocks = []
    for block in json_blocks:
        try:
            # Clean up the JSON text
            json_text = block.strip()
            # Convert Python boolean literals to JSON booleans using regex
            json_text = re.sub(r'\bTrue\b', 'true', json_text)
            json_text = re.sub(r'\bFalse\b', 'false', json_text)
            # Parse the JSON and add to results
            json_obj = json.loads(json_text)
            processed_json_blocks.append(json_obj)
        except json.JSONDecodeError as e:
            # Determine a context range around the error position
            start = max(e.pos - 20, 0)
            end = e.pos + 20
            context = json_text[start:end]
            print(f"Error parsing JSON block: {e.msg} at line {e.lineno} column {e.colno} (char {e.pos})")
            print(f"Context: ...{context}...")
    
    return processed_python_blocks, processed_json_blocks

def generate_python_file(python_blocks, output_path):
    """
    Generates a Python file containing the extracted code blocks wrapped in a results list.
    """
    with open(output_path, 'w') as f:
        f.write('import vfbquery as vfb\n\n')  # Add import statement
        f.write('results = []\n')
        for block in python_blocks:
            f.write(f'results.append({block})\n')

def generate_json_file(json_blocks, output_path):
    """
    Generates a Python file containing the extracted JSON blocks as a Python list.
    """
    with open(output_path, 'w') as f:
        f.write('from src.vfbquery.term_info_queries import *\n')
        f.write('results = ')
        
        # Convert JSON list to Python compatible string
        # This handles 'null' conversion to 'None' and other JSON->Python differences
        python_list = str(json_blocks)
        # Replace true/false with True/False
        python_list = python_list.replace('true', 'True').replace('false', 'False')
        # Replace null with None
        python_list = python_list.replace('null', 'None')
        
        f.write(python_list)

def process_readme(readme_path, python_output_path, json_output_path):
    """
    Process the README file and generate the test files.
    """
    python_blocks, json_blocks = extract_code_blocks(readme_path)
    generate_python_file(python_blocks, python_output_path)
    generate_json_file(json_blocks, json_output_path)
    
    return len(python_blocks), len(json_blocks)

if __name__ == "__main__":
    # Example usage
    readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'README.md')
    python_blocks, json_blocks = extract_code_blocks(readme_path)
    
    python_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_examples.py')
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_results.py')
    
    generate_python_file(python_blocks, python_path)
    generate_json_file(json_blocks, json_path)
    
    print(f"Extracted {len(python_blocks)} Python blocks and {len(json_blocks)} JSON blocks")
