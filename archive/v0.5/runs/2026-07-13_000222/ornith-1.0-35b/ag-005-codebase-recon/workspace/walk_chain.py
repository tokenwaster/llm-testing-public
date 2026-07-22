import importlib
import sys

sys.path.insert(0, '.')

current = "mod_27"
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    visited.append((current, token))
    print(f"{i+1}: {current} -> SECRET_TOKEN={token}")
    current = mod.NEXT

with open("answer.txt", "w") as f:
    f.write(visited[-1][1])

print(f"\nFinal answer written: {visited[-1][1]}")
