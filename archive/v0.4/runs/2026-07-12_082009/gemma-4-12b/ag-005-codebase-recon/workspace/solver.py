import importlib
import sys
import os

# Add current directory to path so we can import from pipeline/
sys.path.append(os.getcwd())

def get_next_module(module_name):
    try:
        # module_name is like "mod_27", but it's in the "pipeline" package
        full_module_name = f"pipeline.{module_name}"
        module = importlib.import_module(full_module_name)
        return getattr(module, 'NEXT', None)
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return None

def solve():
    # Start module is defined in pipeline.entry
    import pipeline.entry as entry
    current_mod = entry.START
    
    visited = []
    curr = current_mod
    
    while curr and len(visited) < 7:
        visited.append(curr)
        if len(visited) == 7:
            break
        curr = get_next_module(curr)
        
    if len(visited) == 7:
        final_mod_name = visited[6]
        print(f"Final module name: {final_mod_name}")
        
        # Get the SECRET_TOKEN of the 7th module
        full_module_name = f"pipeline.{final_mod_name}"
        final_module = importlib.import_module(full_module_name)
        token = getattr(final_module, 'SECRET_TOKEN', None)
        print(f"Token: {token}")
    else:
        print(f"Only visited {len(visited)} modules.")

if __name__ == "__main__":
    solve()
