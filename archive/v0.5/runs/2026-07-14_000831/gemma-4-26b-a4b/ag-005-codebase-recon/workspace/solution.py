import importlib
import sys
import os

# Add current directory to sys.path so we can import pipeline
sys.path.append(os.getcwd())

def solve():
    # Import entry to get START
    import pipeline.entry as entry
    current_module_name = entry.START
    
    visited_count = 1
    target_count = 7
    
    print(f"Starting with: {current_module_name}")

    while visited_count < target_count:
        # Import the current module
        module_path = f"pipeline.{current_module_name}"
        try:
            module = importlib.import_module(module_path)
            # Reload to ensure we get fresh content if needed, 
            # though not strictly necessary here as it's a single run
            importlib.reload(module)
            
            next_module_name = getattr(module, 'NEXT', None)
            
            if next_module_name is None:
                print("Reached the end of the chain before 7 modules.")
                break
            
            current_module_name = next_module_name
            visited_count += 1
            print(f"Step {visited_count}: Moving to {current_module_name}")
            
        except Exception as e:
            print(f"Error: {e}")
            break

    # Now we are at the 7th module (or stopped early)
    if visited_count == target_count:
        module_path = f"pipeline.{current_module_name}"
        module = importlib.import_module(module_path)
        importlib.reload(module)
        token = getattr(module, 'SECRET_TOKEN')
        print(f"Found token: {token}")
        with open('answer.txt', 'w') as f:
            f.write(str(token))
    else:
        print("Failed to reach 7 modules.")

if __name__ == "__main__":
    solve()
