import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

random.seed(42)

# Test common_elements
a = [random.randint(0, 300000) for _ in range(200000)]
b = [random.randint(0, 300000) for _ in range(200000)]
t0 = time.time()
res = common_elements(a, b)
t1 = time.time()
print(f"common_elements: {t1-t0:.3f}s, found {len(res)} elements")
assert res == sorted(res), "not sorted"

# Test fib
t0 = time.time()
res = fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s")
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55

# Test count_pairs
nums = [random.randint(-100000, 100000) for _ in range(100000)]
t0 = time.time()
res = count_pairs(nums, 0)
t1 = time.time()
print(f"count_pairs: {t1-t0:.3f}s, pairs: {res}")

# Test dedupe_keep_order
items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
res = dedupe_keep_order(items)
t1 = time.time()
print(f"dedupe_keep_order: {t1-t0:.3f}s, unique: {len(res)}")
assert len(res) == len(set(res)), "duplicates remain"
first_seen = {}
for x in items:
    if x not in first_seen:
        first_seen[x] = True
assert res == [k for k in first_seen], "order wrong"

print("\nAll tests passed!")
