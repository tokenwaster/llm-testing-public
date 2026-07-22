import importlib

current_module_name = "pipeline.entry"
entry = importlib.import_module(current_module_name)
start_mod = entry.START

print(f"START: {start_mod}")

current_mod_name = start_mod
visited = []

for i in range(1, 8):
    # Import the module
    mod = importlib.import_module(f"pipeline.{current_mod_name}")
    secret = getattr(mod, "SECRET_TOKEN")
    next_mod = getattr(mod, "NEXT")
    visited.append((i, current_mod_name, secret))
    print(f"Step {i}: {current_mod_name} -> NEXT: {next_mod}, SECRET: {secret}")
    current_mod_name = next_mod

print("Done.")
