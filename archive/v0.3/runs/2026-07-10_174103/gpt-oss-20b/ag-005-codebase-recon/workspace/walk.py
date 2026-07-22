import importlib
entry = importlib.import_module('pipeline.entry')
start = entry.START
current = start
for i in range(7):
    mod = importlib.import_module(f'pipeline.{current}')
    if i==6:
        print(mod.SECRET_TOKEN)
    current = mod.NEXT
