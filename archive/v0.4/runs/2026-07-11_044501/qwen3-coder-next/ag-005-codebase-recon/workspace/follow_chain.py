"""Script to follow the pipeline chain and find the 7th module's SECRET_TOKEN."""

import os
import sys

# Add the pipeline directory to the path
sys.path.insert(0, os.path.join(os.getcwd(), 'pipeline'))

def get_module_info(module_name):
    """Import a module and extract NEXT and SECRET_TOKEN."""
    try:
        # Import the module
        module = __import__(module_name)
        
        # Get NEXT (default to None if not defined)
        next_module = getattr(module, 'NEXT', None)
        
        # Get SECRET_TOKEN
        secret_token = getattr(module, 'SECRET_TOKEN', None)
        
        return {
            'name': module_name,
            'next': next_module,
            'token': secret_token
        }
    except ImportError as e:
        print(f"Error importing {module_name}: {e}")
        return None

def follow_chain(start_module, steps=7):
    """Follow the chain for a specified number of steps."""
    current_module = start_module
    visited = []
    
    for i in range(steps):
        info = get_module_info(current_module)
        if info is None:
            print(f"Failed to load module: {current_module}")
            break
        
        visited.append(info)
        print(f"Step {i+1}: Module={info['name']}, Token={info['token'][:20]}...")
        
        # Move to the next module
        if info['next'] is None:
            print("Reached end of chain!")
            break
        
        current_module = info['next']
    
    return visited

# Start from mod_27 (as defined in entry.py)
start_module = "mod_27"
chain = follow_chain(start_module, 7)

print("\n" + "="*60)
if len(chain) >= 7:
    print(f"The 7th module is: {chain[6]['name']}")
    print(f"SECRET_TOKEN: {chain[6]['token']}")
else:
    print(f"Only visited {len(chain)} modules")
