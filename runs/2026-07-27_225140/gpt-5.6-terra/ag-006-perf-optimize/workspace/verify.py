import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

assert common_elements([3, 1, 2, 2], [2, 3, 3]) == [2, 3]
assert fib(0) == 0 and fib(1) == 1 and fib(10) == 55 and fib(300) == 222232244629420445529739893461909967206666939096499764990979600
assert count_pairs([1, 5, 7, -1, 5], 6) == 3
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]

cases = [
    (common_elements, (list(range(200_000)), list(range(100_000, 300_000)))),
    (fib, (300,)),
    (count_pairs, ([i % 1000 for i in range(100_000)], 999)),
    (dedupe_keep_order, ([i % 100_000 for i in range(200_000)],)),
]
for function, args in cases:
    start = time.perf_counter()
    function(*args)
    elapsed = time.perf_counter() - start
    print(function.__name__, f'{elapsed:.4f}s')
    assert elapsed < 2
