import time
import perf

# Test correctness
print("Testing correctness...")
assert perf.common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.count_pairs([1, 2, 3, 4], 5) == 2
assert perf.dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
print("Correctness tests passed!")

# Test performance
print("\nTesting performance...")

start = time.time()
a = list(range(200000))
b = list(range(100000, 300000))
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements (200k elements): {elapsed:.3f}s")
assert elapsed < 2.0

start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s")
assert elapsed < 2.0

start = time.time()
nums = list(range(100000))
result = perf.count_pairs(nums, 1000)
elapsed = time.time() - start
print(f"count_pairs (100k elements): {elapsed:.3f}s")
assert elapsed < 2.0

start = time.time()
items = list(range(100000)) + list(range(100000))
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order (200k items): {elapsed:.3f}s")
assert elapsed < 2.0

print("\nAll performance tests passed!")
