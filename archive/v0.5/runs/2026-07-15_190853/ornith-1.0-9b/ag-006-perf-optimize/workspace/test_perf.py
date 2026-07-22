import perf
import time

# Test correctness
print("common_elements:", perf.common_elements([1,2,3],[2,3,4]))
print("fib(10):", perf.fib(10))
print("count_pairs [1,5,7,-1,5] target=6:", perf.count_pairs([1,5,7,-1,5], 6))
print("dedupe_keep_order:", perf.dedupe_keep_order([1,2,1,3,2]))

# Performance tests
import random
random.seed(42)

# common_elements on 200k lists
a = list(range(200_000))
b = list(range(100_000, 300_000))
t0 = time.time()
result = perf.common_elements(a, b)
print(f"common_elements: {time.time()-t0:.3f}s, len={len(result)}")

# fib(300)
t0 = time.time()
r = perf.fib(300)
print(f"fib(300): {time.time()-t0:.3f}s, result={r}")

# count_pairs on 100k
nums = [random.randint(-10**9, 10**9) for _ in range(100_000)]
target = sum(nums[:2])
t0 = time.time()
c = perf.count_pairs(nums, target)
print(f"count_pairs: {time.time()-t0:.3f}s, count={c}")

# dedupe_keep_order on 200k
items = list(range(200_000)) + [random.randint(0, 1000) for _ in range(200_000)]
t0 = time.time()
d = perf.dedupe_keep_order(items)
print(f"dedupe_keep_order: {time.time()-t0:.3f}s, len={len(d)}")
