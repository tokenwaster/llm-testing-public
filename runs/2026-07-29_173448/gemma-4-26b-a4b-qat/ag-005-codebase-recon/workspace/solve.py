import importlib

def solve():
    import sys
    import os
    sys.path.append(os.getcwd())
    
    import pipeline.entry as entry
    
    current_mod_name = entry.START
    visited_tokens = []
    
    for i in range(7):
        mod = importlib.import_module(f"pipeline.{current_mod_name}")
        visited_tokens.append(mod.SECRET_TOKEN)
        print(f"Step {i+1}: module {current_mod_name} token {mod.SECRET_TOKEN}")
        
        current_mod_name = mod.NEXT
        if current_mod_name is None:
            break
            
    if len(visited_tokens) < 7:
        print(f"Chain ended early after {len(visited_tokens)} modules.")
    else:
        print(f"7th token: {visited_tokens[6]}")
        return visited_tokens[6]

if __name__ == "__main__":
    print(solve())
