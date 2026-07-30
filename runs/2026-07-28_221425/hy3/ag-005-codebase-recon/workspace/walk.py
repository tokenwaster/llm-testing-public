import importlib

mod = importlib.import_module("pipeline.entry")
name = mod.START
visited = []
for _ in range(7):
    m = importlib.import_module("pipeline." + name)
    visited.append((name, m.SECRET_TOKEN, m.NEXT))
    name = m.NEXT
    if name is None:
        break

for v in visited:
    print(v)

print("7th token:", visited[6][1])
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
