#!/usr/bin/env python3
import importlib.util
import os

def load_module(module_name):
    # module_name like "mod_27"
    path = os.path.join("pipeline", f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Start from entry.py's START
from pipeline import entry
current_name = entry.START

visited = []
for i in range(7):
    mod = load_module(current_name)
    visited.append((current_name, getattr(mod, 'SECRET_TOKEN', None)))
    print(f"{i+1}. {current_name} -> SECRET_TOKEN: {mod.SECRET_TOKEN}")
    if i < 6:  # Don't need NEXT for the last one
        current_name = mod.NEXT

print("\n7th module's token:", visited[6][1])

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
