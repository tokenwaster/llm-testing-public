"""Walk the pipeline chain to find the 7th module's SECRET_TOKEN."""
import importlib

# Start with entry.py
START = "mod_27"

current_module_name = START
visited = []

for i in range(7):
    # Import the current module
    module = importlib.import_module(f"pipeline.{current_module_name}")
    
    # Get its SECRET_TOKEN and NEXT
    secret_token = getattr(module, "SECRET_TOKEN")
    next_module = getattr(module, "NEXT")
    
    visited.append({
        'index': i + 1,
        'module': current_module_name,
        'token': secret_token
    })
    
    print(f"Step {i+1}: Module={current_module_name}, NEXT={next_module}")
    
    if next_module is None:
        print("Reached end of chain!")
        break
    
    current_module_name = next_module

# The 7th module's token
if len(visited) >= 7:
    seventh_token = visited[6]['token']
    print(f"\n7th module: {visited[6]['module']}")
    print(f"SECRET_TOKEN: {seventh_token}")
    
    # Write to answer.txt
    with open('answer.txt', 'w') as f:
        f.write(seventh_token)
    print("Written to answer.txt")
else:
    print(f"Only visited {len(visited)} modules")
