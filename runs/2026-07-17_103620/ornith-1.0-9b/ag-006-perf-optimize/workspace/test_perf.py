import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
assert common_elements([1,2,3], [2,3,4]) == [2, 3]
assert common_elements([], [1,2]) == []
assert common_elements([1,1,2], [2,2,3]) == [2]

assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(300) > 0

nums = [1, 2, 3, 4, 5]
assert count_pairs(nums, 7) == 2  # (2,5), (3,4)

items = [1, 2, 3, 2, 4, 1, 5]
assert dedupe_keep_order(items) == [1, 2, 3, 4, 5]

# Performance tests
import random
random.seed(42)

a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.time()
result = common_elements(a, b)
print(f"common_elements: {time.time()-t0:.3f}s, len={len(result)}")

t0 = time.time()
r = fib(300)
print(f"fib(300): {time.time()-t0:.3f}s, result digits={len(str(r))}")

nums = [random.randint(-10**9, 10**9) for _ in range(100000)]
target = nums[0] + nums[1]
t0 = time.time()
c = count_pairs(nums, target)
print(f"count_pairs: {time.time()-t0:.3f}s, count={c}")

items = [random.randint(0, 10**9) for _ in range(200000)]
t0 = time.time()
d = dedupe_keep_order(items)
print(f"dedupe_keep_order: {time.time()-t0:.3f}s, len={len(d)}")
