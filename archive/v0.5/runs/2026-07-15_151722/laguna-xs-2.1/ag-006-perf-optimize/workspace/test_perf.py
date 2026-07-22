import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("Testing correctness...")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = common_elements(a, b)
expected = [3, 4, 5]
assert result == expected, f"common_elements failed: {result} != {expected}"
print("common_elements: PASS")

# fib
for n in range(10):
    result = fib(n)
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34][n]
    assert result == expected, f"fib({n}) failed: {result} != {expected}"
# Correct fib(300) value
assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600, "fib(300) failed"
print("fib: PASS")

# count_pairs
nums = [1, 2, 3, 4, 5]
target = 6
result = count_pairs(nums, target)
expected = 2  # (1,5) and (2,4)
assert result == expected, f"count_pairs failed: {result} != {expected}"
print("count_pairs: PASS")

# dedupe_keep_order
items = [1, 2, 3, 2, 1, 4]
result = dedupe_keep_order(items)
expected = [1, 2, 3, 4]
assert result == expected, f"dedupe_keep_order failed: {result} != {expected}"
print("dedupe_keep_order: PASS")

print("\nAll correctness tests passed!")

# Test performance
print("\nTesting performance...")

# common_elements on 200k elements
a = [random.randint(0, 10000) for _ in range(200000)]
b = [random.randint(0, 10000) for _ in range(200000)]
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements(200k): {elapsed:.3f}s (limit: 2s) - {'PASS' if elapsed < 2 else 'FAIL'}")

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s (limit: 2s) - {'PASS' if elapsed < 2 else 'FAIL'}")

# count_pairs on 100k elements
nums = [random.randint(0, 1000) for _ in range(100000)]
target = 1000
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs(100k): {elapsed:.3f}s (limit: 2s) - {'PASS' if elapsed < 2 else 'FAIL'}")

# dedupe_keep_order on 200k items
items = [random.randint(0, 10000) for _ in range(200000)]
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order(200k): {elapsed:.3f}s (limit: 2s) - {'PASS' if elapsed < 2 else 'FAIL'}")