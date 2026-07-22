import importlib.util
import os

def get_module_globals(module_name):
    """Reads a module file and returns its global namespace."""
    path = f"pipeline/{module_name}.py"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Module {module_name} not found at {path}")

    spec = importlib.util.spec_from_file_location("temp_mod", path)
    module = importlib.util.module_from_spec(spec)
    # Execute the module code in a controlled namespace
    exec(open(path).read(), module.__dict__)
    return module.__dict__

def follow_chain(start_module):
    """Follows the chain for 7 modules and returns the token of the 7th."""
    current_module = start_module
    tokens = []
    
    for i in range(7):
        try:
            # Get the global variables from the current module
            globals_dict = get_module_globals(current_module)
            
            # Extract SECRET_TOKEN and NEXT
            token = globals_dict.get("SECRET_TOKEN")
            next_module = globals_dict.get("NEXT")

            if token is None:
                raise AttributeError(f"Module {current_module} does not define SECRET_TOKEN.")
            
            tokens.append(token)
            print(f"Step {i+1}: Module {current_module}, Token found.")

            if i == 6: # We reached the 7th module (index 6)
                return token, next_module

            if next_module is None:
                raise StopIteration(f"Chain ended prematurely at step {i+1}.")
            
            current_module = next_module

        except FileNotFoundError as e:
            print(f"Error: {e}")
            return None, None
        except AttributeError as e:
            print(f"Error processing module {current_module}: {e}")
            return None, None
        except StopIteration as e:
            print(f"Chain stopped early: {e}")
            return tokens[-1] if tokens else None, None

    # Should not be reached if loop runs 7 times successfully
    return tokens[6], current_module


if __name__ == "__main__":
    START = "mod_27" # From entry.py
    token_7, _ = follow_chain(START)
    print("\\n--- RESULT ---")
    print(f"The SECRET_TOKEN of the 7th module is: {token_7}")