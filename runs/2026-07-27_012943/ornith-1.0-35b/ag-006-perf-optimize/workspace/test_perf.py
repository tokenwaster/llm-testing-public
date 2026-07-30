"""Verify correctness and performance of perf.py."""
import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order


# --- Correctness checks ---
assert common_elements([1,2,3], [2,3,4]) == [2, 3]
assert common_elements([], [1]) == []
assert common_elements([5,5,5], [5,5]) == [5]

assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(300) > 0  # just non-zero sanity check

assert count_pairs([1,1,1], 2) == 3
assert count_pairs([1,2,3,4], 5) == 2   # (1,4),(2,3)
assert count_pairs([], 0) == 0

assert dedupe_keep_order([3,1,2,1,3]) == [3, 1, 2]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([5]) == [5]


# --- Timing checks ---
random.seed(42)
a = [random.randint(0, 1_000_000) for _ in range(200_000)]
b = [random.randint(0, 1_000_000) for _ in range(200_000)]

t0 = time.perf_counter()
common_elements(a, b)
dt = time.perf_counter() - t0
print(f"common_elements: {dt:.3f}s")
assert dt < 2.0

t0 = time.perf_counter()
fib(300)
dt = time.perf_counter() - t0
print(f"fib(300):        {dt:.3f}s")
assert dt < 2.0

nums = [random.randint(-1_000, 1_000) for _ in range(100_000)]
t0 = time.perf_counter()
count_pairs(nums, 0)
dt = time.perf_counter() - t0
print(f"count_pairs:     {dt:.3f}s")
assert dt < 2.0

items = [random.randint(0, 50_000) for _ in range(200_000)]
t0 = time.perf_counter()
dedupe_keep_order(items)
dt = time.perf_counter() - t0
print(f"dedupe:          {dt:.3f}s")
assert dt < 2.0

# Verify fib(300) exact value matches a reference
import math
def ref_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
assert fib(300) == ref_fib(300), "fib mismatch!"

print("ALL CHECKS PASSED")
