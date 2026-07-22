import importlib

def solve():
    # Import entry to get START
    entry = importlib.import_module('pipeline.entry')
    current_module_name = entry.START
    
    visited_count = 0
    last_token = None

    while current_module_name is not None:
        visited_count += 1
        # Construct the full module path
        full_module_path = f"pipeline.{current_module_name}"
        
        try:
            module = importlib.import_module(full_module_path)
        except ImportError as e:
            print(f"Error importing {full_module_path}: {e}")
            break

        last_token = module.SECRET_TOKEN
        
        if visited_count == 7:
            print(f"Found 7th module: {current_module_name}")
            print(f"Token: {last_token}")
            return last_token

        # Move to the next module
        current_module_name = getattr(module, 'NEXT', None)

    print("Reached end of chain before 7 modules.")
    return None

if __name__ == "__main__":
    token = solve()
    if token:
        with open('answer.txt', 'w') as f:
            f.write(token)
