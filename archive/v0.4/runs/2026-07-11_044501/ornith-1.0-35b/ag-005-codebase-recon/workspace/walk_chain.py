import importlib, sys
sys.path.insert(0, '.')

start = "mod_27"
name = start
for i in range(7):
    mod = importlib.import_module(f"pipeline.{name}")
    token = getattr(mod, 'SECRET_TOKEN')
    print(f"{i+1}: {name} -> SECRET_TOKEN={token}")
    name = getattr(mod, 'NEXT', None)
