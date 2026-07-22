import importlib

# Start from entry.py's START
import pipeline.entry as entry
current = entry.START
visited = []

for i in range(7):
    visited.append(current)
    mod = importlib.import_module(f"pipeline.{current}")
    if i == 6:
        print(f"7th module: {current}")
        print(f"SECRET_TOKEN: {mod.SECRET_TOKEN}")
    current = mod.NEXT

print(f"Visited: {visited}")
