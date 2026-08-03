#!/usr/bin/env python3
"""Walk the module chain and find the 7th module's SECRET_TOKEN."""

import sys
import importlib

# Start from the entry point
from pipeline.entry import START

current_module_name = START
visited = []

# Visit 7 modules in total
for i in range(7):
    visited.append(current_module_name)
    print(f"Module {i+1}: {current_module_name}")
    
    # Import the current module
    module = importlib.import_module(f"pipeline.{current_module_name}")
    
    # Get the SECRET_TOKEN from this module
    secret_token = getattr(module, 'SECRET_TOKEN', None)
    print(f"  SECRET_TOKEN: {secret_token}")
    
    # Get the NEXT module name
    next_module = getattr(module, 'NEXT', None)
    print(f"  NEXT: {next_module}")
    
    if i == 6:  # 7th module (0-indexed as 6)
        seventh_token = secret_token
    
    if next_module is None:
        print(f"\nChain ends at module {i+1}")
        break
    
    current_module_name = next_module

print(f"\n7th module's SECRET_TOKEN: {seventh_token}")
