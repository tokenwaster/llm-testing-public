import importlib
import sys
sys.path.insert(0, '.')

# Import entry module directly
import pipeline.entry as entry

# Start at the module named by START
current_name = entry.START

visited = []
for i in range(7):
    mod = importlib.import_module(f'pipeline.{current_name}')
    token = mod.SECRET_TOKEN
    visited.append((current_name, token))
    print(f"Step {i+1}: {current_name} -> SECRET_TOKEN = {token}")
    
    # Get the next module
    current_name = mod.NEXT
    if current_name is None:
        print("Chain ended early!")
        break

print("\n7th module SECRET_TOKEN:", visited[6][1])
