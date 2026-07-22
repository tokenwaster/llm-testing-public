import perf
import random
import time

# Correctness checks
assert perf.common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.count_pairs([1, 2, 3, 4, 3], 6) == 2
assert perf.dedupe_keep_order([1, 2, 1, 3, 2, 4]) == [1, 2, 3, 4]

# Performance checks
random.seed(0)

a = [random.randint(0, 1000000) for _ in range(200000)]
b = [random.randint(0, 1000000) for _ in range(200000)]
t0 = time.perf_counter()
perf.common_elements(a, b)
print("common_elements:", time.perf_counter() - t0)

t0 = time.perf_counter()
perf.fib(300)
print("fib(300):", time.perf_counter() - t0)

nums = [random.randint(-100000, 100000) for _ in range(100000)]
t0 = time.perf_counter()
perf.count_pairs(nums, 0)
print("count_pairs:", time.perf_counter() - t0)

items = [random.randint(0, 1000000) for _ in range(200000)]
t0 = time.perf_counter()
perf.dedupe_keep_order(items)
print("dedupe_keep_order:", time.perf_counter() - t0)

print("All checks passed.")
