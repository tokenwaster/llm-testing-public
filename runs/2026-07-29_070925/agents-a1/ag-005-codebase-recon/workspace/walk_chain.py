import importlib
import os

# Get the start module name from entry.py
from pipeline.entry import START

current_name = START
chain_modules = [current_name]

for i in range(6):  # We need to visit 7 total, so 6 more hops after start
    try:
        mod = importlib.import_module(f"pipeline.{current_name}")
    except Exception as e:
        print(f"Error importing {current_name}: {e}")
        break
    
    next_name = getattr(mod, 'NEXT', None)
    
    if next_name is None:
        print("Chain ended early!")
        break
    
    chain_modules.append(next_name)
    current_name = next_name

print(f"Chain visited: {' -> '.join(chain_modules)}")

# Get the 7th module's SECRET_TOKEN (index 6, since we start counting from 1st at index 0)
if len(chain_modules) >= 7:
    seventh_module = importlib.import_module("pipeline." + chain_modules[6])
    token = getattr(seventh_module, 'SECRET_TOKEN', None)
    print(f"Token for module '{chain_modules[6]}': {token}")
    
    # Write to answer.txt
    with open('answer.txt', 'w') as f:
        f.write(token if isinstance(token, str) else str(token))
else:
    print("Not enough modules in chain!")
