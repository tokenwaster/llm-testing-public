import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

a = list(range(200000))
b = list(range(100000, 300000))
t = time.time()
r = common_elements(a, b)
print('common', time.time() - t, r[:3], r[-3:])

print('fib300', fib(300))

n = list(range(100000))
t = time.time()
print('pairs', count_pairs(n, 100000), time.time() - t)

items = list(range(50000)) * 4
t = time.time()
r = dedupe_keep_order(items)
print('dedupe', time.time() - t, len(r))
