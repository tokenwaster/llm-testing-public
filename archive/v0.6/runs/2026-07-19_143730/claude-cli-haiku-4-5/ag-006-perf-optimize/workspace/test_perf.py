"""Quick test of optimized perf.py functions."""
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test common_elements
print("Testing common_elements...")
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([], [1, 2]) == []
assert common_elements([1, 1, 2], [1, 2, 2]) == [1, 2]

a = list(range(100000)) + list(range(50000, 150000))
b = list(range(75000, 175000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"  200k-element lists: {elapsed:.3f}s")
assert elapsed < 2.0, f"common_elements timeout: {elapsed:.3f}s"

# Test fib
print("Testing fib...")
assert fib(0) == 0
assert fib(1) == 1
assert fib(5) == 5
assert fib(10) == 55

start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"  fib(300): {elapsed:.3f}s")
assert elapsed < 2.0, f"fib timeout: {elapsed:.3f}s"
# Verify correctness: fib(300) should be a large Fibonacci number
assert result > 0 and isinstance(result, int)

# Test count_pairs
print("Testing count_pairs...")
assert count_pairs([1, 2, 3], 5) == 1  # (2, 3)
assert count_pairs([1, 1, 1, 1], 2) == 6  # all pairs of 1+1
assert count_pairs([], 5) == 0
assert count_pairs([1], 5) == 0

nums = list(range(100000))
start = time.time()
result = count_pairs(nums, 100000)
elapsed = time.time() - start
print(f"  100k elements: {elapsed:.3f}s, found {result} pairs")
assert elapsed < 2.0, f"count_pairs timeout: {elapsed:.3f}s"

# Test dedupe_keep_order
print("Testing dedupe_keep_order...")
assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1, 1, 1]) == [1]
assert dedupe_keep_order([1, 2, 3]) == [1, 2, 3]

items = list(range(100000)) + list(range(100000))
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"  200k items: {elapsed:.3f}s, deduped to {len(result)}")
assert elapsed < 2.0, f"dedupe_keep_order timeout: {elapsed:.3f}s"
assert len(result) == 100000

print("\nAll tests passed!")
