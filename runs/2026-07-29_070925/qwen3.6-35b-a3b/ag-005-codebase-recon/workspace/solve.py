import importlib
import sys

sys.path.insert(0, '.')

# Start from mod_27
current = "mod_27"

visited = []

for i in range(7):
    mod = importlib.import_module(f'pipeline.{current}')
    token = getattr(mod, 'SECRET_TOKEN')
    visited.append((i+1, current, token))
    print(f"{i+1}: {current} -> SECRET_TOKEN={token}")
    
    next_mod = getattr(mod, 'NEXT', None)
    if next_mod is None:
        print("Chain ended early!")
        break
    current = next_mod

# Write the 7th module's token to answer.txt
with open('answer.txt', 'w') as f:
    f.write(visited[-1][2])

print(f"\nAnswer written: {visited[-1][2]}")
