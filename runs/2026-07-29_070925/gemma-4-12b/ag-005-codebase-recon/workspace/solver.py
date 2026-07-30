import importlib

def solve():
    current_module_name = "mod_27"
    count = 1
    
    print(f"Module {count}: {current_module_name}")
    
    while count < 7:
        module = importlib.import_module(f"pipeline.{current_module_name}")
        next_module = getattr(module, "NEXT", None)
        
        if next_module is None:
            print("End of chain reached early.")
            break
            
        current_module_name = next_module
        count += 1
        print(f"Module {count}: {current_module_name}")

    if count == 7:
        final_module = importlib.import_module(f"pipeline.{current_module_name}")
        token = getattr(final_module, "SECRET_TOKEN")
        print(f"Final token: {token}")
    else:
        print("Did not reach 7 modules.")

if __name__ == "__main__":
    solve()
