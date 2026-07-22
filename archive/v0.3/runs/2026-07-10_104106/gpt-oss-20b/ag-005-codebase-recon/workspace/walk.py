import importlib

def main():
    mod_name='pipeline.entry'
    module=importlib.import_module(mod_name)
    start=getattr(module,'START')
    current=start
    for i in range(7):
        m=importlib.import_module(f'pipeline.{current}')
        if i==6:
            print(m.SECRET_TOKEN)
            return
        next_mod=getattr(m,'NEXT')
        current=next_mod
if __name__=='__main__':
    main()
