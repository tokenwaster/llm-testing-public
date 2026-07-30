import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness first
print("Testing correctness...")

# common_elements test
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
assert common_elements(a, b) == [3, 4, 5], "common_elements failed"
print("common_elements: OK")

# fib test
for n in range(10):
    assert fib(n) == fib.__wrapped__(n) if hasattr(fib, '__wrapped__') else True
# Manual check
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(3) == 2
assert fib(4) == 3
assert fib(5) == 5
assert fib(6) == 8
print("fib: OK")

# count_pairs test
nums = [1, 2, 3, 4, 3]
target = 6
result = count_pairs(nums, target)
assert result == 2, f"count_pairs failed: got {result}"
print("count_pairs: OK")

# dedupe_keep_order test
items = [1, 2, 3, 2, 4, 1]
result = dedupe_keep_order(items)
assert result == [1, 2, 3, 4], f"dedupe_keep_order failed: got {result}"
print("dedupe_keep_order: OK")

# Performance tests
print("\nTesting performance...")

# common_elements on large lists
a = list(range(200000))
b = list(range(100000, 300000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements on 200k lists: {elapsed:.2f}s (should be < 2s)")
assert elapsed < 2.0

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.2f}s (should be < 2s)")
assert elapsed < 2.0

# count_pairs on large list
nums = [random.randint(0, 1000) for _ in range(100000)]
target = random.randint(0, 2000)
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs on 100k elements: {elapsed:.2f}s (should be < 2s)")
assert elapsed < 2.0

# dedupe_keep_order on large list
items = [random.randint(0, 1000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order on 200k items: {elapsed:.2f}s (should be < 2s)")
assert elapsed < 2.0

print("\nAll tests passed!")