"""Script to follow the pipeline chain and find the 7th module's SECRET_TOKEN."""

import sys
sys.path.insert(0, '.')

from pipeline import entry

# Start with the first module
current_module_name = entry.START
visited = []

for i in range(1, 8):  # We want 7 modules total
    visited.append(current_module_name)
    
    # Import the module
    module = __import__(f'pipeline.{current_module_name}', fromlist=[''])
    
    print(f"Module {i}: {current_module_name}")
    print(f"  SECRET_TOKEN: {module.SECRET_TOKEN}")
    print(f"  NEXT: {module.NEXT}")
    
    if module.NEXT is None:
        print("Chain ended early!")
        break
    
    current_module_name = module.NEXT

print(f"\n7th module: {visited[6]}")
print(f"SECRET_TOKEN: {__import__(f'pipeline.{visited[6]}', fromlist=['']).SECRET_TOKEN}")
