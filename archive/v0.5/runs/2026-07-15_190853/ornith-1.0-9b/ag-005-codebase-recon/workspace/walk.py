import importlib.util
import os

base = "pipeline"

def load_module(name):
    spec = importlib.util.spec_from_file_location(name, f"{base}/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# START is in entry.py
from pipeline.entry import START

print(f"START: {START}")

current = START
visited = [current]
for i in range(6):  # already visited 1, need 6 more to reach 7 total
    current_mod = load_module(current)
    next_name = current_mod.NEXT
    print(f"Step {i+1}: {visited[i]} -> NEXT={next_name}")
    if next_name is None:
        print("End of chain!")
        break
    visited.append(next_name)
    current = next_name

print(f"\nVisited 7 modules: {visited}")
target = load_module(visited[6])
token = target.SECRET_TOKEN
print(f"SECRET_TOKEN of module {visited[6]}: {token}")

with open("answer.txt", "w") as f:
    f.write(token)
print("Written to answer.txt")
