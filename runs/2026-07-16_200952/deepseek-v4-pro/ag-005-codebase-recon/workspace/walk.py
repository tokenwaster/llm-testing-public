import importlib

# Start module
current = "mod_27"
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    token = mod.SECRET_TOKEN
    nxt = mod.NEXT
    print(f"{i+1}: {current} -> NEXT={nxt}, SECRET_TOKEN={token}")
    if i == 6:
        # This is the 7th module
        with open("answer.txt", "w") as f:
            f.write(token)
        print(f"\n7th module: {current}, token written to answer.txt")
    if nxt is None:
        print("Chain ended early!")
        break
    current = nxt