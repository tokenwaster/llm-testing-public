"""Script to find the 7th module's SECRET_TOKEN in the chain."""

import sys
sys.path.insert(0, '.')

from pipeline import entry

# Start with the first module
current_module_name = entry.START
visited = []

print(f"Starting at: {current_module_name}")

for i in range(1, 8):  # We need to visit 7 modules total
    visited.append(current_module_name)
    
    if i == 7:
        # This is the 7th module - get its SECRET_TOKEN
        module = __import__(f"pipeline.{current_module_name}", fromlist=['SECRET_TOKEN'])
        secret_token = module.SECRET_TOKEN
        print(f"\n7th module: {current_module_name}")
        print(f"SECRET_TOKEN: {secret_token}")
        break
    
    # Get the NEXT module
    module = __import__(f"pipeline.{current_module_name}", fromlist=['NEXT'])
    next_module = module.NEXT
    print(f"Module {i}: {current_module_name} -> {next_module}")
    current_module_name = next_module

# Write the answer to a file
with open('answer.txt', 'w') as f:
    f.write(secret_token)

print(f"\nToken written to answer.txt: {secret_token}")
