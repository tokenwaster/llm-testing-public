import re
import os

def solve():
    # 1. Get START from entry.py
    try:
        with open("pipeline/entry.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: pipeline/entry.py not found.")
        return

    start_match = re.search(r'START\s*=\s*["\']([^"\']+)["\']', content)
    if not start_match:
        print("Error: START variable not found in entry.py")
        return

    current_module_name = start_match.group(1)
    
    chain_length = 7
    secret_tokens = []
    
    for i in range(chain_length):
        if not current_module_name:
            print(f"Chain ended prematurely at step {i+1}. Current module name is None.")
            return

        file_path = f"pipeline/{current_module_name}.py"
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: Module file {file_path} not found.")
            return

        # Extract SECRET_TOKEN (must be quoted)
        secret_token_match = re.search(r'SECRET_TOKEN\s*=\s*(["\'])(.*?)\1', content)
        if not secret_token_match:
            print(f"Error: SECRET_TOKEN not found in {current_module_name}.")
            return
        secret_token = secret_token_match.group(2)

        # Extract NEXT (handles quoted or unquoted strings, capturing the value)
        next_module = None
        # Look for NEXT = VALUE where VALUE can be quoted or unquoted identifier/string
        # Group 1: optional quote type (' or ")
        # Group 2: the actual content of the next module name
        next_module_match = re.search(r'NEXT\s*=\s*(["\']?)(.*?)\2', content)
        if next_module_match:
            potential_next = next_module_match.group(2).strip()
            # If the value is not empty and not explicitly 'None' (case insensitive), treat it as the next module name.
            if potential_next and potential_next.lower() != 'none':
                next_module = potential_next

        # Store the token for this step (this is the i+1 module's token)
        secret_tokens.append(secret_token)
        print(f"Step {i+1}/{chain_length}: Module={current_module_name}, Token='{secret_token}', Next={next_module}")

        # Move to the next module
        if i < chain_length - 1:
            current_module_name = next_module
        else:
            break # Reached the target length

    # The token of the 7th module is the last one collected.
    final_token = secret_tokens[-1]
    print(f"Successfully traversed {len(secret_tokens)} modules.")
    print(f"The SECRET_TOKEN of the 7th module is: {final_token}")

    # Write the result to answer.txt
    with open("answer.txt", "w") as f:
        f.write(final_token)

solve()