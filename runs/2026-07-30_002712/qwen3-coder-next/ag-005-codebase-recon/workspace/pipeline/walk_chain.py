import sys
sys.path.insert(0, 'pipeline')

from entry import START

# Walk the chain for 7 steps
current = START
chain = []

for i in range(1, 8):  # 1 to 7 inclusive
    chain.append(current)
    print(f"Step {i}: module={current}")
    
    # Import the module to get NEXT
    module = __import__(current, fromlist=['NEXT', 'SECRET_TOKEN'])
    next_module = getattr(module, 'NEXT')
    secret_token = getattr(module, 'SECRET_TOKEN')
    
    if i == 7:
        print(f"\n=== 7th module (step {i}) ===")
        print(f"Module: {current}")
        print(f"SECRET_TOKEN: {secret_token}")
        break
    
    if next_module is None:
        print("Chain ended prematurely!")
        break
    
    current = next_module

# Write the answer
with open('answer.txt', 'w') as f:
    # Re-import to get the 7th token
    pass
