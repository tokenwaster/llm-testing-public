import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
assert common_elements([1,2,3], [2,3,4]) == [2,3]
assert common_elements([], [1]) == []
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(300) > 0
assert count_pairs([1,2,3,4,5], 5) == 2  # (1,4),(2,3)
assert count_pairs([], 0) == 0
assert dedupe_keep_order([1,2,2,3,1]) == [1,2,3]

# Timing tests
random.seed(42)
a = [random.randint(0, 100000) for _ in range(200000)]
b = [random.randint(0, 100000) for _ in range(200000)]
t = time.time(); common_elements(a, b); print(f"common_elements: {time.time()-t:.3f}s")

t = time.time(); fib(300); print(f"fib(300): {time.time()-t:.3f}s")

nums = [random.randint(0, 100000) for _ in range(100000)]
t = time.time(); count_pairs(nums, 50000); print(f"count_pairs: {time.time()-t:.3f}s")

items = [random.randint(0, 50000) for _ in range(200000)]
t = time.time(); dedupe_keep_order(items); print(f"dedupe_keep_order: {time.time()-t:.3f}s")

print("All tests passed!")
