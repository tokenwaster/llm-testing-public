#!/usr/bin/env python3
"""Walk the pipeline chain starting from START until we've visited 7 modules, then output the token of the 7th."""

import importlib.util
import os

def load_module(module_name):
    """Dynamically load a module from pipeline/ and return its name, NEXT, and SECRET_TOKEN."""
    # Build path to module file in pipeline directory
    mod_path = os.path.join("pipeline", f"{module_name}.py")
    
    spec = importlib.util.spec_from_file_location(module_name, mod_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return {
        "name": module_name,
        "next": getattr(module, "NEXT", None),
        "token": getattr(module, "SECRET_TOKEN", None)
    }

def walk_chain(start_mod="mod_27"):
    current = start_mod
    visited = []
    
    # We need to visit 7 modules total (including the start)
    for i in range(7):
        mod_info = load_module(current)
        visited.append(mod_info)
        
        if mod_info["next"] is None:
            print(f"Chain ended at module {i+1}: {current}")
            break
            
        current = mod_info["next"]
    
    return visited

if __name__ == "__main__":
    chain = walk_chain()
    
    print("Traversed modules:")
    for i, m in enumerate(chain, 1):
        print(f"  {i}. {m['name']} -> token={m['token']}, next={chain[i]['next'] if i < len(chain) else 'END'}")
    
    # The answer is the SECRET_TOKEN of the 7th module visited
    seventh_token = chain[6]["token"] if len(chain) >= 7 else None
    
    if seventh_token:
        print(f"\nAnswer (7th token): {seventh_token}")
        
        # Write to answer.txt in workspace root
        with open("answer.txt", "w") as f:
            f.write(seventh_token)
        print("Written to answer.txt")
    else:
        print("\nCould not find 7 modules - chain too short!")
