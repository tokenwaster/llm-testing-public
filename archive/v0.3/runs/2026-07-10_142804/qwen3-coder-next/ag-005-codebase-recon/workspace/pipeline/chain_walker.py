"""Walk the pipeline chain to find the 7th module's SECRET_TOKEN."""

import importlib

# Start with the entry point
START = "mod_27"

def get_module_info(module_name):
    """Get NEXT and SECRET_TOKEN from a module."""
    mod = importlib.import_module(f"pipeline.{module_name}")
    return {
        'name': module_name,
        'NEXT': getattr(mod, 'NEXT', None),
        'SECRET_TOKEN': getattr(mod, 'SECRET_TOKEN', None)
    }

# Walk the chain
current = START
chain = []

for i in range(7):
    info = get_module_info(current)
    chain.append(info)
    print(f"Step {i+1}: {info['name']} - Token: {info['SECRET_TOKEN']}")
    
    if info['NEXT'] is None:
        print("Reached end of chain!")
        break
    current = info['NEXT']

print("\n--- Summary ---")
print(f"The 7th module in the chain is: {chain[6]['name']}")
print(f"SECRET_TOKEN: {chain[6]['SECRET_TOKEN']}")

# Write to answer.txt
with open('answer.txt', 'w') as f:
    f.write(chain[6]['SECRET_TOKEN'])

print("\nWritten to answer.txt")
