import importlib
import sys
import os

# Add the current directory to sys.path to ensure 'pipeline' can be imported
sys.path.append(os.getcwd())

def solve():
    import pipeline.entry as entry
    current_module_name = entry.START
    
    visited_modules = []
    
    for i in range(7):
        # Construct the full module path
        full_module_path = f"pipeline.{current_module_name}"
        
        try:
            # Import the module
            module = importlib.import_module(full_module_path)
            # Reload if it was already imported (though unlikely in this script)
            importlib.reload(module)
            
            visited_modules.append(module)
            print(f"Step {i+1}: Visited {current_module_name}")
            
            # Get the next module name
            if i < 6: # We only need to find the 7th module's token
                next_module_name = getattr(module, 'NEXT', None)
                if next_module_name is None:
                    print("Reached end of chain prematurely.")
                    break
                current_module_name = next_module_name
            else:
                # We have reached the 7th module
                token = getattr(module, 'SECRET_TOKEN')
                print(f"Found 7th module token: {token}")
                return token
        except Exception as e:
            print(f"Error at step {i+1} ({current_module_name}): {e}")
            break
            
    return None

if __name__ == "__main__":
    token = solve()
    if token:
        print(f"FINAL_TOKEN:{token}")
    else:
        print("Failed to find token.")
