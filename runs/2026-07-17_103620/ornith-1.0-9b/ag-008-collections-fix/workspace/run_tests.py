import sys, os
sys.path.insert(0, '.')
os.chdir('.')
from tests.test_collkit import *
passed = failed = 0
for name in dir():
    if name.startswith('test_'):
        try:
            eval(name)()
            passed += 1; print(f"PASS {name}")
        except Exception as e:
            failed += 1; print(f"FAIL {name}: {e}")
print(f"\n{passed} passed, {failed} failed")
