#!/usr/bin/env python3
import importlib.util
import os

def load_module(module_name):
    """Load a module from its .py file in the pipeline/ directory."""
    filepath = os.path.join("pipeline", f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load {filepath}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Starting point from entry.py
START = "mod_27"

current_name = START
chain_modules = []  # We'll store (name, module_object) pairs

print(f"Starting at {START}")
for i in range(7):
    print(f"Hop {i+1}: Loading {current_name}...")
    current_module = load_module(current_name)
    
    if not hasattr(current_module, 'SECRET_TOKEN'):
        raise ValueError(f"{current_name} does not have SECRET_TOKEN!")
    
    chain_modules.append((current_name, current_module))
    print(f"  -> SECRET_TOKEN: {current_module.SECRET_TOKEN}")
    
    # Get the NEXT module for next iteration
    if i < 6:  # Don't need NEXT from last module, but we want to verify consistency
        if not hasattr(current_module, 'NEXT'):
            raise ValueError(f"{current_name} does not have NEXT!")
        current_name = current_module.NEXT
        print(f"  -> Next hop: {current_name}")

# The 7th module (index 6) is what we need
seventh_name, seventh_module = chain_modules[6]
print(f"\n=== 7th module ({seventh_name}) has SECRET_TOKEN ===")
print(seventh_module.SECRET_TOKEN)

# Write to answer.txt
with open("answer.txt", "w") as f:
    f.write(seventh_module.SECRET_TOKEN)

print("\nWritten to answer.txt")
