"""Script to follow the pipeline chain and find the 7th module's SECRET_TOKEN."""

import os
import sys

# Add the pipeline directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pipeline'))

from entry import START

def get_module_info(module_name):
    """Import a module and return its NEXT and SECRET_TOKEN."""
    module = __import__(module_name)
    next_mod = getattr(module, 'NEXT', None)
    secret_token = getattr(module, 'SECRET_TOKEN', None)
    return next_mod, secret_token

# Follow the chain
current_module = START
visited = []

for i in range(7):
    visited.append(current_module)
    print(f"Step {i+1}: {current_module}")
    
    if i == 6:  # We've reached the 7th module (index 6)
        break
    
    next_mod, _ = get_module_info(current_module)
    current_module = next_mod

# Get the SECRET_TOKEN of the 7th module
_, secret_token = get_module_info(visited[6])
print(f"\n7th module: {visited[6]}")
print(f"SECRET_TOKEN: {secret_token}")

# Write to answer.txt
with open('answer.txt', 'w') as f:
    f.write(secret_token)

print("\nWritten to answer.txt")
