import importlib
import sys

# Add pipeline to path
sys.path.insert(0, '/workspace')

# Start from entry.py
from pipeline.entry import START

current = START
chain = [current]

# Follow the chain for 7 modules total
for i in range(6):  # We already have 1, need 6 more to get to 7
    module = importlib.import_module(f'pipeline.{current}')
    next_module = module.NEXT
    if next_module is None:
        print(f"Chain ends at module {current}")
        break
    chain.append(next_module)
    current = next_module

print(f"Chain of {len(chain)} modules:")
for idx, mod in enumerate(chain, 1):
    print(f"  {idx}. {mod}")

# Get the 7th module's SECRET_TOKEN
seventh_module_name = chain[6]  # 0-indexed, so [6] is the 7th
seventh_module = importlib.import_module(f'pipeline.{seventh_module_name}')
secret_token = seventh_module.SECRET_TOKEN

print(f"\n7th module: {seventh_module_name}")
print(f"SECRET_TOKEN: {secret_token}")

# Write to answer.txt
with open('/workspace/answer.txt', 'w') as f:
    f.write(secret_token)

print("\nAnswer written to answer.txt")
