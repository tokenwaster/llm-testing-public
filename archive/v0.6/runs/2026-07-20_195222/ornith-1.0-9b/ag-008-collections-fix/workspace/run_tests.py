import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tests.test_collkit import *
import pytest

# Run all test functions
passed = 0
failed = 0
for name in dir():
    if name.startswith('test_'):
        try:
            exec(name)()
            passed += 1
            print(f"PASS: {name}")
        except Exception as e:
            failed += 1
            print(f"FAIL: {name}: {e}")

print(f"\n{passed} passed, {failed} failed")
