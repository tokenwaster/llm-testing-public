import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
print("=== Correctness ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = common_elements(a, b)
expected = [3, 4, 5]
assert result == expected, f"common_elements failed: {result} != {expected}"
print("common_elements: PASS")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(300) > 0  # just check it completes
print("fib: PASS")

# count_pairs
nums = [1, 2, 3, 4, 5]
result = count_pairs(nums, 6)
expected = 4  # (1,5),(2,4),(3,3 is not i<j with values but nums[2]+nums[?])... let's compute: (1,5)=6, (2,4)=6, no other pairs sum to 6 except (5,1) which is same as (1,5) - wait indices. nums=[1,2,3,4,5], target=6: (0,4)=1+5=6, (1,3)=2+4=6 = 2 pairs
assert result == 2, f"count_pairs failed: {result} != 2"
print("count_pairs: PASS")

# dedupe_keep_order
items = [3, 1, 2, 1, 3, 4, 2]
result = dedupe_keep_order(items)
expected = [3, 1, 2, 4]
assert result == expected, f"dedupe failed: {result} != {expected}"
print("dedupe_keep_order: PASS")

# Test timing
print("\n=== Timing ===")

import random
random.seed(42)

a_large = [random.randint(0, 1_000_000) for _ in range(200_000)]
b_large = [random.randint(0, 1_000_000) for _ in range(200_000)]

t0 = time.time()
common_elements(a_large, b_large)
dt = time.time() - t0
print(f"common_elements(200k): {dt:.3f}s (budget: 2s) {'PASS' if dt < 2 else 'FAIL'}")

t0 = time.time()
fib(300)
dt = time.time() - t0
print(f"fib(300): {dt:.4f}s (budget: 2s) {'PASS' if dt < 2 else 'FAIL'}")

nums_large = [random.randint(-1000, 1000) for _ in range(100_000)]
t0 = time.time()
count_pairs(nums_large, 0)
dt = time.time() - t0
print(f"count_pairs(100k): {dt:.3f}s (budget: 2s) {'PASS' if dt < 2 else 'FAIL'}")

items_large = [random.randint(0, 50_000) for _ in range(200_000)]
t0 = time.time()
dedupe_keep_order(items_large)
dt = time.time() - t0
print(f"dedupe(200k): {dt:.3f}s (budget: 2s) {'PASS' if dt < 2 else 'FAIL'}")
