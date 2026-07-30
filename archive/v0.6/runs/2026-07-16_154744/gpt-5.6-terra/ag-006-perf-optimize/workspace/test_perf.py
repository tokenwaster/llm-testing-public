import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

assert common_elements([3, 1, 2, 3], [4, 2, 3, 3]) == [2, 3]
assert fib(0) == 0 and fib(1) == 1 and fib(10) == 55 and fib(300) == 222232244629420445529739893461909967206666939096499764990979600
assert count_pairs([1, 5, 7, -1, 5], 6) == 3
assert count_pairs([3, 3, 3, 3], 6) == 6
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert dedupe_keep_order([[1], [2], [1]]) == [[1], [2]]

def timed(name, fn):
    start = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - start
    print(name, elapsed)
    assert elapsed < 2

n = 200_000
timed('common', lambda: common_elements(list(range(n)), list(range(n // 2, n + n // 2))))
timed('fib', lambda: fib(300))
timed('pairs', lambda: count_pairs(list(range(100_000)), 99_999))
timed('dedupe', lambda: dedupe_keep_order(list(range(n)) + list(range(n))))
