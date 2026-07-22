import importlib
import os

def find_token():
    # Start with the value of START from entry.py
    # Since I can't easily import it without knowing if it's in a package, 
    # I'll just read it manually or use a simple approach.
    
    # Let's try to find the start module name by reading entry.py
    with open('pipeline/entry.py', 'r') as f:
        content = f.read()
        # Find START = "..."
        import re
        start_match = re.search(r'START\s*=\s*["\']([^"\']+)["\']', content)
        if not start_match:
            raise ValueError("Could not find START in entry.py")
        current_module_name = start_match.group(1)

    visited_count = 0
    target_token = None

    while current_module_name is not None and visited_count < 7:
        visited_count += 1
        print(f"Visiting {current_module_name} (Visit #{visited_count})")
        
        # Import the module dynamically
        module_path = f"pipeline.{current_module_name}"
        try:
            module = importlib.import_module(module_path)
            token = getattr(module, 'SECRET_TOKEN', None)
            next_module = getattr(module, 'NEXT', None)
            
            if token is None:
                print(f"Warning: No SECRET_TOKEN found in {current_module_name}")
            
            if visited_count == 7:
                target_token = token
                break
                
            current_module_name = next_module
        except Exception as e:
            print(f"Error importing {module_path}: {e}")
            break

    return target_token

if __name__ == "__main__":
    token = find_token()
    if token:
        with open('answer.txt', 'w') as f:
            f.write(token)
        print(f"Successfully wrote token {token} to answer.txt")
    else:
        print("Failed to find the 7th module's token.")
