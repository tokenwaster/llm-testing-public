import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness tests
print("=== Correctness Tests ===")

# Test common_elements with small lists
a = [1, 2, 3]
b = [2, 3, 4]
result = common_elements(a, b)
assert result == [2, 3], f"common_elements failed: {result}"
print("common_elements(small): OK")

# Test fib small values
for n in range(10):
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34][n]
    result = fib(n)
    assert result == expected, f"fib({n}) failed: got {result}, expect {expected}"
print("fib(small): OK")

# Test count_pairs small list
nums = [1, 2, 3, 4, 5]
target = 6
pairs = [(0, 2), (0, 3) if nums[0]+nums[3]==6 else None, (1, 3)]  # Actually let's count properly: pairs are indices (i,j) where i<j and sum=target
# With [1,2,3,4,5] target=6: pairs are (0,2)=1+3? No wait nums[0]=1, nums[2]=3 => 4!=6. Let me recalc
# Actually indices: 
# nums=[1,2,3,4,5], i<j
# (0,?): need 5 -> index 4 gives sum=6 -> pair (0,4) works
# (1,?) -> need 4 -> index 3 gives sum=6 -> pair (1,3) works  
# (2,?) -> need 3 -> index 2 already used i<j condition not possible since j>i required and nums[2]=3 itself... wait target-nums[i]
# Let's just test with a known count
result = count_pairs(nums, target)
expected = 2  # pairs: (0,4):1+5=6; (1,3):2+4=6
assert result == expected, f"count_pairs failed: got {result}, expect {expected}"
print("count_pairs(small): OK")

# Test dedupe_keep_order small list
items = [1, 2, 1, 3, 2, 4]
result = dedupe_keep_order(items)
assert result == [1, 2, 3, 4], f"dedupe failed: {result}"
print("dedupe(small): OK")

# Performance tests - generate large inputs and time them
import random
random.seed(0)

print("\n=== Performance Tests ===")

# common_elements with two 200k-element lists
a = [random.randint(1, 500000) for _ in range(200000)]
b = [random.randint(1, 500000) for _ in range(200000)]

start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements(200k each): {elapsed:.3f}s (must be < 2s)")

# fib(300)
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"fib(300): {elapsed:.3f}s, value={result} (must be < 2s)")

# count_pairs with 100k elements
nums = [random.randint(-50000, 50000) for _ in range(100000)]
target = random.randint(-50000, 50000)

start = time.time()
result = count_pairs(nums, target)
elapsed = time.time() - start
print(f"count_pairs(100k): {elapsed:.3f}s (must be < 2s)")

# dedupe_keep_order with 200k items
items = [random.randint(1, 500000) for _ in range(200000)]

start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order(200k): {elapsed:.3f}s (must be < 2s)")
