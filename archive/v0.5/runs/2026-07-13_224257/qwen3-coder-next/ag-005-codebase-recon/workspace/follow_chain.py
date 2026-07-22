"""Script to follow the pipeline chain and find the 7th module's SECRET_TOKEN."""

import os
import sys

# Add the pipeline directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'pipeline'))

def get_module_info(module_name):
    """Import a module and extract NEXT and SECRET_TOKEN."""
    try:
        # Import the module
        mod = __import__(module_name)
        
        # Get NEXT (default to None if not defined)
        next_mod = getattr(mod, 'NEXT', None)
        
        # Get SECRET_TOKEN
        secret_token = getattr(mod, 'SECRET_TOKEN', None)
        
        return {
            'name': module_name,
            'next': next_mod,
            'token': secret_token
        }
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
        return None

def follow_chain(start_module, steps=7):
    """Follow the chain for the specified number of steps."""
    current = start_module
    visited = []
    
    for i in range(steps):
        info = get_module_info(current)
        if info is None:
            print(f"Failed to get module: {current}")
            return None
        
        visited.append(info)
        print(f"Step {i+1}: {info['name']} - Token: {info['token'][:20]}...")
        
        # Move to next module
        if info['next'] is None:
            print(f"Chain ended at step {i+1} (module {current})")
            return visited
        
        current = info['next']
    
    return visited

# Get START from entry.py
import entry
start_module = entry.START

print(f"Starting chain from: {start_module}")
print(f"Finding the 7th module's SECRET_TOKEN...\n")

result = follow_chain(start_module, 7)

if result and len(result) >= 7:
    seventh_token = result[6]['token']  # Index 6 is the 7th element
    print(f"\n{'='*50}")
    print(f"7th module: {result[6]['name']}")
    print(f"SECRET_TOKEN: {seventh_token}")
    print(f"{'='*50}")
    
    # Write to answer.txt
    with open('answer.txt', 'w') as f:
        f.write(seventh_token)
    print("\nToken written to answer.txt")
else:
    print("Failed to get 7 modules in the chain")
