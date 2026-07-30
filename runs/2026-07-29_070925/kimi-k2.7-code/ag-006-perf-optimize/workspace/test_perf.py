import perf
import random
import time

# Correctness checks
assert perf.common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert perf.common_elements([5, 5, 5], [5]) == [5]
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.count_pairs([1, 2, 3, 4], 5) == 2
assert perf.count_pairs([1, 1, 1], 2) == 3
assert perf.dedupe_keep_order([4, 1, 2, 1, 3, 4]) == [4, 1, 2, 3]

# common_elements timing
a = list(range(200000))
b = list(range(100000, 300000))
t0 = time.perf_counter()
res = perf.common_elements(a, b)
t1 = time.perf_counter()
assert res == list(range(100000, 200000))
print(f"common_elements: {t1 - t0:.3f}s")
assert t1 - t0 < 2

# fib timing
t0 = time.perf_counter()
res = perf.fib(300)
t1 = time.perf_counter()
print(f"fib: {t1 - t0:.3f}s")
assert t1 - t0 < 2
assert res == 222232244629420445529739893461909967206666939096499764990979600

# count_pairs timing
random.seed(0)
nums = [random.randint(-10000, 10000) for _ in range(100000)]
t0 = time.perf_counter()
res = perf.count_pairs(nums, 50)
t1 = time.perf_counter()
print(f"count_pairs: {t1 - t0:.3f}s")
assert t1 - t0 < 2

# dedupe timing
t0 = time.perf_counter()
res = perf.dedupe_keep_order(nums)
t1 = time.perf_counter()
print(f"dedupe_keep_order: {t1 - t0:.3f}s")
assert t1 - t0 < 2

print("All checks passed")
