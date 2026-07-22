"""Walk the pipeline chain to find the 7th module's SECRET_TOKEN."""

import os
import re

# Start with the entry point from entry.py
START = "mod_27"

def get_module_info(module_name):
    """Parse a module file to extract NEXT and SECRET_TOKEN."""
    filepath = f"pipeline/{module_name}.py"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Extract SECRET_TOKEN
    token_match = re.search(r'SECRET_TOKEN\s*=\s*"([^"]+)"', content)
    secret_token = token_match.group(1) if token_match else None
    
    # Extract NEXT
    next_match = re.search(r'NEXT\s*=\s*"([^"]+)"', content)
    next_module = next_match.group(1) if next_match else None
    
    return {
        'name': module_name,
        'NEXT': next_module,
        'SECRET_TOKEN': secret_token
    }

# Walk the chain
current = START
chain = []

for i in range(7):
    info = get_module_info(current)
    chain.append(info)
    print(f"Step {i+1}: {info['name']} - Token: {info['SECRET_TOKEN']}")
    
    if info['NEXT'] is None:
        print("Reached end of chain!")
        break
    current = info['NEXT']

print("\n--- Summary ---")
print(f"The 7th module in the chain is: {chain[6]['name']}")
print(f"SECRET_TOKEN: {chain[6]['SECRET_TOKEN']}")

# Write to answer.txt
with open('answer.txt', 'w') as f:
    f.write(chain[6]['SECRET_TOKEN'])

print("\nWritten to answer.txt")
