"""Script to follow the pipeline chain and find the 7th module's SECRET_TOKEN."""

import importlib

# Start with mod_27 as per entry.py
current_module_name = "mod_27"
visited = []

for i in range(7):
    # Import the module
    module = importlib.import_module(f"pipeline.{current_module_name}")
    
    # Get the SECRET_TOKEN and NEXT
    secret_token = module.SECRET_TOKEN
    next_module = module.NEXT
    
    visited.append({
        'index': i + 1,
        'module': current_module_name,
        'token': secret_token
    })
    
    print(f"Step {i+1}: {current_module_name}")
    
    # Move to the next module (if not None)
    if next_module is None:
        print("Chain ended early!")
        break
    
    current_module_name = next_module

# The 7th module's token
print(f"\n7th module: {visited[6]['module']}")
print(f"SECRET_TOKEN: {visited[6]['token']}")

# Write to answer.txt
with open('answer.txt', 'w') as f:
    f.write(visited[6]['token'])

print("\nToken written to answer.txt")
