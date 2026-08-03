import importlib

entry = importlib.import_module("pipeline.entry")
name = entry.START

visited = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{name}")
    visited.append(name)
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(i+1, name, token, nxt)
    if i < 6:
        name = nxt

with open("answer.txt", "w") as f:
    f.write(token)
