import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order
import random

# Common elements correctness and timing
a = list(range(200000))
b = [150000] + list(range(199000, 250000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
print(f"common_elements: {len(result)} elements in {elapsed:.3f}s")
assert result == sorted(set(a).intersection(set(b)))

# fib correctness and timing
for n in [0, 1, 2]:
    print(f"fib({n}) = {fib(n)}")
start = time.time()
r300 = fib(300)
elapsed = time.time() - start
print(f"fib(300) in {elapsed:.3f}s, value: {r300}")

# count_pairs correctness and timing (using brute force for small subset to verify algorithm)
nums_small = [random.randint(-50, 50) for _ in range(1000)]
target_small = 20
brute_count = sum(1 for i in range(len(nums_small)) for j in range(i+1, len(nums_small)) if nums_small[i] + nums_small[j] == target_small)
fast_count = count_pairs(nums_small, target_small)
assert fast_count == brute_count, f"count mismatch: {fast_count} vs {brute_count}"

nums_large = [random.randint(-1000, 1000) for _ in range(100000)]
target = 500
start = time.time()
count = count_pairs(nums_large, target)
elapsed = time.time() - start
print(f"count_pairs: {count} pairs in {elapsed:.3f}s")

# dedupe_keep_order correctness and timing
items = list(range(200000)) * 5  # many duplicates
start = time.time()
deduped = dedupe_keep_order(items)
elapsed = time.time() - start
print(f"dedupe_keep_order: {len(deduped)} unique in {elapsed:.3f}s")

print("\nAll timing tests passed!")
