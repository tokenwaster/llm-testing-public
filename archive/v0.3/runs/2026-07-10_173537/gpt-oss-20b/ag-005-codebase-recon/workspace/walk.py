import importlib

def main():
    entry = importlib.import_module('pipeline.entry')
    current = entry.START
    for i in range(7):
        module = importlib.import_module(f'pipeline.{current}')
        if i==6:
            print(module.SECRET_TOKEN)
            return
        next_mod = getattr(module, 'NEXT')
        if next_mod is None:
            raise Exception('Chain ended early')
        current = next_mod
if __name__=='__main__':
    main()
