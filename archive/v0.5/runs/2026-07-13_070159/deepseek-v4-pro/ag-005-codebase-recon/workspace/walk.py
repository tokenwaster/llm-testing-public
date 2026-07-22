import importlib

start = "mod_27"
current = start
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(f"{i+1}. {current} -> NEXT={nxt}, SECRET_TOKEN={token}")
    if i < 6 and nxt is None:
        print("Chain ended early!")
        break
    current = nxt

print(f"\n7th module: {visited[6]}")
print(f"Token: {importlib.import_module(f'pipeline.{visited[6]}').SECRET_TOKEN}")