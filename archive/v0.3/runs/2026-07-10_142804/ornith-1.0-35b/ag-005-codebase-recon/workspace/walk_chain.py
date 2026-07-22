import importlib, sys
sys.path.insert(0, '.')

from pipeline.entry import START

current = START
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    print(f"{i+1}: {current} -> SECRET_TOKEN={token}")
    current = mod.NEXT
