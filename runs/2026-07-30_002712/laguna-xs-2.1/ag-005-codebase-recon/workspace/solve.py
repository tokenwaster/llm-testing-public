import sys
sys.path.insert(0, 'pipeline')

from entry import START
import importlib

current = START
count = 1

while count < 7:
    module = importlib.import_module(current)
    next_mod = getattr(module, 'NEXT', None)
    if next_mod is None:
        print(f"Chain ended early at {current}")
        break
    current = next_mod
    count += 1
    print(f"{count}: {current}")

# Get the SECRET_TOKEN from the 7th module
module = importlib.import_module(current)
token = getattr(module, 'SECRET_TOKEN')
print(f"\nToken for 7th module ({current}): {token}")

with open('answer.txt', 'w') as f:
    f.write(token)