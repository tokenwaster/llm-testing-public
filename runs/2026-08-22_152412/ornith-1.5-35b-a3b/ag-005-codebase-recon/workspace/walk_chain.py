import importlib

START = "mod_27"  # will read from entry dynamically below

# Read START from entry module
entry = importlib.import_module("pipeline.entry")
current = entry.START

visited = []
token = None
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    if nxt is None:
        print(f"Chain ended early at {i+1}: {current}")
        break
    current = nxt

print("Visited:", visited)
print("7th module token:", token)

with open("answer.txt", "w") as f:
    f.write(token)
