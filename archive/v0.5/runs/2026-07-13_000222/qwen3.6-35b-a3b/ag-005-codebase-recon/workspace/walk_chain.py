import importlib
import sys
sys.path.insert(0, '.')

# Start at the module named by START
current = "mod_27"
visited = []

for i in range(7):
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    visited.append((current, token))
    print(f"Step {i+1}: {current} -> token: {token}")
    
    # Get the next module
    next_mod = mod.NEXT
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod

# The 7th module's token
print(f"\n7th module: {visited[6][0]}")
print(f"Token: {visited[6][1]}")

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
print(f"\nWrote token to answer.txt")
