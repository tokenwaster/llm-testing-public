import importlib.util
import os
import re # Import regex for robust parsing

def get_module_attributes(module_name):
    """Loads a module file and returns its attributes (NEXT, SECRET_TOKEN)."""
    path = f"pipeline/{module_name}.py"
    if not os.path.exists(path):
        return None, None, False

    try:
        # Use exec to load the module's contents into a temporary namespace
        with open(path, 'r') as f:
            code = f.read()
        
        module_namespace = {}
        exec(code, module_namespace)

        next_val = module_namespace.get('NEXT')
        secret_token = module_namespace.get('SECRET_TOKEN')
        return next_val, secret_token, True
    except Exception as e:
        # print(f"Error loading {module_name}: {e}") # Debugging line
        return None, None, False

def solve():
    """Follows the pipeline chain for 7 steps and prints the final SECRET_TOKEN."""
    try:
        with open("pipeline/entry.py", "r") as f:
            content = f.read()
    except FileNotFoundError:
        print("Error: entry.py not found.")
        return

    # Extract START from entry.py using regex for robustness
    start_match = re.search(r'START\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    if start_match:
        start_module = start_match.group(1)
    else:
        print("Error: Could not find START variable in entry.py.")
        return

    current_module = start_module
    visited_tokens = []
    total_modules = 0
    target_count = 7

    print(f"Starting pipeline traversal from module: {start_module}")

    while total_modules < target_count and current_module is not None:
        # 1. Get attributes of the current module
        next_module, secret_token, success = get_module_attributes(current_module)

        if not success or secret_token is None:
            print(f"Failed to read required attributes from {current_module}. Stopping.")
            break

        # 2. Record the token and increment count
        visited_tokens.append(secret_token)
        total_modules += 1
        print(f"Step {total_modules}: Module={current_module}, Token=...{secret_token[-5:]}")

        if total_modules == target_count:
            break

        # 3. Move to the next module
        current_module = next_module

    if total_modules < target_count:
        print(f"Could only visit {total_modules} modules, expected {target_count}.")
        return None

    final_token = visited_tokens[-1]
    return final_token

if __name__ == "__main__":
    result = solve()
    if result:
        with open("answer.txt", "w") as f:
            f.write(result)
        print("\nSuccessfully wrote the 7th module's SECRET_TOKEN to answer.txt.")

