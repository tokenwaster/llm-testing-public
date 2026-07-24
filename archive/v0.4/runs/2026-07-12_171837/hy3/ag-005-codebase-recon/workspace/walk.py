import importlib

import pipeline.entry as entry

mod_name = entry.START
visited = []
for _ in range(7):
    mod = importlib.import_module("pipeline." + mod_name)
    visited.append(mod_name)
    mod_name = mod.NEXT
    if mod_name is None:
        break

print("Visited:", visited)
seventh = importlib.import_module("pipeline." + visited[6])
print("7th token:", seventh.SECRET_TOKEN)
with open("answer.txt", "w") as f:
    f.write(seventh.SECRET_TOKEN)
