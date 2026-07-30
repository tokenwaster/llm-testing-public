import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# --- Correctness tests ---
print("=== Correctness ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
assert common_elements(a, b) == [3, 4, 5], f"got {common_elements(a, b)}"
print("common_elements: OK")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(20) == 6765
print("fib: OK")

# count_pairs
assert count_pairs([1, 2, 3, 4, 5], 5) == 2  # (1,4),(2,3)
assert count_pairs([1, 1, 1], 2) == 3  # (0,1),(0,2),(1,2)
assert count_pairs([], 0) == 0
assert count_pairs([3, -1, 2, 0], 2) == 2  # (-1,3),(0,2)
print("count_pairs: OK")

# dedupe_keep_order
assert dedupe_keep_order([3, 1, 2, 1, 3, 4]) == [3, 1, 2, 4]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1]) == [1]
print("dedupe_keep_order: OK")

# --- Performance tests ---
print("\n=== Performance ===")

# common_elements on 200k elements
a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.time()
result = common_elements(a, b)
t1 = time.time()
print(f"common_elements(200k): {t1-t0:.3f}s (budget: 2s) -> {'PASS' if t1-t0 < 2 else 'FAIL'}")

# fib(300)
t0 = time.time()
result = fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s (budget: 2s) -> {'PASS' if t1-t0 < 2 else 'FAIL'}")
assert result == 222232244629420445529739893461909967206666939096499764990979600

# count_pairs on 100k elements
nums = [random.randint(-1000, 1000) for _ in range(100000)]
t0 = time.time()
result = count_pairs(nums, 0)
t1 = time.time()
print(f"count_pairs(100k): {t1-t0:.3f}s (budget: 2s) -> {'PASS' if t1-t0 < 2 else 'FAIL'}")

# dedupe_keep_order on 200k items
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
result = dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order(200k): {t1-t0:.3f}s (budget: 2s) -> {'PASS' if t1-t0 < 2 else 'FAIL'}")

print("\nAll tests passed!")
