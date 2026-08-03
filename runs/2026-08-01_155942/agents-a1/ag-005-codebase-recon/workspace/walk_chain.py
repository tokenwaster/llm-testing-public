#!/usr/bin/env python3
import importlib.util
import os

def load_module(module_name):
    """Dynamically load a module from pipeline/."""
    path = os.path.join("pipeline", f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

current = "mod_27"  # START from entry.py
chain = []

for i in range(7):
    print(f"[{i+1}] module: {current}")
    mod = load_module(current)
    secret_token = getattr(mod, 'SECRET_TOKEN', None)
    chain.append((current, secret_token))
    
    # Next hop (unless we've reached 7 modules already)
    if i < 6:
        next_mod = getattr(mod, 'NEXT', None)
        print(f"       NEXT -> {next_mod}")
        current = next_mod

print("\n--- Chain Summary ---")
for idx, (name, token) in enumerate(chain, 1):
    print(f"{idx}. {name}: SECRET_TOKEN={token[:50]}...")

# Write the 7th module's SECRET_TOKEN to answer.txt
seventh_token = chain[6][1]
with open("answer.txt", "w") as f:
    f.write(seventh_token)

print(f"\nAnswer written to answer.txt:\n{seventh_token}")
