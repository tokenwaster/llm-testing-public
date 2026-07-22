import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("Testing correctness...")

# common_elements
assert common_elements([1,2,3], [2,3,4]) == [2,3]
assert common_elements([], [1,2,3]) == []
assert common_elements([1,1,2], [2,2,3]) == [2]
print("common_elements: OK")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(3) == 2
assert fib(10) == 55
assert fib(30) == 832040
print("fib: OK")

# count_pairs
assert count_pairs([1,2,3], 4) == 1  # (1,3)
assert count_pairs([1,1,1], 2) == 3  # all pairs of indices
assert count_pairs([1,2,3,4], 5) == 2  # (1,4), (2,3)
print("count_pairs: OK")

# dedupe_keep_order
assert dedupe_keep_order([1,2,1,3,2]) == [1,2,3]
assert dedupe_keep_order([]) == []
print("dedupe_keep_order: OK")

print("\nTesting performance...")

import random

# common_elements on two 200,000-element lists
a = list(range(200000))
b = list(range(100000, 300000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements: {elapsed:.4f}s (should be <2s), result len={len(result)}")
assert elapsed < 2

# fib(300)
start = time.time()
val = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.4f}s (should be <2s), result={val}")
assert elapsed < 2

# count_pairs on 100,000 elements
nums = [random.randint(0, 1000) for _ in range(100000)]
target = 500
start = time.time()
count = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs: {elapsed:.4f}s (should be <2s), count={count}")
assert elapsed < 2

# dedupe_keep_order on 200,000 items
items = [random.randint(0, 1000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order: {elapsed:.4f}s (should be <2s), result len={len(result)}")
assert elapsed < 2

print("\nAll tests passed!")
