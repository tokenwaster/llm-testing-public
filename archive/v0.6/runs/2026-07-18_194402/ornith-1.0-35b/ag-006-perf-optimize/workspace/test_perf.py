import perf, time, random
random.seed(0)

# common_elements
a = [random.randint(0, 500_000) for _ in range(200_000)]
b = [random.randint(0, 500_000) for _ in range(200_000)]
t0 = time.time(); r = perf.common_elements(a, b); print(f'common_elements: {time.time()-t0:.3f}s, len={len(r)}')

# fib
print('fib(300):', perf.fib(300))
t0 = time.time(); perf.fib(300); print(f'fib(300) time: {time.time()-t0:.4f}s')

# count_pairs
nums = [random.randint(-100, 100) for _ in range(100_000)]
t0 = time.time(); c = perf.count_pairs(nums, 50); print(f'count_pairs: {time.time()-t0:.3f}s, count={c}')

# dedupe_keep_order
items = [random.randint(0, 100_000) for _ in range(200_000)]
t0 = time.time(); r = perf.dedupe_keep_order(items); print(f'dedupe: {time.time()-t0:.3f}s, len={len(r)}')

# correctness checks
assert perf.fib(0) == 0 and perf.fib(1) == 1 and perf.fib(2) == 1 and perf.fib(10) == 55
assert perf.common_elements([1,2,3], [2,3,4]) == [2, 3]
# count_pairs: pairs summing to 6 in [1,2,3,4,5]: (1,5),(2,4) = 2
assert perf.count_pairs([1,2,3,4,5], 6) == 2
# dedupe
assert perf.dedupe_keep_order([3,1,2,1,3]) == [3, 1, 2]
print('all ok')
