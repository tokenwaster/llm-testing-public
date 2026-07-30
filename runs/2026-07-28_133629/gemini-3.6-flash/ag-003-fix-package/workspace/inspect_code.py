import os

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

print("--- textstats/__init__.py ---")
print(read('textstats/__init__.py'))

print("--- textstats/core.py ---")
print(read('textstats/core.py'))

print("--- textstats/helpers.py ---")
print(read('textstats/helpers.py'))
