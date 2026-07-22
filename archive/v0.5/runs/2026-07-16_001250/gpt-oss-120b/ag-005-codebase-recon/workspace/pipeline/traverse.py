import importlib
import sys
import os

def main():
    # Ensure pipeline package is importable
    sys.path.append(os.path.abspath('.'))
    from pipeline import entry
    current = entry.START
    count = 0
    token = None
    while current is not None and count < 7:
        mod = importlib.import_module(f'pipeline.{current}')
        count += 1
        token = getattr(mod, 'SECRET_TOKEN', None)
        # print progress
        print(f"{count}: {current}, token={token}, next={getattr(mod, 'NEXT', None)}")
        current = getattr(mod, 'NEXT', None)
    # Write token of 7th module to answer.txt
    if token is None:
        raise ValueError('Token not found')
    with open('answer.txt', 'w') as f:
        f.write(token)

if __name__ == '__main__':
    main()
