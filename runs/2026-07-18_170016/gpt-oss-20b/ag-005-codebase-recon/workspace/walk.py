import importlib

def walk(start, steps):
    module_name=start
    for i in range(steps-1):
        mod=importlib.import_module(f"pipeline.{module_name}")
        next_mod=getattr(mod,'NEXT')
        if not next_mod:
            raise Exception('reached end before steps')
        module_name=next_mod
    return importlib.import_module(f"pipeline.{module_name}").SECRET_TOKEN

if __name__=='__main__':
    token=walk("mod_27",7)
    print(token)
