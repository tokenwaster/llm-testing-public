import sys
sys.path.insert(0, '.')

from pipeline import entry

# Start with the first module
current_module_name = entry.START
visited = []

print(f"Starting at: {current_module_name}")

for i in range(7):
    # Import the current module
    module = __import__(f"pipeline.{current_module_name}", fromlist=['NEXT', 'SECRET_TOKEN'])
    
    # Store the token for this module
    secret_token = module.SECRET_TOKEN
    next_module = module.NEXT
    
    visited.append((i+1, current_module_name, secret_token))
    
    print(f"Step {i+1}: Module={current_module_name}, NEXT={next_module}")
    
    if next_module is None:
        print("Chain ended early!")
        break
    
    current_module_name = next_module

# The 7th module's token
if len(visited) >= 7:
    seventh_token = visited[6][2]
    print(f"\n7th module: {visited[6][1]}")
    print(f"SECRET_TOKEN: {seventh_token}")
    
    # Write to answer.txt
    with open('answer.txt', 'w') as f:
        f.write(seventh_token)
    print("\nToken written to answer.txt")
else:
    print(f"\nOnly visited {len(visited)} modules")
