import importlib

def main():
    current='pipeline.entry.START'
    # get start module name
    from pipeline.entry import START
    mod_name=f'pipeline.{START}'
    for i in range(7):
        mod=importlib.import_module(mod_name)
        if i==6:
            token=getattr(mod,'SECRET_TOKEN')
            with open('answer.txt','w') as f: f.write(token)
            print('token',token)
            return
        next_mod=getattr(mod,'NEXT')
        mod_name=f'pipeline.{next_mod}'
if __name__=='__main__':
    main()
