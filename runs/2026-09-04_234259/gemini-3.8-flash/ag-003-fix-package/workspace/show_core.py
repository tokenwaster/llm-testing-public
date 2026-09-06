import json
with open('textstats/core.py', 'r', encoding='utf-8') as f:
    s = f.read()
print(json.dumps({'content': s}))
