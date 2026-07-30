import perf
import time
import random

# Test performance
print('Testing performance...', flush=True)

# common_elements: two 200k lists
random.seed(42)
a = [random.randint(0, 1000000) for _ in range(200000)]
b = [random.randint(0, 1000000) for _ in range(200000)]
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f'common_elements: {elapsed:.3f}s (budget: 2s)', flush=True)

# fib(300)
start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f'fib(300): {elapsed:.3f}s (budget: 2s)', flush=True)

# count_pairs: 100k elements
nums = [random.randint(0, 1000) for _ in range(100000)]
target = 1000
start = time.time()
result = perf.count_pairs(nums, target)
elapsed = time.time() - start
print(f'count_pairs: {elapsed:.3f}s (budget: 2s)', flush=True)

# dedupe_keep_order: 200k items
items = [random.randint(0, 50000) for _ in range(200000)]
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f'dedupe_keep_order: {elapsed:.3f}s (budget: 2s)', flush=True)

print('All performance tests passed!', flush=True)