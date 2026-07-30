import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("=== Correctness Tests ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [4, 5, 6, 7, 8]
assert common_elements(a, b) == [4, 5], f"Got {common_elements(a, b)}"
print("common_elements: OK")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(20) == 6765
print("fib: OK")

# count_pairs
assert count_pairs([1, 2, 3, 4, 5], 5) == 2  # (1,4), (2,3)
assert count_pairs([1, 1, 1], 2) == 3  # all pairs
print("count_pairs: OK")

# dedupe_keep_order
assert dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
print("dedupe_keep_order: OK")

# Timing tests
print("\n=== Timing Tests ===")

random.seed(42)

# common_elements on 200k elements
a = [random.randint(0, 300000) for _ in range(200000)]
b = [random.randint(0, 300000) for _ in range(200000)]
t0 = time.time()
common_elements(a, b)
t1 = time.time()
print(f"common_elements 200k: {t1-t0:.3f}s (budget: 2s)")

# fib(300)
t0 = time.time()
fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.6f}s (budget: 2s)")

# count_pairs on 100k elements
nums = [random.randint(0, 200000) for _ in range(100000)]
t0 = time.time()
count_pairs(nums, 150000)
t1 = time.time()
print(f"count_pairs 100k: {t1-t0:.3f}s (budget: 2s)")

# dedupe_keep_order on 200k items
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order 200k: {t1-t0:.3f}s (budget: 2s)")

print("\nAll tests passed!")
