import importlib
mods=[]
current='pipeline.entry.START'
# get start name
spec=importlib.import_module('pipeline.entry')
name=getattr(spec,'START')
for i in range(7):
    mod=importlib.import_module(f'pipeline.{name}')
    print(i+1, name, getattr(mod,'SECRET_TOKEN'))
    nxt=getattr(mod,'NEXT')
    if nxt is None:
        break
    name=nxt
