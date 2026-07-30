import time
import random
import perf

# common_elements
a = [random.randint(0, 100000) for _ in range(200000)]
b = [random.randint(0, 100000) for _ in range(200000)]
t = time.time()
r = perf.common_elements(a, b)
print("common_elements:", time.time() - t, "len", len(r))

# fib(300)
t = time.time()
f = perf.fib(300)
print("fib(300):", time.time() - t, f)

# count_pairs
nums = [random.randint(0, 1000) for _ in range(100000)]
t = time.time()
c = perf.count_pairs(nums, 500)
print("count_pairs:", time.time() - t, c)

# dedupe
items = [random.randint(0, 100000) for _ in range(200000)]
t = time.time()
d = perf.dedupe_keep_order(items)
print("dedupe:", time.time() - t, "len", len(d))

# Correctness spot checks
assert perf.common_elements([1,2,3,2], [2,3,4]) == [2,3]
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.count_pairs([1,2,3,2], 4) == 2  # (1,3),(2,2)
assert perf.dedupe_keep_order([1,2,1,3,2]) == [1,2,3]
print("All correctness checks passed")
