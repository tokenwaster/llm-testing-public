import time
import perf

# Test correctness
print("=== Correctness ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = perf.common_elements(a, b)
print(f"common_elements([1,2,3,4,5], [3,4,5,6,7]) = {result}")
assert result == [3, 4, 5], f"Expected [3, 4, 5], got {result}"

# fib
for n, expected in [(0, 0), (1, 1), (2, 1), (3, 2), (4, 3), (5, 5), (10, 55)]:
    result = perf.fib(n)
    print(f"fib({n}) = {result}")
    assert result == expected, f"Expected {expected}, got {result}"

# count_pairs
nums = [1, 5, 7, -1, 5]
target = 6
result = perf.count_pairs(nums, target)
print(f"count_pairs([1,5,7,-1,5], 6) = {result}")
assert result == 3, f"Expected 3, got {result}"

# dedupe_keep_order
items = [3, 1, 2, 3, 4, 1, 5]
result = perf.dedupe_keep_order(items)
print(f"dedupe_keep_order([3,1,2,3,4,1,5]) = {result}")
assert result == [3, 1, 2, 4, 5], f"Expected [3, 1, 2, 4, 5], got {result}"

print("\n=== Performance ===")

# common_elements on 200k elements
import random
random.seed(42)
a_large = [random.randint(0, 400000) for _ in range(200000)]
b_large = [random.randint(0, 400000) for _ in range(200000)]
t0 = time.time()
perf.common_elements(a_large, b_large)
t1 = time.time()
print(f"common_elements 200k: {t1-t0:.3f}s (budget: 2s)")
assert t1 - t0 < 2, "common_elements too slow"

# fib(300)
t0 = time.time()
result = perf.fib(300)
t1 = time.time()
print(f"fib(300) = {result} in {t1-t0:.3f}s (budget: 2s)")
assert t1 - t0 < 2, "fib too slow"

# count_pairs on 100k elements
nums_large = [random.randint(-1000000, 1000000) for _ in range(100000)]
t0 = time.time()
perf.count_pairs(nums_large, 0)
t1 = time.time()
print(f"count_pairs 100k: {t1-t0:.3f}s (budget: 2s)")
assert t1 - t0 < 2, "count_pairs too slow"

# dedupe_keep_order on 200k items
items_large = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
perf.dedupe_keep_order(items_large)
t1 = time.time()
print(f"dedupe_keep_order 200k: {t1-t0:.3f}s (budget: 2s)")
assert t1 - t0 < 2, "dedupe_keep_order too slow"

print("\nAll tests passed!")
