import importlib

# Start at the module named by START
current = "mod_27"
visited = []

for i in range(7):
    module_name = f"pipeline.{current}"
    mod = importlib.import_module(module_name)
    visited.append((current, mod.SECRET_TOKEN))
    print(f"Step {i+1}: {current} -> SECRET_TOKEN={mod.SECRET_TOKEN}, NEXT={mod.NEXT}")
    if mod.NEXT is None:
        print("Chain ended before 7 modules!")
        break
    current = mod.NEXT

print(f"\n7th module: {visited[6][0]}")
print(f"SECRET_TOKEN: {visited[6][1]}")

with open("answer.txt", "w") as f:
    f.write(visited[6][1])

print("\nWritten to answer.txt")
