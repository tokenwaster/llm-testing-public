import perf

# Test common_elements
assert perf.common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert perf.common_elements([1, 1, 2], [1, 2, 3]) == [1, 2]

# Test fib
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.fib(300) > 0  # Just verify it runs and returns positive

# Test count_pairs
assert perf.count_pairs([1, 2, 3, 2], 4) == 2  # (1,3) and (2,2)
assert perf.count_pairs([1, 1, 1], 2) == 3  # (0,1), (0,2), (1,2)

# Test dedupe_keep_order
assert perf.dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert perf.dedupe_keep_order([]) == []

print("All basic tests passed!")
