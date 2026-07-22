import random
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness checks
print("Correctness:")

# common_elements
a = [3, 1, 2, 3, 4, 1, 5]
b = [3, 5, 6, 1, 7, 2]
print("common_elements:", common_elements(a, b))  # [1, 2, 3, 5]

# fib
print("fib(0..10):", [fib(i) for i in range(11)])
print("fib(100):", fib(100))
print("fib(300):", fib(300))

# count_pairs
print("count_pairs [1,2,3,4,5], 6:", count_pairs([1, 2, 3, 4, 5], 6))  # (1,5),(2,4) = 2
print("count_pairs [1,1,1,1], 2:", count_pairs([1, 1, 1, 1], 2))  # 6
print("count_pairs [1,2,3], 10:", count_pairs([1, 2, 3], 10))  # 0

# dedupe_keep_order
print("dedupe:", dedupe_keep_order([3, 1, 2, 1, 3, 4, 2, 5]))  # [3,1,2,4,5]

print("\nTiming tests:")

# common_elements on 200,000 elements
n = 200_000
ra = list(range(n))
rb = [random.randint(0, n) for _ in range(n)]
t0 = time.time()
r = common_elements(ra, rb)
print(f"common_elements({n}, {n}): {time.time()-t0:.3f}s, {len(r)} results")

# fib(300)
t0 = time.time()
f = fib(300)
print(f"fib(300): {time.time()-t0:.3f}s, value has {len(str(f))} digits")

# count_pairs on 100,000 elements
nums = [random.randint(0, 1000) for _ in range(100_000)]
t0 = time.time()
c = count_pairs(nums, 500)
print(f"count_pairs({len(nums)}): {time.time()-t0:.3f}s, count={c}")

# dedupe_keep_order on 200,000 items
items = [random.randint(0, 50_000) for _ in range(200_000)]
t0 = time.time()
d = dedupe_keep_order(items)
print(f"dedupe_keep_order({len(items)}): {time.time()-t0:.3f}s, {len(d)} unique")
