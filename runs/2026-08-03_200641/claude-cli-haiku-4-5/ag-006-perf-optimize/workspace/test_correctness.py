from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test common_elements edge cases
print('Testing common_elements...')
assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
assert common_elements([1, 1, 2], [2, 3]) == [2]
assert common_elements([], [1, 2, 3]) == []
assert common_elements([1, 2], []) == []
assert common_elements([1, 2, 1], [1, 2, 1]) == [1, 2]
print('  common_elements: OK')

# Test fib
print('Testing fib...')
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(3) == 2
assert fib(4) == 3
assert fib(5) == 5
assert fib(10) == 55
print('  fib: OK')

# Test count_pairs edge cases
print('Testing count_pairs...')
assert count_pairs([1, 2, 3], 5) == 1  # (2,3)
assert count_pairs([1, 1, 1], 2) == 3  # (0,1), (0,2), (1,2)
assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,3), (2,1) = (1,4), (2,3)
assert count_pairs([], 5) == 0
assert count_pairs([1], 5) == 0
assert count_pairs([2, 2], 4) == 1  # (0,1)
print('  count_pairs: OK')

# Test dedupe_keep_order edge cases
print('Testing dedupe_keep_order...')
assert dedupe_keep_order([1, 2, 3]) == [1, 2, 3]
assert dedupe_keep_order([1, 1, 1]) == [1]
assert dedupe_keep_order([1, 2, 1, 2]) == [1, 2]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order(['a', 'b', 'a']) == ['a', 'b']
print('  dedupe_keep_order: OK')

print('\nAll correctness tests passed!')
