import importlib

mod = importlib.import_module("pipeline.entry")
name = mod.START
visited = []
for _ in range(7):
    m = importlib.import_module(f"pipeline.{name}")
    visited.append((name, m.SECRET_TOKEN))
    name = m.NEXT

for i, (n, t) in enumerate(visited, 1):
    print(i, n, t)

print("7th token:", visited[6][1])
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
