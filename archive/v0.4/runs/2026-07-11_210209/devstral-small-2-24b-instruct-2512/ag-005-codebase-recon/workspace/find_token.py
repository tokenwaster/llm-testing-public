#!/usr/bin/env python3
"""Script to find the SECRET_TOKEN of the 7th module in the chain."""

import importlib

# Start from entry.py
START = "mod_27"
current_module_name = START
count = 0
secret_token = None

while count < 7:
    # Import the current module
    module = importlib.import_module(f"pipeline.{current_module_name}")
    
    # Get the SECRET_TOKEN (this is the nth module)
    secret_token = module.SECRET_TOKEN
    print(f"Module {count + 1}: {current_module_name}, Token: {secret_token}")
    
    # Move to the next module
    current_module_name = module.NEXT
    count += 1
    
    if current_module_name is None:
        break

print(f"\n7th module's SECRET_TOKEN: {secret_token}")
