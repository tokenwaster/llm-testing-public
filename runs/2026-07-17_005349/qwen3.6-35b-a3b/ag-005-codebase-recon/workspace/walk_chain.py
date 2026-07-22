import importlib

# Start at the module named by START
current = "mod_27"

# Walk the chain, collecting visited modules
visited = []
for i in range(7):
    # Import the module
    mod = importlib.import_module(f"pipeline.{current}")
    visited.append(current)
    print(f"Step {i+1}: {current}")
    
    # Get the NEXT module
    current = mod.NEXT
    if current is None:
        print("Chain ended early!")
        break

# The 7th module's SECRET_TOKEN
target_module = visited[6]
target_mod = importlib.import_module(f"pipeline.{target_module}")
token = target_mod.SECRET_TOKEN
print(f"\n7th module: {target_module}")
print(f"SECRET_TOKEN: {token}")

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(token)
print(f"Written to answer.txt")
