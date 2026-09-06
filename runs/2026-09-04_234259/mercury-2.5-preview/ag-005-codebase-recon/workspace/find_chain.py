import sys
import importlib.util

# Import entry module to get START
spec = importlib.util.spec_from_file_location("entry", "pipeline/entry.py")
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)

# Get starting module name
current = entry.START

# We need to visit 7 modules total, counting the start module as 1st
for i in range(7):
    # Import the module dynamically
    mod = __import__(f"pipeline.{current}", fromlist=['NEXT', 'SECRET_TOKEN'])
    print(f"Module {i+1}: {current}")
    
    # Get the next module in chain
    next_mod = mod.NEXT
    if next_mod is None:
        print("Chain ended!")
        break
    current = next_mod

# The 7th module's SECRET_TOKEN
answer = mod.SECRET_TOKEN
print(f"\nAnswer: {answer}")
