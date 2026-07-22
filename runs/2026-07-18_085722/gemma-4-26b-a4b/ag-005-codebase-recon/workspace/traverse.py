import importlib

def follow_chain(start_module_name, steps):
    current_module_name = start_module_name
    visited_modules = []
    
    for i in range(steps):
        try:
            # Import the module dynamically. 
            # The modules are in the 'pipeline' package.
            module_path = f"pipeline.{current_module_name}"
            module = importlib.import_module(module_path)
            
            visited_modules.append({
                'name': current_module_name,
                'token': getattr(module, 'SECRET_TOKEN'),
                'next': getattr(module, 'NEXT', None)
            })
            
            if module_path == f"pipeline.{current_module_name}" and getattr(module, 'NEXT', None) is None:
                 # If NEXT is None, we can't go further. But the problem says 7 modules.
                 pass

            next_module_name = getattr(module, 'NEXT', None)
            if next_module_name is None:
                break
            current_module_name = next_module_name
        except Exception as e:
            print(f"Error at {current_module_name}: {e}")
            break
            
    return visited_modules

# Get START from entry.py
import pipeline.entry as entry
start_node = entry.START

chain = follow_chain(start_node, 7)

for i, node in enumerate(chain):
    print(f"{i+1}: {node['name']} (Token: {node['token']}, Next: {node['next']})")

if len(chain) >= 7:
    print(f"\nTarget token: {chain[6]['token']}")
else:
    print(f"\nChain ended early. Only visited {len(chain)} modules.")
