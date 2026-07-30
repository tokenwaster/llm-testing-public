import importlib
import sys
import os

def follow_chain(start_module_name, count):
    current_module_name = start_module_name
    visited_count = 0
    last_token = None

    while current_module_name is not None and visited_count < count:
        visited_count += 1
        print(f"Visiting {current_module_name} (Count: {visited_count})")
        
        try:
            # Construct the module path. The modules are in 'pipeline' package.
            module_path = f"pipeline.{current_module_name}"
            module = importlib.import_module(module_path)
            
            last_token = getattr(module, "SECRET_TOKEN")
            next_module_name = getattr(module, "NEXT", None)
            
            if visited_count < count:
                current_module_name = next_module_name
            else:
                # We've reached the 7th module
                pass

        except Exception as e:
            print(f"Error accessing {current_module_name}: {e}")
            break

    return last_token, visited_count

if __name__ == "__main__":
    # Hardcoded START from entry.py for now or I could read it properly.
    # Since I already read it: START = "mod_27"
    start_node = "mod_27"
    target_count = 7
    
    token, actual_visited = follow_chain(start_node, target_count)
    print(f"Final Token: {token}")
    print(f"Total visited: {actual_visited}")
