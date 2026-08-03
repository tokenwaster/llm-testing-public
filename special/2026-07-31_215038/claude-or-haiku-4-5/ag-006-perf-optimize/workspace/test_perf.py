import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

print("Testing common_elements...")
result = common_elements([1, 2, 3, 4], [3, 4, 5, 6])
assert result == [3, 4], f"Expected [3, 4], got {result}"
print("  Basic test passed")

result = common_elements([1, 1, 2, 3], [2, 3, 4])
assert result == [2, 3], f"Expected [2, 3], got {result}"
print("  Duplicate handling test passed")

start = time.time()
a = list(range(200000))
b = list(range(100000, 300000))
result = common_elements(a, b)
elapsed = time.time() - start
print(f"  Performance test (200k elements): {elapsed:.3f}s")
assert result == sorted(set(a) & set(b)), "Result mismatch"
print(f"  Found {len(result)} common elements")

print("\nTesting fib...")
assert fib(0) == 0
assert fib(1) == 1
assert fib(2) == 1
assert fib(3) == 2
assert fib(4) == 3
assert fib(5) == 5
assert fib(10) == 55
print("  Basic tests passed")

start = time.time()
result = fib(300)
elapsed = time.time() - start
print(f"  fib(300) = {result}")
print(f"  Time: {elapsed:.3f}s")
assert fib(10) == 55
assert fib(20) == 6765
print("  Correctness verified")

print("\nTesting count_pairs...")
result = count_pairs([1, 2, 3, 4, 5], 7)
assert result == 2, f"Expected 2, got {result}"
print("  Basic test passed")

result = count_pairs([1, 1, 1, 1], 2)
assert result == 6, f"Expected 6, got {result}"
print("  Duplicate test passed")

start = time.time()
nums = list(range(100000))
result = count_pairs(nums, 100000)
elapsed = time.time() - start
print(f"  Performance test (100k elements): {elapsed:.3f}s")
print(f"  Found {result} pairs")

print("\nTesting dedupe_keep_order...")
result = dedupe_keep_order([1, 2, 2, 3, 1, 4])
assert result == [1, 2, 3, 4], f"Expected [1, 2, 3, 4], got {result}"
print("  Basic test passed")

result = dedupe_keep_order([])
assert result == [], f"Expected [], got {result}"
print("  Empty list test passed")

result = dedupe_keep_order([1])
assert result == [1], f"Expected [1], got {result}"
print("  Single element test passed")

start = time.time()
items = list(range(100000)) + list(range(100000))
result = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"  Performance test (200k items): {elapsed:.3f}s")
assert len(result) == 100000, f"Expected 100000 unique items, got {len(result)}"
print(f"  Reduced to {len(result)} unique items")

print("\nAll tests passed!")
