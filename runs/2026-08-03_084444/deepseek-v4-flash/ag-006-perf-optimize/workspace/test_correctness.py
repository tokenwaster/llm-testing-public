import perf

# Test common_elements
assert perf.common_elements([], []) == []
assert perf.common_elements([1,2,3], [4,5,6]) == []
assert perf.common_elements([1,2,3,2], [2,3,4]) == [2,3]
assert perf.common_elements([3,1,2], [1,2,3]) == [1,2,3]
assert perf.common_elements([1,1,1], [1,1]) == [1]
print("common_elements: OK")

# Test fib
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(2) == 1
assert perf.fib(10) == 55
assert perf.fib(20) == 6765
assert perf.fib(50) == 12586269025
print("fib: OK")

# Test count_pairs
assert perf.count_pairs([], 10) == 0
assert perf.count_pairs([1], 10) == 0
assert perf.count_pairs([1,2,3], 4) == 1  # (1,3)
assert perf.count_pairs([1,1,1], 2) == 3  # 3 pairs
assert perf.count_pairs([1,2,3,4,5], 5) == 2  # (1,4), (2,3)
assert perf.count_pairs([1,1,2,2], 3) == 4  # (1,2) x 4
print("count_pairs: OK")

# Test dedupe_keep_order
assert perf.dedupe_keep_order([]) == []
assert perf.dedupe_keep_order([1,2,3]) == [1,2,3]
assert perf.dedupe_keep_order([1,2,1,3,2,3]) == [1,2,3]
assert perf.dedupe_keep_order(['a','b','a']) == ['a','b']
print("dedupe_keep_order: OK")

print("All tests passed!")