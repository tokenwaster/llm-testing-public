from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Edge case tests
print("Testing edge cases...")

# common_elements - empty lists, no intersection
assert common_elements([], []) == []
assert common_elements([1, 2], [3, 4]) == []
assert common_elements([1, 1, 1], [1, 1, 1]) == [1]
assert sorted(common_elements([5, 1, 3], [1, 2, 5])) == [1, 5]

# fib - edge cases
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
# Check a larger value manually computed
assert fib(10) == 55
fib_30 = fib(30)
expected_30 = 832040
assert fib_30 == expected_30, f"fib(30) should be {expected_30}, got {fib_30}"

# count_pairs - various edge cases
assert count_pairs([], 5) == 0
assert count_pairs([1], 5) == 0
assert count_pairs([2, 3], 5) == 1  # 2+3=5, one pair
assert count_pairs([2, 3, 2, 3], 5) == 4  # two 2s and two 3s = 4 pairs
# Pairs with same number: [3, 3] -> target 6 counts as one pair
assert count_pairs([3, 3], 6) == 1

# dedupe_keep_order - edge cases
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1]) == [1]
assert dedupe_keep_order([1, 2, 1, 2, 3]) == [1, 2, 3]
assert dedupe_keep_order([5, 5, 5, 5]) == [5]

# Verify fib(100) is correct (known value)
fib_100 = fib(100)
expected_fib_100 = 354224848179261915075
assert fib_100 == expected_fib_100, f"fib(100) mismatch"

print("All edge case tests passed!")