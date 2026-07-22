import sys, os
sys.path.insert(0, '.')

from pipeline import entry

current = entry.START
visited = [current]

for i in range(6):  # already visited 1 (the start), need 6 more hops to reach 7 total
    mod_name = current.replace('mod_', 'mod_')
    with open(f"pipeline/{mod_name}.py") as f:
        content = f.read()
    
    next_mod = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("NEXT"):
            val = line.split('"')[1] if '"' in line else line.split("'")[1]
            next_mod = val
    
    if next_mod is None:
        print(f"Chain ended at {current}")
        break
    
    visited.append(next_mod)
    current = next_mod

print("Visited chain:", visited)
# Get the 7th module's SECRET_TOKEN
mod_name = visited[-1].replace('mod_', 'mod_')
with open(f"pipeline/{mod_name}.py") as f:
    content = f.read()

token = None
for line in content.splitlines():
    line = line.strip()
    if line.startswith("SECRET_TOKEN"):
        val = line.split('"')[1] if '"' in line else line.split("'")[1]
        token = val
        break

print(f"SECRET_TOKEN of {visited[-1]}: {token}")

with open('answer.txt', 'w') as f:
    f.write(str(token))
