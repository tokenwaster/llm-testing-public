import time
import perf

# Correctness checks
assert perf.common_elements([1,2,3,2], [2,3,4]) == [2,3]
assert perf.common_elements([], [1,2]) == []
assert perf.common_elements([1,1,1], [1]) == [1]

assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.fib(20) == 6765
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600

# [1,2,3,4,3] target 6: (2,4)=6, (3,3)=6 => 2 pairs
assert perf.count_pairs([1,2,3,4,3], 6) == 2
assert perf.count_pairs([], 5) == 0
assert perf.count_pairs([1,1,1], 2) == 3

assert perf.dedupe_keep_order([3,1,3,2,1,2]) == [3,1,2]
assert perf.dedupe_keep_order([]) == []
assert perf.dedupe_keep_order([1,1,1]) == [1]

# Performance checks
import random
random.seed(42)

a = [random.randint(0, 100000) for _ in range(200000)]
b = [random.randint(0, 100000) for _ in range(200000)]
t = time.time(); perf.common_elements(a, b); print(f"common_elements: {time.time()-t:.3f}s")

t = time.time(); perf.fib(300); print(f"fib(300): {time.time()-t:.6f}s")

nums = [random.randint(0, 1000) for _ in range(100000)]
t = time.time(); perf.count_pairs(nums, 500); print(f"count_pairs: {time.time()-t:.3f}s")

items = [random.randint(0, 100000) for _ in range(200000)]
t = time.time(); perf.dedupe_keep_order(items); print(f"dedupe_keep_order: {time.time()-t:.3f}s")

print("All checks passed!")
