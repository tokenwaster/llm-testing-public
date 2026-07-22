import importlib

current = "mod_27"  # from entry.START
visited = []
for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append((current, mod.SECRET_TOKEN))
    current = mod.NEXT
    if current is None:
        break

for name, token in visited:
    print(name, token)

seventh_token = visited[6][1]
with open("answer.txt", "w") as f:
    f.write(seventh_token)
print("7th module:", visited[6][0])
print("Token:", seventh_token)
