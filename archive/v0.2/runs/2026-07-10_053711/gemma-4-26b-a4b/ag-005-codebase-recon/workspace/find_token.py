import importlib

def follow_chain(start_module_name, count):
    current_module_name = start_module_name
    visited_modules = []
    
    for _ in range(count):
        if current_module_name is None:
            break
        
        # Construct the full module path
        module_path = f"pipeline.{current_module_name}"
        try:
            module = importlib.import_module(module_path)
            visited_modules.append(module)
            current_module_name = getattr(module, 'NEXT', None)
        except ImportError as e:
            print(f"Error importing {module_path}: {e}")
            break
        except AttributeError as e:
            print(f"Error accessing attribute in {module_path}: {e}")
            break

    return visited_modules

if __name__ == "__main__":
    # We need to get START from pipeline.entry
    import pipeline.entry as entry
    start_node = entry.START
    print(f"Starting with: {start_node}")
    
    chain = follow_chain(start_node, 7)
    print(f"Visited {len(chain)} modules.")
    
    if len(chain) == 7:
        token = getattr(chain[6], 'SECRET_TOKEN', None)
        print(f"The 7th module's token is: {token}")
        with open('answer.txt', 'w') as f:
            f.write(str(token))
    else:
        print(f"Chain ended prematurely after {len(chain)} modules.")
