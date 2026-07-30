import importlib

# Read START
entry = importlib.import_module("pipeline.entry")
current = entry.START

visited = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append((current, mod.SECRET_TOKEN))
    print(f"Step {i+1}: module={current}, token={mod.SECRET_TOKEN}, next={mod.NEXT}")
    if i < 6:
        current = mod.NEXT

print(f"\n7th module: {visited[6][0]}, token: {visited[6][1]}")

with open("answer.txt", "w") as f:
    f.write(visited[6][1])
