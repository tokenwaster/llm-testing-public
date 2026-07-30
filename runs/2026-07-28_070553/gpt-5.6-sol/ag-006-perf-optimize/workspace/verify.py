import random
import time
import perf

assert perf.common_elements([3, 1, 2, 2], [2, 3, 4, 3]) == [2, 3]
assert perf.common_elements([], [1]) == []
assert perf.fib(0) == 0
assert perf.fib(1) == 1
assert perf.fib(10) == 55
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600
assert perf.count_pairs([1, 1, 1], 2) == 3
assert perf.count_pairs([1, 2, 3, 4, 5], 6) == 2
assert perf.dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert perf.dedupe_keep_order([[1], [2], [1]]) == [[1], [2]]

cases = [([random.randint(-5, 5) for _ in range(20)], random.randint(-5, 5)) for _ in range(100)]
for nums, target in cases:
    expected = sum(nums[i] + nums[j] == target for i in range(len(nums)) for j in range(i + 1, len(nums)))
    assert perf.count_pairs(nums, target) == expected

def timed(name, fn):
    start = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - start
    print(name, f'{elapsed:.3f}s')
    assert elapsed < 2

random.seed(1)
a = [random.randrange(300000) for _ in range(200000)]
b = [random.randrange(300000) for _ in range(200000)]
nums = [random.randrange(10000) for _ in range(100000)]
items = [random.randrange(100000) for _ in range(200000)]
timed('common_elements', lambda: perf.common_elements(a, b))
timed('fib', lambda: perf.fib(300))
timed('count_pairs', lambda: perf.count_pairs(nums, 9999))
timed('dedupe_keep_order', lambda: perf.dedupe_keep_order(items))
print('all checks passed')
