import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test common_elements
print('Testing common_elements...')
start = time.time()
result = common_elements(list(range(200000)), list(range(100000, 300000)))
elapsed = time.time() - start
print(f'  Result length: {len(result)}, Time: {elapsed:.3f}s')
assert result == list(range(100000, 200000)), 'common_elements failed'

# Test fib(300)
print('Testing fib(300)...')
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f'  Result (first 20 chars): {str(result)[:20]}..., Time: {elapsed:.3f}s')

# Test count_pairs
print('Testing count_pairs...')
nums = list(range(100000))
start = time.time()
result = count_pairs(nums, 150000)
elapsed = time.time() - start
print(f'  Result: {result}, Time: {elapsed:.3f}s')

# Test dedupe_keep_order
print('Testing dedupe_keep_order...')
items = list(range(100000)) * 2
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f'  Result length: {len(result)}, Time: {elapsed:.3f}s')
assert result == list(range(100000)), 'dedupe_keep_order failed'

print('\nAll tests passed!')
