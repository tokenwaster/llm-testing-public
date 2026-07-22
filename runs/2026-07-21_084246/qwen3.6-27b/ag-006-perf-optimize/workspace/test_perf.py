import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Quick correctness tests
assert common_elements([1,2,3], [2,3,4]) == [2, 3]
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(30) == 832040
assert count_pairs([1,2,3,4], 5) == 2  # (1,4) and (2,3)
assert dedupe_keep_order([1,2,2,3,1]) == [1, 2, 3]

# Timing tests
import random
random.seed(42)

# common_elements on 200k lists
a = [random.randint(0, 100000) for _ in range(200000)]
b = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s")

# fib(300)
t0 = time.time()
fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s")

# count_pairs on 100k elements
nums = [random.randint(0, 100000) for _ in range(100000)]
t0 = time.time()
count_pairs(nums, 50000)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s")

# dedupe_keep_order on 200k items
items = [random.randint(0, 50000) for _ in range(200000)]
t0 = time.time()
dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s")

print("All tests passed!")
