import importlib

def get_next(module_name):
    mod=importlib.import_module(f"pipeline.{module_name}")
    return getattr(mod,'NEXT')

def main():
    cur='mod_27'
    for i in range(7):
        mod=importlib.import_module(f"pipeline.{cur}")
        token=getattr(mod,'SECRET_TOKEN')
        if i==6:
            print(token)
        cur=get_next(cur)

if __name__=='__main__':
    main()
