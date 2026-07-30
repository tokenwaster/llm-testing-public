import importlib
import sys

# Make sure pipeline is importable
sys.path.insert(0, '.')

entry = importlib.import_module('pipeline.entry')
current = entry.START

print(f"Start: {current}")

for i in range(7):
    mod = importlib.import_module(f'pipeline.{current}')
    print(f"Step {i+1}: {current}, SECRET_TOKEN = {mod.SECRET_TOKEN}, NEXT = {mod.NEXT}")
    if i == 6:
        # 7th module (1-indexed)
        with open('answer.txt', 'w') as f:
            f.write(mod.SECRET_TOKEN)
        print(f"Answer written: {mod.SECRET_TOKEN}")
        break
    current = mod.NEXT
