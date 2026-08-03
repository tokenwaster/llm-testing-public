import perf
import time

a = list(range(1, 200001))
b = list(range(100001, 300001))
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f'common_elements: {elapsed:.3f}s, result length={len(result)}')
assert result == sorted(result), 'Not sorted'
assert result[0] == 100001 and result[-1] == 200000, 'Wrong range'

start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f'fib(300): {elapsed:.3f}s')

nums = list(range(100000))
target = 100000
start = time.time()
result = perf.count_pairs(nums, target)
elapsed = time.time() - start
print(f'count_pairs: {elapsed:.3f}s, result={result}')

items = list(range(100000)) + list(range(100000))
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f'dedupe_keep_order: {elapsed:.3f}s, result length={len(result)}')
assert len(result) == 100000, 'Dedup failed'
assert result == list(range(100000)), 'Order not preserved'

print('\nAll tests passed!')
