import importlib
import sys
import os

# Add the current directory to path if necessary for relative imports, 
# although since we are running a script that uses modules within 'pipeline', 
# standard package handling should suffice if we treat them as local modules.

def solve():
    """Follows the pipeline chain for 7 steps and prints the final SECRET_TOKEN."""
    
    try:
        # Get START from entry.py (or assume it's available)
        with open("pipeline/entry.py", "r") as f:
            content = f.read()
        
        start_line = [line for line in content.splitlines() if 'START =' in line]
        if not start_line:
            print("Error: START constant not found in pipeline/entry.py")
            return

        start_module_name = start_line[0].split('=')[-1].strip().strip('"').strip("'")
        
    except Exception as e:
        print(f"Error reading entry.py: {e}")
        return

    current_module_name = start_module_name
    chain = []
    target_length = 7
    
    print(f"Starting chain traversal at module: {start_module_name}")

    for i in range(target_length):
        if current_module_name is None:
            print(f"Chain ended prematurely at step {i}. Expected {target_length} steps.")
            return

        try:
            # Dynamically import the module. Assuming they are named mod_XX and reside in 'pipeline'.
            module_path = f"pipeline.{current_module_name}"
            
            # Use importlib to load the module dynamically
            module = importlib.import_module(module_path)
            
        except ModuleNotFoundError:
            print(f"Error: Could not find module {module_path}")
            return
        except Exception as e:
            print(f"Error loading module {current_module_name}: {e}")
            return

        # 1. Record the token of the current module (this is the i+1-th module)
        try:
            secret_token = getattr(module, 'SECRET_TOKEN')
            chain.append((i + 1, secret_token))
            print(f"Step {i+1}/{target_length}: Visited {current_module_name}. Token found.")
        except AttributeError:
            print(f"Error: Module {current_module_name} does not define SECRET_TOKEN.")
            return

        # 2. Determine the next module name
        try:
            next_module = getattr(module, 'NEXT')
        except AttributeError:
            print(f"Error: Module {current_module_name} does not define NEXT.")
            return

        if i < target_length - 1:
            if next_module is None:
                print(f"Chain ended unexpectedly at step {i+1}. Expected more steps.")
                return
            current_module_name = next_module
        else:
            # We reached the target length, no need to check NEXT for further traversal
            pass

    # After 7 successful steps, the last recorded token is the answer.
    if len(chain) == target_length:
        final_token = chain[-1][1]
        print("\\n--- SUCCESS ---")
        print(f"Successfully visited {target_length} modules.")
        print(f"The SECRET_TOKEN of the 7th module is: {final_token}")
    else:
        print("Failed to complete the chain traversal.")

solve()