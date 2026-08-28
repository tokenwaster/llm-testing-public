import importlib.util
from pathlib import Path

pipeline_dir = Path("pipeline")

def load_module(name):
    spec = importlib.util.spec_from_file_location(name, pipeline_dir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load entry to get START
entry_mod = load_module("entry")
start = entry_mod.START

print(f"Start: {start}")

chain = []
current = start
for i in range(7):
    chain.append(current)
    mod = load_module(current)
    next_val = getattr(mod, 'NEXT', None)
    print(f"[{i+1}] {current} -> NEXT={next_val}")
    current = next_val

print(f"\n7th module: {chain[-1]}")
seventh_mod = load_module(chain[-1])
token = seventh_mod.SECRET_TOKEN
print(f"SECRET_TOKEN of 7th module ({chain[-1]}): {token}")

with open("answer.txt", "w") as f:
    f.write(token)

print("\nWritten to answer.txt:", token)
