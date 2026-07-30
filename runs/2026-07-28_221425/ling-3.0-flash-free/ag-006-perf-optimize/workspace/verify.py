import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test common_elements
a = [3, 1, 2, 3, 4, 5]
b = [4, 3, 5, 6, 7]
result = common_elements(a, b)
assert result == [3, 4, 5], f"common_elements failed: {result}"
print("common_elements correctness: PASS")

# Test fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(30) == 832040
print("fib correctness: PASS")

# Test count_pairs
assert count_pairs([1, 2, 3, 4, 5], 5) == 2  # (1,4), (2,3)
assert count_pairs([1, 1, 1], 2) == 3  # C(3,2) = 3
assert count_pairs([1, 5, 7, -1], 6) == 2  # (1,5), (7,-1)
print("count_pairs correctness: PASS")

# Test dedupe_keep_order
assert dedupe_keep_order([3, 1, 2, 3, 1, 4]) == [3, 1, 2, 4]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1, 1, 1]) == [1]
print("dedupe_keep_order correctness: PASS")

# Timing tests
print("\n--- Timing Tests ---")

# common_elements: two 200,000-element lists
import random
random.seed(42)
big_a = [random.randint(0, 500000) for _ in range(200000)]
big_b = [random.randint(0, 500000) for _ in range(200000)]
t = time.time()
r = common_elements(big_a, big_b)
elapsed = time.time() - t
print(f"common_elements (200k): {elapsed:.3f}s (limit 2s) {'PASS' if elapsed < 2 else 'FAIL'}")

# fib(300)
t = time.time()
r = fib(300)
elapsed = time.time() - t
print(f"fib(300): {elapsed:.6f}s (limit 2s) {'PASS' if elapsed < 2 else 'FAIL'}")

# count_pairs: 100,000 elements
big_nums = [random.randint(0, 100000) for _ in range(100000)]
t = time.time()
r = count_pairs(big_nums, 100000)
elapsed = time.time() - t
print(f"count_pairs (100k): {elapsed:.3f}s (limit 2s) {'PASS' if elapsed < 2 else 'FAIL'}")

# dedupe_keep_order: 200,000 items
big_items = [random.randint(0, 100000) for _ in range(200000)]
t = time.time()
r = dedupe_keep_order(big_items)
elapsed = time.time() - t
print(f"dedupe_keep_order (200k): {elapsed:.3f}s (limit 2s) {'PASS' if elapsed < 2 else 'FAIL'}")

print("\nAll tests done.")
