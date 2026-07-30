import time
import perf

# Test common_elements
a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.time()
result = perf.common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s, len={len(result)}, expected 100000")
assert len(result) == 100000
assert result == list(range(100000, 200000))
assert t1 - t0 < 2

# Test fib
t0 = time.time()
result = perf.fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s, result={result}")
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert t1 - t0 < 2

# Test count_pairs
import random
random.seed(42)
nums = [random.randint(0, 1000) for _ in range(100000)]
t0 = time.time()
result = perf.count_pairs(nums, 500)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s, count={result}")
assert t1 - t0 < 2

# Test dedupe_keep_order
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
result = perf.dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s, len={len(result)}")
assert t1 - t0 < 2

# Verify dedupe correctness
assert result == sorted(set(result), key=lambda x: items.index(x))

print("\nAll tests passed!")
