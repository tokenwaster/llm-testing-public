from perf import common_elements, fib, count_pairs, dedupe_keep_order

# common_elements
assert common_elements([3, 1, 2, 2], [2, 4, 1, 1]) == [1, 2]
assert common_elements([], [1]) == []
assert common_elements([5, 5], [5]) == [5]

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(30) == 832040
assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600

# count_pairs
assert count_pairs([1, 2, 3, 4], 5) == 2  # 1+4, 2+3
assert count_pairs([1, 1, 1], 2) == 3
assert count_pairs([5, -1, 3, 2], 4) == 1  # only 5 + (-1)
assert count_pairs([], 0) == 0
assert count_pairs([1, 2], 4) == 0
assert count_pairs([2, 2, 2, 2], 4) == 6

# dedupe
assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order(["a", "b", "a"]) == ["a", "b"]

print("all correctness checks passed")

# rough timing smoke tests
import time
import random

N = 200_000
a = [random.randint(0, N) for _ in range(N)]
b = [random.randint(0, N) for _ in range(N)]
t0 = time.perf_counter()
r = common_elements(a, b)
t1 = time.perf_counter()
print(f"common_elements: {t1-t0:.3f}s, len={len(r)}")

t0 = time.perf_counter()
f = fib(300)
t1 = time.perf_counter()
print(f"fib(300): {t1-t0:.3f}s")

nums = [random.randint(-1000, 1000) for _ in range(100_000)]
t0 = time.perf_counter()
c = count_pairs(nums, 0)
t1 = time.perf_counter()
print(f"count_pairs: {t1-t0:.3f}s, count={c}")

items = [random.randint(0, N // 10) for _ in range(N)]
t0 = time.perf_counter()
d = dedupe_keep_order(items)
t1 = time.perf_counter()
print(f"dedupe: {t1-t0:.3f}s, len={len(d)}")
