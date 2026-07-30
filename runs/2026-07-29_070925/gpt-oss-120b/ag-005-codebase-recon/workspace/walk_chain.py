import importlib

def get_nth_token(start_module, n):
    current = start_module
    for i in range(1, n+1):
        mod = importlib.import_module(f'pipeline.{current}')
        token = getattr(mod, 'SECRET_TOKEN', None)
        if i == n:
            return token
        # move to next
        nxt = getattr(mod, 'NEXT', None)
        if not nxt:
            raise ValueError(f'Chain ended early at {current}')
        current = nxt
    raise RuntimeError('Should not reach here')

if __name__ == '__main__':
    from pipeline import entry
    token = get_nth_token(entry.START, 7)
    print(token)
