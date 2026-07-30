import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# --- Correctness checks ---
print("=== Correctness ===")

# common_elements
assert common_elements([1,2,3], [2,3,4]) == [2, 3]
assert common_elements([], [1,2]) == []
assert common_elements([5], [5]) == [5]
print("common_elements: OK")

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(10) == 55
assert fib(300) > 0  # just check it runs and returns a positive int
print("fib: OK")

# count_pairs
assert count_pairs([1,2,3,4], 5) == 2   # (1,4),(2,3)
assert count_pairs([], 0) == 0
assert count_pairs([1,1,1], 2) == 3      # C(3,2)=3
print("count_pairs: OK")

# dedupe_keep_order
assert dedupe_keep_order([1,2,1,3,2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([5]) == [5]
print("dedupe_keep_order: OK")

# --- Performance checks ---
print("\n=== Performance ===")

random.seed(42)
a = [random.randint(-10**9, 10**9) for _ in range(200_000)]
b = [random.randint(-10**9, 10**9) for _ in range(200_000)]

t0 = time.time()
common_elements(a, b)
print(f"common_elements (200k): {time.time()-t0:.3f}s")

t0 = time.time()
fib(300)
print(f"fib(300): {time.time()-t0:.3f}s")

nums = [random.randint(-10**9, 10**9) for _ in range(100_000)]
target = nums[0] + nums[1]
t0 = time.time()
count_pairs(nums, target)
print(f"count_pairs (100k): {time.time()-t0:.3f}s")

items = [random.randint(0, 50) for _ in range(200_000)]
t0 = time.time()
dedupe_keep_order(items)
print(f"dedupe_keep_order (200k): {time.time()-t0:.3f}s")

print("\nAll checks passed!")
