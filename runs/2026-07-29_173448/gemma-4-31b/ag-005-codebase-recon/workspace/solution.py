import importlib

def solve():
    current_mod_name = "mod_27" # From entry.py
    visited = []
    
    for i in range(7):
        module = importlib.import_module(f"pipeline.{current_mod_name}")
        visited.append(current_mod_name)
        if i < 6:
            current_mod_name = module.NEXT
        else:
            token = module.SECRET_TOKEN
            print(token)

if __name__ == "__main__":
    solve()
