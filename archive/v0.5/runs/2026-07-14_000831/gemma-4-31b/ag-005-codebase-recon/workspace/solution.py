import importlib

def solve():
    # Start from entry.py
    from pipeline.entry import START
    
    current_module_name = START
    visited_count = 0
    
    while current_module_name is not None and visited_count < 7:
        visited_count += 1
        # Import the module dynamically from the pipeline package
        module_path = f"pipeline.{current_module_name}"
        module = importlib.import_module(module_path)
        
        if visited_count == 7:
            print(f"The 7th module is {current_module_name} and its SECRET_TOKEN is {module.SECRET_TOKEN}")
            return module.SECRET_TOKEN
        
        current_module_name = getattr(module, "NEXT", None)

    if visited_count < 7:
        print(f"Chain ended prematurely at module {current_module_name} after {visited_count} steps.")
        return None

if __name__ == "__main__":
    solve()
