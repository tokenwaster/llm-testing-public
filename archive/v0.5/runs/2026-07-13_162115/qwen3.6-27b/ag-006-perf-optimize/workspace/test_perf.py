import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("=== Correctness Tests ===")

# common_elements
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([], [1, 2]) == []
assert common_elements([1, 1, 2], [1, 2, 2]) == [1, 2]
print("common_elements: OK")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(20) == 6765
print("fib: OK")

# count_pairs
assert count_pairs([1, 3, 2, 4], 5) == 2  # (1,4) and (3,2)
assert count_pairs([1, 1, 1], 2) == 3
assert count_pairs([], 5) == 0
print("count_pairs: OK")

# dedupe_keep_order
assert dedupe_keep_order([1, 2, 2, 3, 1]) == [1, 2, 3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1, 1, 1]) == [1]
print("dedupe_keep_order: OK")

# Test timing
print("\n=== Timing Tests ===")
random.seed(42)

# common_elements timing
a = [random.randint(0, 300000) for _ in range(200000)]
b = [random.randint(0, 300000) for _ in range(200000)]
t0 = time.time()
common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s (budget: 2s)")

# fib timing
t0 = time.time()
fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s (budget: 2s)")

# count_pairs timing
nums = [random.randint(0, 200000) for _ in range(100000)]
t0 = time.time()
count_pairs(nums, 150000)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s (budget: 2s)")

# dedupe_keep_order timing
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s (budget: 2s)")

print("\nAll tests passed!")
