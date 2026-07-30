import os
import base64

for fname in ['__init__.py', 'core.py', 'helpers.py']:
    path = os.path.join('textstats', fname)
    print(f"=== {path} ===")
    with open(path, 'rb') as f:
        data = f.read()
        print(base64.b64encode(data).decode('utf-8'))
