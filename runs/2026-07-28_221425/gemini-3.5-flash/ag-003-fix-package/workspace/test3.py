import os

for fname in ['__init__.py', 'core.py', 'helpers.py']:
    path = os.path.join('textstats', fname)
    print(f"=== {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        print(f.read())
