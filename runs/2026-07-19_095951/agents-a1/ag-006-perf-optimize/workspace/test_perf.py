import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness with small inputs first
print("Testing correctness...")

# common_elements
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([], []) == []
assert common_elements([1, 1, 2], [2, 2, 3]) == [2]

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(30) == 832040

# count_pairs
assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,4), (2,3)
assert count_pairs([1, 1, 1], 2) == 3     # three pairs of (1,1)
assert count_pairs([], 0) == 0

# dedupe_keep_order
assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []

print("Correctness tests passed!")

# Performance tests
print("\nTesting performance...")

import random
random.seed(42)

# common_elements: two 200k-element lists
a = [random.randint(1, 1000000) for _ in range(200000)]
b = [random.randint(1, 1000000) for _ in range(200000)]
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements: {elapsed:.3f}s (under 2s)")
assert elapsed < 2.0

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s (under 2s)")
assert elapsed < 2.0
assert result == 22223224

# count_pairs: 100k elements
nums = [random.randint(-50000, 50000) for _ in range(100000)]
target = random.randint(-100000, 100000)
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs: {elapsed:.3f}s (under 2s)")
assert elapsed < 2.0

# dedupe_keep_order: 200k items
items = [random.randint(1, 100000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order: {elapsed:.3f}s (under 2s)")
assert elapsed < 2.0

print("\nAll tests passed!")
