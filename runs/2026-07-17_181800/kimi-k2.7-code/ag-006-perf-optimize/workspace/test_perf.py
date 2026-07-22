import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# common_elements
a = list(range(200000))
b = list(range(100000, 300000))
random.shuffle(a)
random.shuffle(b)
t0 = time.time()
res = common_elements(a, b)
t1 = time.time()
assert res == list(range(100000, 200000))
print("common_elements:", t1 - t0)

# fib
t0 = time.time()
res = fib(300)
t1 = time.time()
assert res == 222232244629420445529739893461909967206666939096499764990979600
print("fib(300):", t1 - t0)

# count_pairs
nums = list(range(100000))
random.shuffle(nums)
t0 = time.time()
res = count_pairs(nums, 99999)
t1 = time.time()
# pairs i<j with i+j=99999 -> i in [0,49999], j=99999-i > i => i < 49999.5 => 50000 pairs
assert res == 50000
print("count_pairs:", t1 - t0)

# dedupe_keep_order
items = [i % 100000 for i in range(200000)]
t0 = time.time()
res = dedupe_keep_order(items)
t1 = time.time()
assert res == list(range(100000))
print("dedupe_keep_order:", t1 - t0)

print("all passed")
