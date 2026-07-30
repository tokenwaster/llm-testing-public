import os

# Read all 30 modules by parsing source
modules = {}
pkg_dir = "pipeline"
for i in range(30):
    fname = f"mod_{i:02d}.py"
    path = os.path.join(pkg_dir, fname)
    with open(path) as f:
        src = f.read()
    
    # Extract SECRET_TOKEN and NEXT using simple regex
    secret_m = re.search(r'SECRET_TOKEN\s*=\s*"([^"]*)"', src)
    next_m = re.search(r'NEXT\s*=\s*"([^"]*)"', src)
    
    token = secret_m.group(1) if secret_m else None
    nxt = next_m.group(1) if next_m else None
    
    modules[f"mod_{i:02d}"] = {"SECRET_TOKEN": token, "NEXT": nxt}

# Walk chain from START for 7 modules (1-indexed)
current = "mod_27"
visited = []
for i in range(7):
    visited.append(current)
    next_val = modules[current]["NEXT"]
    current = next_val

print("Visited chain:", visited)
token = modules[visited[-1]]["SECRET_TOKEN"]
print(f"Token from {visited[-1]}: {token}")

with open("answer.txt", "w") as f:
    f.write(token)
print("Written to answer.txt")
