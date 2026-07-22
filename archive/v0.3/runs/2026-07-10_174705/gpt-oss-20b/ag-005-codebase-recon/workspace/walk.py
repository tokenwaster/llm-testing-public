import importlib

def main():
    mod_name='pipeline.entry'
    module=importlib.import_module(mod_name)
    start=getattr(module,'START')
    current=start
    for i in range(7):
        m=importlib.import_module(f'pipeline.{current}')
        if i==6:
            token=getattr(m,'SECRET_TOKEN')
            with open('answer.txt','w') as f:
                f.write(token)
            print('token written',token)
            return
        current=getattr(m,'NEXT')
if __name__=='__main__':
    main()
