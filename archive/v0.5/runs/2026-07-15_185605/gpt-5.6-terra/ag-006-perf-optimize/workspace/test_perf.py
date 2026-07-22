import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

assert common_elements([3, 1, 2, 3], [4, 3, 2, 2]) == [2, 3]
assert common_elements([[1], [2], [1]], [[2], [1]]) == [[1], [2]]
assert [fib(n) for n in range(11)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600
assert count_pairs([1, 5, 7, -1, 5], 6) == 3
assert count_pairs([3, 3, 3], 6) == 3
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert dedupe_keep_order([[1], [2], [1]]) == [[1], [2]]

start = time.perf_counter(); common_elements(list(range(200000)), list(range(100000, 300000))); assert time.perf_counter()-start < 2
start = time.perf_counter(); fib(300); assert time.perf_counter()-start < 2
start = time.perf_counter(); count_pairs(list(range(100000)), 99999); assert time.perf_counter()-start < 2
start = time.perf_counter(); dedupe_keep_order(list(range(200000))); assert time.perf_counter()-start < 2
print('ok')
