import importlib

import pipeline.entry as entry

mod_name = entry.START
visited = []
for _ in range(7):
    mod = importlib.import_module("pipeline." + mod_name)
    visited.append((mod_name, mod.SECRET_TOKEN))
    nxt = mod.NEXT
    if nxt is None:
        break
    mod_name = nxt

for i, (name, token) in enumerate(visited, 1):
    print(i, name, token)

print("7th token:", visited[6][1])
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
