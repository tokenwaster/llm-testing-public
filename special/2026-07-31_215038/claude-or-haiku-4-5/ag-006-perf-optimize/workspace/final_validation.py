"""Final validation to ensure all functions produce correct results."""
from perf import common_elements, fib, count_pairs, dedupe_keep_order

print("=== common_elements ===")
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([1, 1, 2], [2, 3]) == [2]
assert common_elements([], [1, 2]) == []
assert common_elements([1], []) == []
assert common_elements([1, 2, 1, 3], [3, 2, 1]) == [1, 2, 3]
print("PASS: All common_elements tests passed")

print("\n=== fib ===")
expected_fibs = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 10: 55, 20: 6765}
for n, expected in expected_fibs.items():
    result = fib(n)
    assert result == expected, f"fib({n}) = {result}, expected {expected}"
print("PASS: All fib tests passed")

print("\n=== count_pairs ===")
assert count_pairs([1, 5, 7, -1], 6) == 2
assert count_pairs([1, 1, 1], 2) == 3
assert count_pairs([1, 2, 3, 4], 5) == 2
assert count_pairs([1, 2, 3, 4], 100) == 0
assert count_pairs([], 5) == 0
assert count_pairs([5], 10) == 0
assert count_pairs([2, 7, 11, 15], 9) == 1
print("PASS: All count_pairs tests passed")

print("\n=== dedupe_keep_order ===")
assert dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
assert dedupe_keep_order([1]) == [1]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1, 1, 1, 1]) == [1]
assert dedupe_keep_order(['a', 'b', 'a', 'c']) == ['a', 'b', 'c']
assert dedupe_keep_order([None, 1, None, 2]) == [None, 1, 2]
print("PASS: All dedupe_keep_order tests passed")

print("\nSUCCESS: ALL VALIDATION TESTS PASSED")
