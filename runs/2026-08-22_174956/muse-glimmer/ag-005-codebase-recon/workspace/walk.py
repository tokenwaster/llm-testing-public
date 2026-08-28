import importlib
import sys
sys.path.insert(0, '.')

# Load entry
import pipeline.entry as entry
start_name = entry.START
print("START:", start_name)

current_name = start_name
visited = []
for i in range(7):
    module_name = f"pipeline.{current_name}"
    mod = importlib.import_module(module_name)
    token = getattr(mod, "SECRET_TOKEN", None)
    nxt = getattr(mod, "NEXT", None)
    visited.append((current_name, token, nxt))
    print(f"{i+1}. {current_name} token={token} NEXT={nxt}")
    if nxt is None:
        break
    current_name = nxt

# Write token of 7th module
if len(visited) >= 7:
    seventh_name, seventh_token, _ = visited[6]
    with open('answer.txt', 'w') as f:
        f.write(seventh_token)
    print("Wrote answer:", seventh_token)
else:
    print("Chain too short")
