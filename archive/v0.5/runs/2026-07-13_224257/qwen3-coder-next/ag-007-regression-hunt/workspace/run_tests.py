import sys
sys.path.insert(0, '.')

from tests.test_toolkit import *

# Run all test functions
import inspect

failed = []
passed = []

for name, obj in globals().items():
    if name.startswith('test_') and callable(obj):
        try:
            obj()
            passed.append(name)
            print(f"PASS: {name}")
        except AssertionError as e:
            failed.append((name, str(e)))
            print(f"FAIL: {name} - {e}")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"ERROR: {name} - {e}")

print(f"\n{len(passed)} pass, {len(failed)} fail")
