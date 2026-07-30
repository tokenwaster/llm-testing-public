import perf

# Test common_elements
print('common_elements:', perf.common_elements([1,2,3], [2,3,4]))

# Test fib(300)
result = perf.fib(300)
print('fib(300):', result)

# Test count_pairs
print('count_pairs:', perf.count_pairs([1,2,3,4], 5))

# Test dedupe_keep_order
print('dedupe:', perf.dedupe_keep_order([1,2,1,3,2]))

# Verify correctness of fib(0) and fib(1)
print('fib(0):', perf.fib(0))
print('fib(1):', perf.fib(1))
