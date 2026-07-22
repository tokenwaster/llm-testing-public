import sys
sys.path.insert(0, '.')

from pipeline import entry
import importlib

# Walk the chain starting from START for 7 modules
current = entry.START
visited = []
for i in range(7):
    visited.append(current)
    print(f"Step {i+1}: {current}")
    
    # Import as pipeline.mod_X
    mod_name = f"pipeline.{current}"
    if mod_name not in sys.modules:
        mod = importlib.import_module(mod_name)
    else:
        mod = sys.modules[mod_name]
    
    next_val = getattr(mod, 'NEXT', None)
    print(f"  -> NEXT: {next_val}")
    current = next_val

print(f"\n7th module: {visited[-1]}")

# Get SECRET_TOKEN of the 7th module
mod_name = f"pipeline.{visited[-1]}"
if mod_name not in sys.modules:
    mod = importlib.import_module(mod_name)
else:
    mod = sys.modules[mod_name]

token = getattr(mod, 'SECRET_TOKEN', None)
print(f"SECRET_TOKEN: {token}")

with open('answer.txt', 'w') as f:
    f.write(str(token))
