import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# --- correctness tests ---

# common_elements
assert common_elements([1,2,3], [2,3,4]) == [2,3]
assert common_elements([], [1,2]) == []
assert common_elements([1,2], []) == []
assert common_elements([3,1,2,2], [2,2,3,3]) == [2,3]

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(20) == 6765

# count_pairs
assert count_pairs([1,2,3,4], 5) == 2  # (1,4), (2,3)
assert count_pairs([1,1,1], 2) == 3    # (0,1), (0,2), (1,2)
assert count_pairs([], 0) == 0
assert count_pairs([1], 1) == 0

# dedupe_keep_order
assert dedupe_keep_order([1,2,3,2,1]) == [1,2,3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([5,5,5]) == [5]

print("All correctness tests passed!")

# --- timing tests ---
import random

# common_elements on 200k elements
a = [random.randint(0, 500000) for _ in range(200000)]
b = [random.randint(0, 500000) for _ in range(200000)]
t0 = time.time()
result = common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s (len={len(result)})")

# fib(300)
t0 = time.time()
r = fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.6f}s = {r}")

# count_pairs on 100k elements
nums = [random.randint(-10000, 10000) for _ in range(100000)]
target = random.randint(-20000, 20000)
t0 = time.time()
r = count_pairs(nums, target)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s (pairs={r})")

# dedupe_keep_order on 200k items
items = [random.randint(0, 50000) for _ in range(200000)]
t0 = time.time()
r = dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s (len={len(r)})")

print("All timing tests done!")