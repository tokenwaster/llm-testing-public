from perf import common_elements, fib, count_pairs, dedupe_keep_order

assert common_elements([3, 1, 2, 1], [2, 3, 3]) == [2, 3]
assert fib(0) == 0 and fib(1) == 1 and fib(10) == 55 and len(str(fib(300))) == 63
assert count_pairs([1, 1, 1, 2, 2], 3) == 6
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
print('ok')
