import perf
import time

# Test common_elements
a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.time()
r = perf.common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s, len={len(r)}, expected=100000")

# Test fib
t0 = time.time()
r = perf.fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.6f}s, value={r}")

# Test count_pairs
import random
random.seed(0)
nums = [random.randint(0, 1000) for _ in range(100000)]
t0 = time.time()
r = perf.count_pairs(nums, 500)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s, count={r}")

# Test dedupe_keep_order
items = list(range(100000)) * 2
random.shuffle(items)
t0 = time.time()
r = perf.dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s, len={len(r)}, expected=100000")