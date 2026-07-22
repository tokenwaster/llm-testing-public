import importlib.util
from pathlib import Path

# start from entry.START
spec = importlib.util.spec_from_file_location('entry', 'pipeline/entry.py')
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)
start = getattr(entry, 'START')
current = start
for i in range(7):
    mod_path = Path(f'pipeline/{current}.py')
    spec = importlib.util.spec_from_file_location(current, str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if i==6:
        token = getattr(mod,'SECRET_TOKEN',None)
        print('token',token)
        with open('answer.txt','w') as f: f.write(token)
    next_mod = getattr(mod,'NEXT',None)
    current = next_mod
