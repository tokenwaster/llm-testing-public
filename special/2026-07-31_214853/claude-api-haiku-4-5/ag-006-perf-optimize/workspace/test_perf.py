#!/usr/bin/env python3
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test 1: common_elements
print("Testing common_elements...")
# Small test
result = common_elements([1, 2, 3, 4], [3, 4, 5, 6])
assert result == [3, 4], f"Expected [3, 4], got {result}"
print("  Small test passed")

# Large test
a = list(range(100000)) + list(range(100000, 200000))
b = list(range(50000, 250000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"  Large test (200k elements): {elapsed:.3f}s - {'PASS' if elapsed < 2 else 'FAIL'}")
print(f"    Result length: {len(result)}, first few: {result[:5]}, last few: {result[-5:]}")

# Test 2: fib
print("\nTesting fib...")
# Small tests
assert fib(0) == 0, f"Expected fib(0)=0, got {fib(0)}"
assert fib(1) == 1, f"Expected fib(1)=1, got {fib(1)}"
assert fib(2) == 1, f"Expected fib(2)=1, got {fib(2)}"
assert fib(3) == 2, f"Expected fib(3)=2, got {fib(3)}"
assert fib(4) == 3, f"Expected fib(4)=3, got {fib(4)}"
assert fib(5) == 5, f"Expected fib(5)=5, got {fib(5)}"
assert fib(10) == 55, f"Expected fib(10)=55, got {fib(10)}"
print("  Small tests passed")

# Large test
start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"  fib(300): {elapsed:.3f}s - {'PASS' if elapsed < 2 else 'FAIL'}")
print(f"    Result: {result}")

# Test 3: count_pairs
print("\nTesting count_pairs...")
# Small tests
result = count_pairs([1, 2, 3, 4, 5], 6)
print(f"  count_pairs([1,2,3,4,5], 6) = {result}")
# Expected: (1,5), (2,4) = 2 pairs
assert result == 2, f"Expected 2 pairs, got {result}"

# Test with duplicates
result = count_pairs([1, 1, 1, 1], 2)
assert result == 6, f"Expected 6 pairs of (1,1), got {result}"  # C(4,2) = 6
print("  Small tests passed")

# Large test
import random
random.seed(42)
nums = [random.randint(0, 100000) for _ in range(100000)]
start = time.time()
result = count_pairs(nums, 100000)
elapsed = time.time() - start
print(f"  Large test (100k elements): {elapsed:.3f}s - {'PASS' if elapsed < 2 else 'FAIL'}")
print(f"    Pair count: {result}")

# Test 4: dedupe_keep_order
print("\nTesting dedupe_keep_order...")
# Small test
result = dedupe_keep_order([1, 2, 2, 3, 1, 4, 4, 4])
assert result == [1, 2, 3, 4], f"Expected [1, 2, 3, 4], got {result}"
print("  Small test passed")

# Large test
items = list(range(100000)) + list(range(100000))
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"  Large test (200k items): {elapsed:.3f}s - {'PASS' if elapsed < 2 else 'FAIL'}")
print(f"    Unique count: {len(result)}, first few: {result[:5]}, last few: {result[-5:]}")

print("\nAll tests completed!")
