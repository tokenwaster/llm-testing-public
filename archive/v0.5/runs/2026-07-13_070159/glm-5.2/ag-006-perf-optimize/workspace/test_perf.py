import time
import random
import sys
sys.path.insert(0, '.')
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness checks - brute force comparison for count_pairs
def count_pairs_brute(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count

assert common_elements([1,2,3,4], [3,4,5,6]) == [3,4]
assert common_elements([1,1,2], [1,2,2]) == [1,2]
assert common_elements([], [1,2]) == []
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(20) == 6765

# Verify count_pairs against brute force on small inputs
for _ in range(200):
    nums = [random.randint(0, 10) for _ in range(random.randint(0, 30))]
    target = random.randint(0, 20)
    assert count_pairs(nums, target) == count_pairs_brute(nums, target), (nums, target)

assert dedupe_keep_order([3,1,2,1,3,2]) == [3,1,2]
assert dedupe_keep_order([]) == []
print("Correctness: PASS")

# Performance checks
random.seed(42)
a = [random.randint(0, 500000) for _ in range(200000)]
b = [random.randint(0, 500000) for _ in range(200000)]
t = time.time(); common_elements(a, b); print(f"common_elements: {time.time()-t:.3f}s")

t = time.time(); fib(300); print(f"fib(300): {time.time()-t:.3f}s")

nums = [random.randint(0, 100000) for _ in range(100000)]
t = time.time(); count_pairs(nums, 50000); print(f"count_pairs: {time.time()-t:.3f}s")

items = [random.randint(0, 500000) for _ in range(200000)]
t = time.time(); dedupe_keep_order(items); print(f"dedupe_keep_order: {time.time()-t:.3f}s")
print("All done.")
