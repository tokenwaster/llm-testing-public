#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from tests.test_collkit import *

# Run all test functions
tests = [
    test_chunk,
    test_flatten,
    test_group_by,
    test_take_while,
    test_unique_values,
    test_partition_union,
    test_windows_first,
    test_unique_order,
    test_partition_orientation,
    test_windows_complete,
]

passed = 0
failed = 0

for test in tests:
    try:
        test()
        print(f"PASSED: {test.__name__}")
        passed += 1
    except Exception as e:
        print(f"FAILED: {test.__name__}: {e}")
        failed += 1

print(f"\n{passed} pass, {failed} fail")
