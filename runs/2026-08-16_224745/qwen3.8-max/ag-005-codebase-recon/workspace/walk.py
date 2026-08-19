import importlib
import pipeline.entry as entry

name = entry.START
visited = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{name}")
    visited.append((name, mod.SECRET_TOKEN))
    name = mod.NEXT

for i, (n, t) in enumerate(visited, 1):
    print(i, n, t)

with open("answer.txt", "w") as f:
    f.write(visited[-1][1])
