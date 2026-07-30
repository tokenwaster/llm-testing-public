import perf
import time

# Test common_elements on 200,000 elements
a = list(range(100000, 300000))
b = list(range(200000, 400000))
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements: {elapsed:.4f}s (budget: 2s), result length: {len(result)}")

# Test fib(300)
start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.4f}s (budget: 2s), result: {result}")

# Test count_pairs on 100,000 elements
nums = list(range(50000)) + list(range(50000))
target = 49999
start = time.time()
result = perf.count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs: {elapsed:.4f}s (budget: 2s), result: {result}")

# Test dedupe_keep_order on 200,000 items
items = list(range(100000)) + list(range(100000))
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order: {elapsed:.4f}s (budget: 2s), result length: {len(result)}")
