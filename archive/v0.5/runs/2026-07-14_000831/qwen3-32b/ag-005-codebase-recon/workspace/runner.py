import importlib

# Load entry module to get START
entry_mod = importlib.import_module('pipeline.entry')
start_name = entry_mod.START

current_name = start_name

# Traverse 6 more steps to reach 7th module
for _ in range(6):
    current_mod = importlib.import_module(f'pipeline.{current_name}')
    next_name = current_mod.NEXT
    if next_name is None:
        raise ValueError("Chain ended before reaching 7 modules")
    current_name = next_name

# Now get the SECRET_TOKEN of the seventh module
seventh_mod = importlib.import_module(f'pipeline.{current_name}')
secret_token = seventh_mod.SECRET_TOKEN

with open('answer.txt', 'w') as f:
    f.write(secret_token)