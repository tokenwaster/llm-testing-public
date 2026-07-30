import sys
sys.path.insert(0, '.')
from tests import test_toolkit

if __name__ == '__main__':
    for name in dir(test_toolkit):
        if name.startswith('test_'):
            func = getattr(test_toolkit, name)
            try:
                result = func()
                print(f"PASS {name}")
            except Exception as e:
                print(f"FAIL {name}: {e}")
