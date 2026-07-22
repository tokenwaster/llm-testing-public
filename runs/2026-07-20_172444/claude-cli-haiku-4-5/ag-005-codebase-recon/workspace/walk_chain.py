import sys
sys.path.insert(0, 'pipeline')

from entry import START

# Follow the chain for 7 modules
current_module = START
tokens = []

for i in range(7):
    print(f"Module {i+1}: {current_module}")
    
    # Import the module
    mod = __import__(current_module)
    
    # Get the SECRET_TOKEN
    token = getattr(mod, 'SECRET_TOKEN', None)
    print(f"  Token: {token}")
    tokens.append((i+1, current_module, token))
    
    # Get the next module
    next_module = getattr(mod, 'NEXT', None)
    print(f"  Next: {next_module}")
    
    if next_module is None:
        print(f"ERROR: Chain ended at module {i+1}, need to reach module 7")
        break
    
    current_module = next_module

# The 7th module's token
seventh_token = tokens[6][2] if len(tokens) >= 7 else None
print(f"\n7th module's SECRET_TOKEN: {seventh_token}")
