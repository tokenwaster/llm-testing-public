import perf

# Verify the module imports correctly and all functions work
print("Module imported successfully")
print("common_elements([1,2,3], [2,3,4]):", perf.common_elements([1,2,3], [2,3,4]))
print("fib(0):", perf.fib(0))
print("fib(1):", perf.fib(1))
print("fib(10):", perf.fib(10))
print("count_pairs([1,2,3,4], 5):", perf.count_pairs([1,2,3,4], 5))
print("dedupe_keep_order([1,2,1,3,2]):", perf.dedupe_keep_order([1,2,1,3,2]))
