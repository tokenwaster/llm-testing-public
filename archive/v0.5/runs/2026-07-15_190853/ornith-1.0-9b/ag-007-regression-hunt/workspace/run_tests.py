import os, sys
# Add workspace root so 'toolkit' package is importable
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.join(os.getcwd(), "tests"))
from test_toolkit import *

# Run all tests manually
passed = 0
failed = 0
errors = []

test_funcs = [obj for name, obj in globals().items() if callable(obj) and name.startswith("test_")]

for func in sorted(test_funcs):
    try:
        func()
        passed += 1
        print(f"  PASS: {func.__name__}")
    except Exception as e:
        failed += 1
        errors.append((func.__name__, str(e)))
        print(f"  FAIL: {func.__name__} - {e}")

print(f"\n{passed} passed, {failed} failed")
if errors:
    for name, err in errors:
        print(f"  {name}: {err}")
