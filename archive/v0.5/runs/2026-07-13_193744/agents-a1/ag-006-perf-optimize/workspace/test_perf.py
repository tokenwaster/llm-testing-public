import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness with small inputs
print("Testing correctness...")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
assert common_elements(a, b) == [3, 4, 5], f"common_elements failed: {common_elements(a, b)}"

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(30) == 832040

# count_pairs
nums = [1, 2, 3, 4, 5]
target = 6
pairs = [(i,j) for i in range(len(nums)) for j in range(i+1, len(nums)) if nums[i]+nums[j]==target]
assert count_pairs(nums, target) == len(pairs), f"count_pairs failed: {count_pairs(nums, target)}"

# dedupe_keep_order
items = [1, 2, 3, 2, 4, 1, 5]
assert dedupe_keep_order(items) == [1, 2, 3, 4, 5], f"dedupe_keep_order failed: {dedupe_keep_order(items)}"

print("Correctness tests passed!")

# Test performance with large inputs
print("\nTesting performance...")

import random
random.seed(0)

# common_elements on two 200,000-element lists
a = [random.randint(1, 1000000) for _ in range(200000)]
b = [random.randint(1, 1000000) for _ in range(200000)]
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements: {elapsed:.3f}s (limit: 2s)")
assert elapsed < 2.0, f"common_elements too slow: {elapsed}s"

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s (limit: 2s)")
assert elapsed < 2.0, f"fib too slow: {elapsed}s"

# count_pairs on 100,000 elements
nums = [random.randint(-10000, 10000) for _ in range(100000)]
target = random.randint(-20000, 20000)
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs: {elapsed:.3f}s (limit: 2s)")
assert elapsed < 2.0, f"count_pairs too slow: {elapsed}s"

# dedupe_keep_order on 200,000 items
items = [random.randint(1, 100000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order: {elapsed:.3f}s (limit: 2s)")
assert elapsed < 2.0, f"dedupe_keep_order too slow: {elapsed}s"

print("\nAll performance tests passed!")
