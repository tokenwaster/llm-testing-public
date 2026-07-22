import importlib.util
import os

def get_module_globals(module_name):
    """Reads module content and returns its global variables."""
    path = f"pipeline/{module_name}.py"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Module {module_name} not found at {path}")

    with open(path, 'r') as f:
        content = f.read()
    
    # Simple execution to capture globals (assuming standard module structure)
    # Since we cannot reliably execute arbitrary code in this environment 
    # without potential side effects or complex setup, I will rely on parsing 
    # the known constants (NEXT and SECRET_TOKEN).

    globals_dict = {}
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Simple parsing for constant assignments like NAME = value
        if '=' in line and (line.split('=')[0].strip().isupper()):
            try:
                key, value_str = [part.strip() for part in line.split('=', 1)]
                # Attempt to evaluate simple values (strings, None)
                if value_str.startswith('"') and value_str.endswith('"'):
                    value = value_str[1:-1] # Strip quotes
                elif value_str == 'None':
                    value = None
                else:
                    # For simplicity in this controlled environment, assume simple string/None values
                    value = value_str 
                globals_dict[key] = value
            except Exception as e:
                # print(f"Could not parse line: {line} due to {e}")
                pass

    return globals_dict

def solve():
    """Traverses the pipeline chain and finds the token of the 7th module."""
    try:
        with open("pipeline/entry.py", 'r') as f:
            content = f.read()
        
        start_module = None
        for line in content.split('\n'):
            if "START =" in line:
                # Assuming START is defined on a single line like START = "mod_27"
                parts = line.split("=")
                if len(parts) > 1:
                    start_module = parts[1].strip().replace('"', '')
                    break

        if not start_module:
            print("Error: Could not find START in entry.py")
            return None

    except Exception as e:
        print(f"Error reading entry.py: {e}")
        return None

    current_module = start_module
    chain = []
    MAX_LENGTH = 7
    
    for i in range(MAX_LENGTH):
        if current_module is None:
            print(f"Chain ended prematurely at module {chain[-1] if chain else 'Start'}. Expected length {MAX_LENGTH}.")
            return None

        try:
            # 1. Get the globals for the current module
            globals_dict = get_module_globals(current_module)
            
            if not globals_dict:
                print(f"Error reading or parsing constants for module {current_module}.")
                return None

            # 2. Extract required values
            next_module = globals_dict.get("NEXT")
            secret_token = globals_dict.get("SECRET_TOKEN")

            if next_module is None and i < MAX_LENGTH - 1:
                 print(f"Chain broken at module {current_module}: NEXT is None before reaching the target length.")
                 return None

            # 3. Record state
            chain.append({
                'module': current_module,
                'token': secret_token,
                'next': next_module
            })
            
            if i == MAX_LENGTH - 1:
                # This is the 7th module (index 6)
                return secret_token

            current_module = next_module

        except Exception as e:
            print(f"An error occurred during traversal at module {current_module}: {e}")
            return None

    # Should not be reached if logic is correct, but included for safety.
    if len(chain) == MAX_LENGTH:
        return chain[-1]['token']
    else:
        return None

if __name__ == "__main__":
    result = solve()
    if result:
        print("SUCCESS")
        print(result)
    else:
        print("FAILURE")