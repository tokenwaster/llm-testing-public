import importlib, sys
sys.path.insert(0, '.')

start = "mod_27"
name = start
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{name}")
    token = mod.SECRET_TOKEN
    print(f"{i}: {name} -> SECRET_TOKEN={token}, NEXT={mod.NEXT}")
    name = mod.NEXT
