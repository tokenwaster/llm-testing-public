import importlib
import sys
import os

# Ensure the pipeline package is in the path
sys.path.append(os.getcwd())

def get_next_and_token(module_name):
    try:
        # module names are like 'mod_27', so we need to import them from 'pipeline'
        module = importlib.import_module(f"pipeline.{module_name}")
        return getattr(module, "NEXT"), getattr(module, "SECRET_TOKEN")
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return None, None

def solve():
    current_module = "mod_27" # From entry.py
    visited = []
    
    for i in range(7):
        visited.append(current_module)
        next_mod, token = get_next_and_token(current_module)
        if next_mod is None:
            break
        current_module = next_mod
    
    # The 7th module visited is the last one in our list (since we loop 7 times)
    # Wait, if I loop 7 times and append each time, the 7th one will be at index 6.
    print(f"Visited chain: {visited}")
    print(f"7th module: {visited[6]}")
    
    # The token of the 7th module is what we need.
    # Let's re-run logic to get the token specifically for the 7th one.
    _, final_token = get_next_and_token(visited[6])
    print(f"Token: {final_token}")

if __name__ == "__main__":
    solve()
