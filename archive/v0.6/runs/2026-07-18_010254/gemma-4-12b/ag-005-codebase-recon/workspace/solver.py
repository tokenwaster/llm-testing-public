import importlib
import sys
import os

# Ensure the pipeline directory is in the path
sys.path.append(os.getcwd())

def get_next_and_token(module_name):
    # module names are like 'mod_27', but they are inside 'pipeline' package
    # However, if I import them as 'pipeline.mod_xx', it might be easier.
    # Let's check how the modules are structured.
    try:
        module = importlib.import_module(f"pipeline.{module_name}")
        next_mod = getattr(module, "NEXT", None)
        token = getattr(module, "SECRET_TOKEN", None)
        return next_mod, token
    except ImportError:
        # Maybe they are just in the pipeline folder and not as submodules?
        # Let's try importing them directly if they were in the root.
        # But they seem to be in a package.
        pass

def solve():
    start_module = "mod_27"
    current_module = start_module
    visited = []
    
    print(f"Starting at: {current_module}")
    
    for i in range(7):
        # Import the module
        module = importlib.import_module(f"pipeline.{current_module}")
        token = getattr(module, "SECRET_TOKEN")
        visited.append((current_module, token))
        print(f"Step {i+1}: Module={current_module}, Token={token}")
        
        next_mod = getattr(module, "NEXT", None)
        if next_mod is None:
            break
        current_module = next_mod

    if len(visited) >= 7:
        print(f"Final token (7th module): {visited[6][1]}")
    else:
        print(f"Chain ended early at step {len(visited)}")

if __name__ == "__main__":
    solve()
