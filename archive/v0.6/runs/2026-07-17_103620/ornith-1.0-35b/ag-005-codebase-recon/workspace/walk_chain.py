import importlib
import sys

sys.path.insert(0, '.')

current = "mod_27"  # START from entry.py
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = getattr(mod, 'SECRET_TOKEN')
    visited.append((i+1, current, token))
    print(f"{i+1}. {current} -> SECRET_TOKEN={token}")
    next_mod = getattr(mod, 'NEXT', None)
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod

# Write the 7th module's token
if len(visited) >= 7:
    seventh_token = visited[6][2]
    with open('answer.txt', 'w') as f:
        f.write(seventh_token)
    print(f"\nAnswer written: {seventh_token}")
