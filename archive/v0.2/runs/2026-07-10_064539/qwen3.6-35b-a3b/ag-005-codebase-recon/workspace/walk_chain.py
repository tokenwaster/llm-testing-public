import importlib

# Start at the module named by START
current = "mod_27"

# We need to visit 7 modules total, so we need 6 hops
for i in range(7):
    print(f"Step {i+1}: visiting {current}")
    mod = importlib.import_module(f"pipeline.{current}")
    if i == 6:
        # This is the 7th module - get its SECRET_TOKEN
        token = mod.SECRET_TOKEN
        print(f"SECRET_TOKEN of {current}: {token}")
        break
    # Get the NEXT module
    current = mod.NEXT
    print(f"  -> NEXT is {current}")
