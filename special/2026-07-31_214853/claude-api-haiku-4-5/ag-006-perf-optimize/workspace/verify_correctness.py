"""Comprehensive correctness verification for optimized functions."""
from perf import common_elements, fib, count_pairs, dedupe_keep_order

print("=== COMPREHENSIVE CORRECTNESS VERIFICATION ===\n")

print("1. Testing common_elements...")
tests = [
    ([], [], []),
    ([1], [1], [1]),
    ([1, 2, 3], [3, 4, 5], [3]),
    ([3, 1, 2], [5, 3, 4], [3]),
    ([1, 2, 2, 3], [2, 3, 3, 4], [2, 3]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
]
for a, b, expected in tests:
    result = common_elements(a, b)
    assert result == expected, f"common_elements({a}, {b}): expected {expected}, got {result}"
    print(f"   PASS: common_elements({a}, {b}) = {result}")

print("\n2. Testing fib...")
fib_tests = [
    (0, 0),
    (1, 1),
    (2, 1),
    (3, 2),
    (4, 3),
    (5, 5),
    (6, 8),
    (7, 13),
    (10, 55),
    (20, 6765),
]
for n, expected in fib_tests:
    result = fib(n)
    assert result == expected, f"fib({n}): expected {expected}, got {result}"
    print(f"   PASS: fib({n}) = {result}")

print("\n3. Testing count_pairs...")
count_tests = [
    ([1, 2, 3, 4, 5], 5, 2),
    ([1, 2, 3], 4, 1),
    ([0, 0, 0], 0, 3),
    ([1, 1, 1, 1], 2, 6),
    ([2, 4, 3, 5, 7], 9, 2),
    ([], 0, 0),
    ([1], 5, 0),
]
for nums, target, expected in count_tests:
    result = count_pairs(nums, target)
    assert result == expected, f"count_pairs({nums}, {target}): expected {expected}, got {result}"
    print(f"   PASS: count_pairs({nums}, {target}) = {result}")

print("\n4. Testing dedupe_keep_order...")
dedupe_tests = [
    ([], []),
    ([1], [1]),
    ([1, 2, 3], [1, 2, 3]),
    ([1, 1, 1], [1]),
    ([1, 2, 1, 2], [1, 2]),
    ([3, 2, 1, 2, 3], [3, 2, 1]),
    (['a', 'b', 'a', 'c', 'b'], ['a', 'b', 'c']),
]
for items, expected in dedupe_tests:
    result = dedupe_keep_order(items)
    assert result == expected, f"dedupe_keep_order({items}): expected {expected}, got {result}"
    print(f"   PASS: dedupe_keep_order({items}) = {result}")

print("\n=== ALL CORRECTNESS TESTS PASSED ===")
