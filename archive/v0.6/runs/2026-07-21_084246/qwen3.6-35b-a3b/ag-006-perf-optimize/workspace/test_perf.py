from perf import common_elements, fib, count_pairs, dedupe_keep_order
import time

# Test common_elements
result = common_elements([1,2,3,4,5], [3,4,5,6,7])
assert result == [3, 4, 5], f"common_elements failed: {result}"
print("common_elements basic: OK")

# Test fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
print("fib basic: OK")

# Test count_pairs
assert count_pairs([1,2,3,4,5], 5) == 2  # (1,4) and (2,3)
print("count_pairs basic: OK")

# Test dedupe_keep_order
assert dedupe_keep_order([3,1,2,1,3,4]) == [3,1,2,4]
print("dedupe basic: OK")

# Performance tests
import random

# common_elements on 200k elements
a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.time()
common_elements(a, b)
t1 = time.time()
print(f"common_elements 200k: {t1-t0:.3f}s (budget: 2s)")

# fib(300)
t0 = time.time()
fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s (budget: 2s)")

# count_pairs on 100k elements
nums = [random.randint(-1000, 1000) for _ in range(100000)]
t0 = time.time()
count_pairs(nums, 0)
t1 = time.time()
print(f"count_pairs 100k: {t1-t0:.3f}s (budget: 2s)")

# dedupe on 200k items
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe 200k: {t1-t0:.3f}s (budget: 2s)")

print("\nAll tests passed!")
