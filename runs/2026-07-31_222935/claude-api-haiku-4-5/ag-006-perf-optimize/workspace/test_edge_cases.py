import perf

# Test edge cases
print("Testing edge cases...")

# common_elements
print("\n1. common_elements")
assert perf.common_elements([], []) == []
assert perf.common_elements([1, 2, 3], []) == []
assert perf.common_elements([], [1, 2, 3]) == []
assert perf.common_elements([1, 2, 3], [3, 2, 1]) == [1, 2, 3]
assert perf.common_elements([1, 1, 2], [2, 2, 3]) == [2]
print("   Edge cases PASS")

# fib
print("\n2. fib")
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(2) == 1
assert perf.fib(3) == 2
assert perf.fib(4) == 3
assert perf.fib(5) == 5
assert perf.fib(10) == 55
print("   Edge cases PASS")

# count_pairs
print("\n3. count_pairs")
assert perf.count_pairs([], 5) == 0
assert perf.count_pairs([1], 5) == 0
assert perf.count_pairs([1, 2, 3], 5) == 1  # (2, 3)
assert perf.count_pairs([1, 1, 1, 1], 2) == 6  # all pairs of 1s: 4 choose 2 = 6
assert perf.count_pairs([0, 0, 0], 0) == 3  # all pairs of 0s: 3 choose 2 = 3
print("   Edge cases PASS")

# dedupe_keep_order
print("\n4. dedupe_keep_order")
assert perf.dedupe_keep_order([]) == []
assert perf.dedupe_keep_order([1]) == [1]
assert perf.dedupe_keep_order([1, 2, 3]) == [1, 2, 3]
assert perf.dedupe_keep_order([1, 2, 1, 2, 1]) == [1, 2]
assert perf.dedupe_keep_order([3, 1, 2, 1, 3]) == [3, 1, 2]
print("   Edge cases PASS")

print("\nAll edge case tests passed!")
