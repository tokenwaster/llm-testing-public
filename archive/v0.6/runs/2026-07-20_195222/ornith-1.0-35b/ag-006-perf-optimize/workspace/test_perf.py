import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness
assert common_elements([1,2,3], [2,3,4]) == [2, 3]
assert fib(0) == 0 and fib(1) == 1 and fib(10) == 55
assert count_pairs([1,1,1,1], 2) == 6
assert dedupe_keep_order([3,1,2,1,3]) == [3,1,2]
print('Correctness OK')

# Timing tests
random.seed(0)
a = random.sample(range(500_000), 200_000)
b = random.sample(range(500_000), 200_000)
t0 = time.time()
common_elements(a, b)
print(f'common_elements: {time.time()-t0:.3f}s')

t0 = time.time()
fib(300)
print(f'fib(300): {time.time()-t0:.6f}s')

nums = [random.randint(-1000, 1000) for _ in range(100_000)]
t0 = time.time()
count_pairs(nums, 0)
print(f'count_pairs: {time.time()-t0:.3f}s')

items = [random.randint(0, 100_000) for _ in range(200_000)]
t0 = time.time()
dedupe_keep_order(items)
print(f'dedupe_keep_order: {time.time()-t0:.3f}s')
