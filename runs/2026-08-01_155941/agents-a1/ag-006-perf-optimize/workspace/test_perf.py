import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness with small examples first
print("Testing correctness...")

a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
assert common_elements(a, b) == sorted(set(a) & set(b)) or common_elements(a, b) == [3, 4, 5], "common_elements failed"

assert fib(0) == 0 and fib(1) == 1 and fib(2) == 1 and fib(10) == 55, "fib failed"

nums = [1, 2, 3, 4]
target = 5
pairs = [(i,j) for i in range(len(nums)) for j in range(i+1,len(nums)) if nums[i]+nums[j]==target]
assert count_pairs(nums, target) == len(pairs), "count_pairs failed"

items = [1,2,3,2,4,1]
deduped = []
for x in items:
    if x not in deduped:
        deduped.append(x)
assert dedupe_keep_order(items) == deduped, "dedupe_keep_order failed"

print("Correctness tests passed!")

# Test performance on large inputs
import random

def test_common_elements():
    a = [random.randint(1, 2000000) for _ in range(200000)]
    b = [random.randint(1, 2000000) for _ in range(200000)]
    start = time.time()
    common_elements(a, b)
    elapsed = time.time() - start
    print(f"common_elements: {elapsed:.4f}s (limit: 2s)")
    assert elapsed < 2.0, "Too slow!"

def test_fib():
    start = time.time()
    fib(300)
    elapsed = time.time() - start
    print(f"fib(300): {elapsed:.4f}s (limit: 2s)")
    assert elapsed < 2.0, "Too slow!"

def test_count_pairs():
    nums = [random.randint(-1000, 1000) for _ in range(100000)]
    target = random.randint(-2000, 2000)
    start = time.time()
    count_pairs(nums, target)
    elapsed = time.time() - start
    print(f"count_pairs: {elapsed:.4f}s (limit: 2s)")
    assert elapsed < 2.0, "Too slow!"

def test_dedupe():
    items = [random.randint(1, 50) for _ in range(200000)]
    start = time.time()
    dedupe_keep_order(items)
    elapsed = time.time() - start
    print(f"dedupe_keep_order: {elapsed:.4f}s (limit: 2s)")
    assert elapsed < 2.0, "Too slow!"

test_common_elements()
test_fib()
test_count_pairs()
test_dedupe()
print("All performance tests passed!")
