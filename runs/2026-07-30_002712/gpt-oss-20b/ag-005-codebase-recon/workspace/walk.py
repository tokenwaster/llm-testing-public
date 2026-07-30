import importlib
mods={}
# load all mod files
for i in range(30):
    name=f"pipeline.mod_{i:02d}"
    mods[name]=importlib.import_module(name)
start='mod_27'
current=start
for step in range(1,8):
    module=mods[f"pipeline.{current}"]
    token=getattr(module,'SECRET_TOKEN',None)
    if step==7:
        print('token:',token)
    nextm=getattr(module,'NEXT',None)
    current=nextm
