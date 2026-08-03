import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

random.seed(1)
a = [random.randint(0, 300000) for _ in range(200000)]
b = [random.randint(0, 300000) for _ in range(200000)]
t=time.time()
r = common_elements(a,b)
print("common_elements", time.time()-t, len(r))

t=time.time()
print("fib(300)=", fib(300), time.time()-t)

nums = [random.randint(0, 1000) for _ in range(100000)]
t=time.time()
print("count_pairs", count_pairs(nums, 500), time.time()-t)

items = [random.randint(0,1000) for _ in range(200000)]
t=time.time()
d = dedupe_keep_order(items)
print("dedupe", time.time()-t, len(d))
