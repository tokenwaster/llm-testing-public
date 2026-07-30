import perf
import time

# Test common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
print("common_elements:", perf.common_elements(a, b))

# Test fib
print("fib(0):", perf.fib(0))
print("fib(1):", perf.fib(1))
print("fib(10):", perf.fib(10))
print("fib(300):", perf.fib(300))

# Test count_pairs
nums = [1, 2, 3, 4, 5]
target = 5
print("count_pairs:", perf.count_pairs(nums, target))

# Test dedupe_keep_order
items = [1, 2, 2, 3, 1, 4, 3]
print("dedupe_keep_order:", perf.dedupe_keep_order(items))

# Timing tests
print("\n--- Timing Tests ---")

# common_elements on large lists
a = list(range(100000, 300000))
b = list(range(200000, 400000))
start = time.time()
result = perf.common_elements(a, b)
print(f"common_elements (200k elements): {time.time() - start:.4f}s, len={len(result)}")

# fib(300)
start = time.time()
result = perf.fib(300)
print(f"fib(300): {time.time() - start:.4f}s")

# count_pairs on 100k elements
nums = list(range(100000))
target = 50000
start = time.time()
result = perf.count_pairs(nums, target)
print(f"count_pairs (100k elements): {time.time() - start:.4f}s")

# dedupe_keep_order on 200k items
items = list(range(100000)) + list(range(100000))
start = time.time()
result = perf.dedupe_keep_order(items)
print(f"dedupe_keep_order (200k items): {time.time() - start:.4f}s, len={len(result)}")
