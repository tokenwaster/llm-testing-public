import importlib

# Start module
current = "mod_27"
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    print(f"Step {i+1}: {current}, SECRET_TOKEN = {mod.SECRET_TOKEN}, NEXT = {mod.NEXT}")
    current = mod.NEXT
    if current is None:
        print("Reached end of chain.")
        break

print(f"\n7th module: {visited[6]}")
print(f"SECRET_TOKEN: {importlib.import_module(f'pipeline.{visited[6]}').SECRET_TOKEN}")