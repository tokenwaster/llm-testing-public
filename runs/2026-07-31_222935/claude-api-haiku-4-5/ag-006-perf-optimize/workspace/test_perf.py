import perf
import time

# Test common_elements
print("Testing common_elements...")
a = list(range(200000))
b = list(range(100000, 300000))
start = time.time()
result = perf.common_elements(a, b)
elapsed = time.time() - start
expected_len = 100000
print(f"  Result length: {len(result)} (expected {expected_len})")
print(f"  Time: {elapsed:.3f}s (budget: 2s)")
assert len(result) == expected_len, f"Expected {expected_len} elements, got {len(result)}"
assert result == sorted(result), "Result not sorted"
print("  PASS")

# Test fib
print("\nTesting fib...")
start = time.time()
result = perf.fib(300)
elapsed = time.time() - start
# Verify it's a very large number (fib(300) should be > 10^62)
assert result > 10**60, f"fib(300) should be very large, got {result}"
print(f"  Result is a very large integer (as expected)")
print(f"  Time: {elapsed:.3f}s (budget: 2s)")
print("  PASS")

# Test count_pairs
print("\nTesting count_pairs...")
nums = list(range(100000))
target = 100000
start = time.time()
result = perf.count_pairs(nums, target)
elapsed = time.time() - start
print(f"  Result: {result}")
print(f"  Time: {elapsed:.3f}s (budget: 2s)")
# With nums=[0,1,2,...,99999] and target=100000:
# Pairs that sum to 100000 with i<j: (1, 99999), (2, 99998), ..., (49999, 50001)
# That's 49999 pairs
assert result == 49999, f"Expected 49999 pairs, got {result}"
print("  PASS")

# Test dedupe_keep_order
print("\nTesting dedupe_keep_order...")
items = list(range(100000)) * 2  # 200,000 items with duplicates
start = time.time()
result = perf.dedupe_keep_order(items)
elapsed = time.time() - start
expected_len = 100000
print(f"  Result length: {len(result)} (expected {expected_len})")
print(f"  Time: {elapsed:.3f}s (budget: 2s)")
assert len(result) == expected_len, f"Expected {expected_len} elements, got {len(result)}"
assert result == list(range(100000)), "Result not in correct order"
print("  PASS")

print("\nAll tests passed!")
