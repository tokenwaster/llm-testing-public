import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness
assert common_elements([3, 1, 2, 2], [2, 3, 4]) == [2, 3]
assert fib(0) == 0 and fib(1) == 1 and fib(10) == 55
assert count_pairs([1, 2, 3, 4, 3], 6) == 2  # 2+4, 3+3
assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]

# Timing
t0 = time.perf_counter()
common_elements(list(range(200_000)), list(range(100_000, 300_000)))
print("common_elements:", time.perf_counter() - t0)

t0 = time.perf_counter()
print("fib(300):", fib(300), "time:", time.perf_counter() - t0)

import random
nums = [random.randint(0, 1000) for _ in range(100_000)]
t0 = time.perf_counter()
count_pairs(nums, 500)
print("count_pairs:", time.perf_counter() - t0)

items = [random.randint(0, 50000) for _ in range(200_000)]
t0 = time.perf_counter()
dedupe_keep_order(items)
print("dedupe:", time.perf_counter() - t0)

print("all ok")
