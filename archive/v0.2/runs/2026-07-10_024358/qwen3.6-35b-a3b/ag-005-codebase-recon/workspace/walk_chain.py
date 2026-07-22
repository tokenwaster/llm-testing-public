import importlib
import sys
sys.path.insert(0, '.')

# Start at the module named by START
current = "mod_27"
visited = []

for i in range(7):
    # Import the module
    mod = importlib.import_module(f"pipeline.{current}")
    token = mod.SECRET_TOKEN
    visited.append((current, token))
    print(f"Step {i+1}: {current} -> SECRET_TOKEN = {token}")
    
    # Get the next module
    current = mod.NEXT
    if current is None:
        print("Chain ended early!")
        break

print(f"\n7th module: {visited[6][0]}")
print(f"7th module's SECRET_TOKEN: {visited[6][1]}")

# Write the answer
with open("answer.txt", "w") as f:
    f.write(visited[6][1])
print(f"\nAnswer written to answer.txt")
