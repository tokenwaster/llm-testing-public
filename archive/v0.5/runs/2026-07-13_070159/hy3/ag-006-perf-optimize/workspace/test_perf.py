import time
import random
import perf

# common_elements
a = list(range(200000))
b = list(range(100000, 300000))
t = time.time()
r = perf.common_elements(a, b)
print("common_elements:", time.time() - t, "len", len(r))
assert r == sorted(set(a) & set(b))

# fib
t = time.time()
f = perf.fib(300)
print("fib:", time.time() - t, f)
assert f == 222232244629420445529739893461909967206666939096499764990979600

# count_pairs
nums = [random.randint(0, 1000) for _ in range(100000)]
target = 500
t = time.time()
c = perf.count_pairs(nums, target)
print("count_pairs:", time.time() - t, c)
# brute check on small
small = nums[:200]
assert perf.count_pairs(small, target) == sum(
    1 for i in range(len(small)) for j in range(i+1, len(small))
    if small[i] + small[j] == target)

# dedupe
items = [random.randint(0, 50000) for _ in range(200000)]
t = time.time()
d = perf.dedupe_keep_order(items)
print("dedupe:", time.time() - t, len(d))
assert len(d) == len(set(items))
assert d == list(dict.fromkeys(items))

print("ALL OK")
