import importlib

entry = importlib.import_module("pipeline.entry")
current = entry.START

visited = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append((current, mod.SECRET_TOKEN))
    if i < 6:
        current = mod.NEXT

for idx, (name, tok) in enumerate(visited, 1):
    print(idx, name, tok)

token = visited[-1][1]
with open("answer.txt", "w") as f:
    f.write(token)
print("WROTE:", token)
