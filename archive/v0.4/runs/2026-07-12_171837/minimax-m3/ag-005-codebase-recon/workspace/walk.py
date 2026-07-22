from pipeline import entry
import importlib

name = entry.START
print(f"Start: {name}")
for i in range(1, 8):
    mod = importlib.import_module(f"pipeline.{name}")
    print(f"Step {i}: {name} -> NEXT={mod.NEXT}, SECRET_TOKEN={mod.SECRET_TOKEN}")
    if i == 7:
        print(f"FINAL TOKEN: {mod.SECRET_TOKEN}")
        break
    name = mod.NEXT
