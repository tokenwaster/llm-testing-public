import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("Testing correctness...")

# common_elements
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([5, 1, 3, 7], [3, 8, 1, 9]) == [1, 3]

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(300) > 0

# count_pairs
assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,4), (2,3)
assert count_pairs([1, 1, 1], 2) == 3  # all pairs of 1s

# dedupe_keep_order
assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []

print("All correctness tests passed!")

# Test timing budgets
print("\nTesting performance...")

# common_elements on 200,000 elements
a = list(range(100000, 300000))
b = list(range(200000, 400000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements (200k elements): {elapsed:.3f}s (budget: <2s) {'PASS' if elapsed < 2 else 'FAIL'}")

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s (budget: <2s) {'PASS' if elapsed < 2 else 'FAIL'}")
print(f"  Result length: {len(str(result))} digits")

# count_pairs on 100,000 elements
nums = list(range(50000)) + list(range(50000))
target = 49999
start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs (100k elements): {elapsed:.3f}s (budget: <2s) {'PASS' if elapsed < 2 else 'FAIL'}")

# dedupe_keep_order on 200,000 items
items = list(range(100000)) + list(range(100000))
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order (200k items): {elapsed:.3f}s (budget: <2s) {'PASS' if elapsed < 2 else 'FAIL'}")

print("\nAll timing tests completed!")
