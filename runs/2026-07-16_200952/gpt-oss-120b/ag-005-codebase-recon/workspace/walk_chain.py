import importlib
import os

# Load the start module name from entry
entry = importlib.import_module('pipeline.entry')
current_name = entry.START
count = 0
secret = None
while current_name is not None and count < 7:
    mod = importlib.import_module(f'pipeline.{current_name}')
    count += 1
    secret = getattr(mod, 'SECRET_TOKEN', None)
    # print for debugging
    print(f"{count}: {current_name}, token={secret}, next={getattr(mod, 'NEXT', None)}")
    current_name = getattr(mod, 'NEXT', None)

if count == 7:
    # write answer
    with open('answer.txt', 'w') as f:
        f.write(secret)
    print('Wrote answer.txt')
else:
    print('Chain shorter than 7')
