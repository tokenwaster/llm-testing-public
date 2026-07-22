import importlib
import sys
import os

# Add current directory to sys.path to ensure pipeline can be imported
sys.path.append(os.getcwd())

def solve():
    import pipeline.entry as entry
    current_module_name = entry.START
    
    visited_modules = []
    
    for i in range(7):
        # Construct the full module path
        full_module_name = f"pipeline.{current_module_name}"
        
        # Import the module
        try:
            module = importlib.import_module(full_module_name)
            # Reload if already imported (just in case, though not strictly necessary here)
            importlib.reload(module)
        except Exception as e:
            print(f"Error importing {full_module_name}: {e}")
            return

        visited_modules.append(module)
        print(f"Step {i+1}: Visited {full_module_name}, Token: {getattr(module, 'SECRET_TOKEN', 'N/A')}")
        
        # Get the next module name
        next_module_name = getattr(module, 'NEXT', None)
        
        if next_module_name is None:
            print("Reached the end of the chain before 7 modules.")
            break
        
        current_module_name = next_module_name

    if len(visited_modules) == 7:
        target_module = visited_modules[6]
        token = getattr(target_module, 'SECRET_TOKEN', None)
        print(f"Found 7th module token: {token}")
        return token
    else:
        print(f"Chain ended after {len(visited_modules)} modules.")
        return None

if __name__ == "__main__":
    token = solve()
    if token:
        print(f"FINAL_TOKEN:{token}")
