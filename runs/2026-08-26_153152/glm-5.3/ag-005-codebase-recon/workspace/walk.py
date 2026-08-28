import importlib

from pipeline import entry

current = entry.START
visited = []

for step in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append((current, mod.SECRET_TOKEN))
    print(f"{step + 1}: {current} -> NEXT={mod.NEXT} token={mod.SECRET_TOKEN}")
    current = mod.NEXT
    if current is None:
        break

print()
print("7th module:", visited[6][0])
print("SECRET_TOKEN:", visited[6][1])

with open("answer.txt", "w") as f:
    f.write(visited[6][1])
