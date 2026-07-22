import importlib

current_mod_name = "pipeline.entry"
entry = importlib.import_module(current_mod_name)
start_mod = entry.START

print(f"START: {start_mod}")

current_mod_name = f"pipeline.{start_mod}"
for i in range(1, 8):
    mod = importlib.import_module(current_mod_name)
    secret = getattr(mod, "SECRET_TOKEN", None)
    nxt = getattr(mod, "NEXT", None)
    print(f"Step {i}: Module {current_mod_name}, SECRET_TOKEN={secret}, NEXT={nxt}")
    if nxt:
        current_mod_name = f"pipeline.{nxt}"
    else:
        current_mod_name = None
