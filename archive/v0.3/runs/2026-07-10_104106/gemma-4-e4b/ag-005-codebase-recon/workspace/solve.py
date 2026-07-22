import importlib.util
import os

# Define the path to the pipeline package root
PACKAGE_ROOT = "pipeline"

def get_module_source(module_name):
    """Reads the source code of a module within the pipeline directory."""
    path = os.path.join(PACKAGE_ROOT, f"{module_name}.py")
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Module {module_name} not found.")
        return None

def find_next_and_secret(source_code):
    """Parses the source code to extract NEXT and SECRET_TOKEN."""
    # Simple regex/string search approach is safer than full AST parsing here,
    # given the structure seems consistent (constant assignments).
    
    next_module = None
    secret_token = None

    # Extract NEXT
    if "NEXT = \"" in source_code:
        start_index = source_code.find("NEXT = \"") + len("NEXT = \"")
        end_index = source_code.find("\"", start_index)
        next_module = source_code[start_index:end_index]

    # Extract SECRET_TOKEN (assuming it's the last defined constant or easily identifiable)
    if "SECRET_TOKEN = \"" in source_code:
        start_index = source_code.find("SECRET_TOKEN = \"") + len("SECRET_TOKEN = \"")
        end_index = source_code.find("\"", start_index)
        secret_token = source_code[start_index:end_index]

    return next_module, secret_token

def solve():
    # 1. Get the starting module name from entry.py
    entry_source = get_module_source("entry")
    if not entry_source:
        print("Could not read entry.py.")
        return None, None

    start_name = None
    if "START = \"" in entry_source:
        start_index = entry_source.find("START = \"") + len("START = \"")
        end_index = entry_source.find("\"", start_index)
        start_name = entry_source[start_index:end_index]

    if not start_name:
        print("Could not find START in entry.py.")
        return None, None

    current_module = start_name
    chain = []
    target_length = 7
    
    print(f"Starting chain traversal from: {start_name}")

    for i in range(target_length):
        if not current_module:
            print(f"Chain ended prematurely at step {i}.")
            return None, None

        # Read the module source
        source = get_module_source(current_module)
        if source is None:
            print(f"Failed to read source for {current_module}. Stopping.")
            return None, None

        # Find tokens
        next_module, secret_token = find_next_and_secret(source)
        
        chain.append({
            'name': current_module, 
            'secret_token': secret_token, 
            'next': next_module
        })

        print(f"Step {i+1}/{target_length}: Module={current_module}, Token='{secret_token}', Next={next_module}")

        # Move to the next module
        if i < target_length - 1:
            current_module = next_module
        else:
            break # Reached the 7th module (index 6)

    # The 7th module is the last element in the chain list
    seventh_module_data = chain[-1]
    return seventh_module_data['secret_token'], None

if __name__ == "__main__":
    token, _ = solve()
    if token:
        print(f"Found SECRET_TOKEN of the 7th module: {token}")
    else:
        print("Failed to find the required token.")