from perf import common_elements, fib, count_pairs, dedupe_keep_order
import time

# Correctness
assert common_elements([3, 1, 2, 2], [2, 4, 1, 1]) == [1, 2]
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(30) == 832040
assert count_pairs([1, 5, 3, 3, 2], 6) == 2  # 1+5, 3+3
assert count_pairs([1, 1, 1], 2) == 3
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]

# Timing
t0 = time.time()
a = list(range(200000))
b = list(range(100000, 300000))
r = common_elements(a, b)
assert len(r) == 100000
print("common_elements:", time.time() - t0)

t0 = time.time()
r = fib(300)
print("fib(300):", r, "time:", time.time() - t0)

t0 = time.time()
nums = list(range(100000))
r = count_pairs(nums, 99999)
print("count_pairs:", r, "time:", time.time() - t0)

t0 = time.time()
items = list(range(100000)) + list(range(100000))
r = dedupe_keep_order(items)
assert r == list(range(100000))
print("dedupe:", time.time() - t0)

print("all ok")
