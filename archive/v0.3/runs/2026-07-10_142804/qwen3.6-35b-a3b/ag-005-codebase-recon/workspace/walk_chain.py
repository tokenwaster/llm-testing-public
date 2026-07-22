import importlib

START = "mod_27"

current = START
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    visited.append((current, token))
    print(f"Step {i+1}: {current} -> SECRET_TOKEN = {token}")
    
    next_mod = mod.NEXT
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod

# Write the 7th module's token to answer.txt
if len(visited) == 7:
    seventh_token = visited[6][1]
    with open("answer.txt", "w") as f:
        f.write(seventh_token)
    print(f"\nAnswer written: {seventh_token}")
else:
    print(f"\nOnly visited {len(visited)} modules")
