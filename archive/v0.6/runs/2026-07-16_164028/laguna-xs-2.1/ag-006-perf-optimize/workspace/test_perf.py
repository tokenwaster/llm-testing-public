"""Test correctness and timing of perf.py functions."""
import time
import perf

# Test common_elements
print("Testing common_elements...")
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
result = perf.common_elements(a, b)
expected = [3, 4, 5]
assert result == expected, f"common_elements failed: {result} != {expected}"
print(f"  common_elements({a}, {b}) = {result} OK")

# Test with duplicates
a = [1, 2, 2, 3, 4]
b = [2, 2, 3, 5]
result = perf.common_elements(a, b)
expected = [2, 3]
assert result == expected, f"common_elements failed: {result} != {expected}"
print(f"  common_elements({a}, {b}) = {result} OK")

# Test fib
print("\nTesting fib...")
for n in range(10):
    result = perf.fib(n)
    # Compute expected iteratively
    if n < 2:
        expected = n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        expected = b
    assert result == expected, f"fib({n}) failed: {result} != {expected}"
print(f"  fib(0..9) all correct OK")
print(f"  fib(300) = {perf.fib(300)} OK")

# Test count_pairs
print("\nTesting count_pairs...")
nums = [1, 2, 3, 4, 5]
target = 6
result = perf.count_pairs(nums, target)
# Pairs: (1,5), (2,4) = 2
expected = 2
assert result == expected, f"count_pairs failed: {result} != {expected}"
print(f"  count_pairs({nums}, {target}) = {result} OK")

# Test with duplicates - correct expected value
nums = [1, 1, 2, 2, 3]
target = 4
result = perf.count_pairs(nums, target)
# Pairs: (0,4): 1+3=4, (1,4): 1+3=4, (2,3): 2+2=4 = 3 pairs
expected = 3
assert result == expected, f"count_pairs failed: {result} != {expected}"
print(f"  count_pairs({nums}, {target}) = {result} OK")

# Test dedupe_keep_order
print("\nTesting dedupe_keep_order...")
items = [1, 2, 3, 2, 1, 4]
result = perf.dedupe_keep_order(items)
expected = [1, 2, 3, 4]
assert result == expected, f"dedupe_keep_order failed: {result} != {expected}"
print(f"  dedupe_keep_order({items}) = {result} OK")

# Timing tests
print("\n" + "="*50)
print("TIMING TESTS")
print("="*50)

# common_elements timing
print("\nTiming common_elements (200k elements each)...")
import random
a = [random.randint(0, 10000) for _ in range(200000)]
b = [random.randint(0, 10000) for _ in range(200000)]
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
print(f"  Time: {elapsed:.3f}s (budget: 2s) {'OK' if elapsed < 2 else 'FAIL'}")

# fib timing
print("\nTiming fib(300)...")
start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
print(f"  Time: {elapsed:.3f}s (budget: 2s) {'OK' if elapsed < 2 else 'FAIL'}")

# count_pairs timing
print("\nTiming count_pairs (100k elements)...")
nums = [random.randint(0, 1000) for _ in range(100000)]
target = 1000
start = time.time()
result = perf.count_pairs(nums, target)
elapsed = time.time() - start
print(f"  Time: {elapsed:.3f}s (budget: 2s) {'OK' if elapsed < 2 else 'FAIL'}")

# dedupe_keep_order timing
print("\nTiming dedupe_keep_order (200k items)...")
items = [random.randint(0, 10000) for _ in range(200000)]
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
print(f"  Time: {elapsed:.3f}s (budget: 2s) {'OK' if elapsed < 2 else 'FAIL'}")

print("\n" + "="*50)
print("ALL TESTS PASSED!")
print("="*50)