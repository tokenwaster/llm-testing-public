import importlib
from pathlib import Path

def main():
    mod_name='pipeline.entry'
    entry=importlib.import_module(mod_name)
    current=entry.START
    count=1
    while count<7:
        module=importlib.import_module(f'pipeline.{current}')
        next_mod=getattr(module,'NEXT')
        if not next_mod:
            raise Exception('Chain ended early')
        current=next_mod
        count+=1
    token=getattr(importlib.import_module(f'pipeline.{current}'),'SECRET_TOKEN')
    Path('answer.txt').write_text(token)
if __name__=='__main__':
    main()
