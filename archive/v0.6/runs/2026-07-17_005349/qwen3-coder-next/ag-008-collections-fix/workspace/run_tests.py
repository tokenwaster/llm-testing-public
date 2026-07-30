#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from tests.test_collkit import *

# Run all test functions
test_functions = [
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

for func in test_functions:
    try:
        func()
        print("PASS: " + func.__name__)
        passed += 1
    except Exception as e:
        print("FAIL: " + func.__name__ + ": " + str(e))
        failed += 1

print("")
print(str(passed) + " pass, " + str(failed) + " fail")
