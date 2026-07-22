import importlib
import sys
sys.path.insert(0, '.')

start = "mod_27"
current = start
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = getattr(mod, 'SECRET_TOKEN')
    visited.append((current, token))
    print(f"{i+1}: {current} -> SECRET_TOKEN={token}")
    nxt = getattr(mod, 'NEXT', None)
    if nxt is None:
        break
    current = nxt

with open("answer.txt", "w") as f:
    f.write(visited[-1][1])
print(f"\nAnswer written: {visited[-1][1]}")
