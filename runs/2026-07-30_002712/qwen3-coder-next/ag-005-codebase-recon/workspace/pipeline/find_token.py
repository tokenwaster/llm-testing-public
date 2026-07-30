import sys
sys.path.insert(0, 'pipeline')

from entry import START

def get_module_attr(module_name, attr):
    """Get an attribute from a module by name"""
    mod = __import__(module_name, fromlist=[attr])
    return getattr(mod, attr)

# Walk the chain for 7 steps
current = START
print(f"Starting at: {START}")

for i in range(1, 8):  # 1 to 7 inclusive
    token = get_module_attr(current, 'SECRET_TOKEN')
    next_mod = get_module_attr(current, 'NEXT')
    
    print(f"Step {i}: module={current}, token={token}")
    
    if i == 7:
        print(f"\n=== The 7th module's SECRET_TOKEN ===")
        print(token)
        
        # Write to answer.txt
        with open('answer.txt', 'w') as f:
            f.write(token)
        print(f"\nWritten '{token}' to answer.txt")
        break
    
    if next_mod is None:
        print("Chain ended prematurely!")
        break
    
    current = next_mod
