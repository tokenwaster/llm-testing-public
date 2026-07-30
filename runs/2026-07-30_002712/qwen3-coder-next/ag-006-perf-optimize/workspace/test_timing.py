import perf
import time

# Test common_elements on large lists
a = list(range(0, 200000, 2))
b = list(range(1, 200000, 2))
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f'common_elements: {elapsed:.3f}s (budget: <2s)')

# Test fib(300)
start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f'fib(300): {elapsed:.3f}s (budget: <2s)')

# Test count_pairs on large list
nums = list(range(100000))
start = time.time()
result = perf.count_pairs(nums, 1000)
elapsed = time.time() - start
print(f'count_pairs: {elapsed:.3f}s (budget: <2s)')

# Test dedupe_keep_order on large list
items = [i % 10000 for i in range(200000)]
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f'dedupe_keep_order: {elapsed:.3f}s (budget: <2s)')
