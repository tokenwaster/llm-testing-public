import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness with small inputs first
print("=== Correctness Tests ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = common_elements(a, b)
expected = sorted([3, 4, 5])
print(f"common_elements: {result}, expected {expected}, {'PASS' if result == expected else 'FAIL'}")

# fib
for n in range(10):
    result = fib(n)
    # known values: 0,1,1,2,3,5,8,13,21,34
    expected = [0,1,1,2,3,5,8,13,21,34][n]
    print(f"fib({n}): {result}, expected {expected}, {'PASS' if result == expected else 'FAIL'}")

# count_pairs
nums = [1, 2, 3, 4, 5]
target = 6
# pairs: (1,5), (2,4) -> indices: (0,4), (1,3) => 2 pairs
result = count_pairs(nums, target)
print(f"count_pairs: {result}, expected 2, {'PASS' if result == 2 else 'FAIL'}")

# dedupe_keep_order
items = [1, 2, 1, 3, 2, 4]
result = dedupe_keep_order(items)
expected = [1, 2, 3, 4]
print(f"dedupe_keep_order: {result}, expected {expected}, {'PASS' if result == expected else 'FAIL'}")

# Performance tests
print("\n=== Performance Tests ===")

import random
random.seed(0)

# common_elements on two 200,000-element lists
a = [random.randint(1, 500000) for _ in range(200000)]
b = [random.randint(1, 500000) for _ in range(200000)]
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements (200k x 200k): {elapsed:.3f}s, result length: {len(result)}")

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s, result: {result}")

# count_pairs on 100,000 elements
nums = [random.randint(-1000, 1000) for _ in range(100000)]
target = 0
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs (100k): {elapsed:.3f}s, result: {result}")

# dedupe_keep_order on 200,000 items
items = [random.randint(1, 50000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order (200k): {elapsed:.3f}s, result length: {len(result)}")
