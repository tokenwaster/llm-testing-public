import importlib
import sys
import os

def get_module_content(module_name):
    """Reads the content of a specific module file within the pipeline package."""
    # Assuming all modules are directly accessible under 'pipeline/mod_XX.py'
    path = f"pipeline/{module_name}.py"
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Module file not found at {path}")
        sys.exit(1)

def get_constant_value(content, constant_name):
    """Uses exec to find the value of a constant in the module content."""
    local_scope = {}
    try:
        # Execute the content in a controlled scope
        exec(content, {}, local_scope)
        return local_scope.get(constant_name)
    except Exception as e:
        print(f"Error executing code for {constant_name}: {e}")
        sys.exit(1)

def solve():
    # 1. Get the starting module name
    try:
        start_content = get_module_content("entry")
        start_node_name = get_constant_value(start_content, "START")
    except Exception as e:
        print(f"Could not read START from entry.py: {e}")
        return

    if start_node_name is None:
        print("START variable not found in entry.py.")
        return

    chain = []
    current_module_name = start_node_name
    target_length = 7
    
    print(f"Starting trace from module: {start_node_name}")

    for i in range(target_length):
        if current_module_name is None or not os.path.exists(f"pipeline/{current_module_name}.py"):
            print(f"\nChain broken at step {i+1} (Module: {current_module_name}). Expected module missing.")
            return

        # 2. Read the current module content and extract required values
        content = get_module_content(current_module_name)
        
        # We need to find NEXT and SECRET_TOKEN. Since they are constants, 
        # we can execute the code block to expose them in a local scope.
        local_scope = {}
        exec(content, {}, local_scope)

        next_node = local_scope.get("NEXT")
        secret_token = local_scope.get("SECRET_TOKEN")

        if next_node is None and i < target_length - 1:
             print(f"\nChain ends prematurely at step {i+1} (Module: {current_module_name}). NEXT is None.")
             return
        
        # 3. Record the token and advance
        chain.append({"module": current_module_name, "token": secret_token})
        print(f"Step {i+1}/{target_length}: Module={current_module_name}, Token='{secret_token}'")

        if next_node is None:
            # We reached the end before 7 steps
            break

        current_module_name = next_node


    # The token of the 7th module (index 6)
    if len(chain) == target_length:
        seventh_token = chain[-1]["token"]
        print("\nSuccessfully visited 7 modules.")
        
        # Write the result to answer.txt
        result_content = seventh_token or ""
        with open("answer.txt", "w") as f:
            f.write(result_content)
        print(f"Written token to answer.txt.")
    else:
        print("\nFailed to visit 7 modules.")

if __name__ == "__main__":
    solve()