import importlib

# Start at the module named by START
current = "mod_27"

# Walk 7 modules
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    print(f"Module {i+1}: {current} -> SECRET_TOKEN = {token}")
    
    # Get the NEXT module
    if hasattr(mod, 'NEXT') and mod.NEXT is not None:
        current = mod.NEXT
    else:
        print("Chain ended early!")
        break
