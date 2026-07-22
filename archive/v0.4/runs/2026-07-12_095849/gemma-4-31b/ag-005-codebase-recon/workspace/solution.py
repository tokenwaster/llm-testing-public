import importlib

def solve():
    # Start module from entry.py
    current_mod_name = "mod_27"
    
    for i in range(1, 8):
        print(f"Step {i}: Visiting {current_mod_name}")
        module = importlib.import_module(f"pipeline.{current_mod_name}")
        
        if i == 7:
            token = getattr(module, "SECRET_TOKEN")
            print(f"Found target token: {token}")
            return token
        
        current_mod_name = getattr(module, "NEXT")

if __name__ == "__main__":
    solve()
