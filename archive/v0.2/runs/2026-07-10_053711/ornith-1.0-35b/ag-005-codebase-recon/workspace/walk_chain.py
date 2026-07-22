import importlib
import sys
sys.path.insert(0, '.')

current = "mod_27"
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    print(f"{i}: {current} -> SECRET_TOKEN={token}, NEXT={mod.NEXT}")
    current = mod.NEXT
