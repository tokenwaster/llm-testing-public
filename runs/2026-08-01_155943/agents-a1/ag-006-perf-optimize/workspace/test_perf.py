import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Test correctness of each function

def test_common_elements():
    assert sorted(common_elements([1,2,3], [2,3,4])) == [2,3]
    # With duplicates and unsorted input
    a = [5, 1, 3, 5, 7, 3, 9]
    b = [3, 5, 8, 5, 6]
    result = common_elements(a, b)
    assert sorted(set(a) & set(b)) == result == [3, 5]

    # Empty lists
    assert common_elements([], []) == []
    assert common_elements([1], []) == []
    assert common_elements([], [1]) == []

    print("common_elements tests passed")

def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(4) == 3
    assert fib(5) == 5
    assert fib(10) == 55
    print("fib tests passed")

def test_count_pairs():
    nums = [1,3,2,4]
    # pairs: (0,3): 1+4=5; (1,2): 3+2=5 => 2 pairs
    assert count_pairs(nums, 5) == 2

    nums = [1,3,1,2]
    # pairs: (0,1)=1+3=4; (1,2)=3+1=4 => 2 pairs
    assert count_pairs(nums, 4) == 2

    # with duplicates: all three indices form a pair summing to 2
    # choose(3,2) = 3 pairs: (0,1), (0,2), (1,2). All sums to 2.
    assert count_pairs([1,1,1], 2) == 3

    print("count_pairs tests passed")

def test_dedupe_keep_order():
    # Preserve order of first occurrence only once
    items = [1,2,1,3,4,2,5]
    assert dedupe_keep_order(items) == [1,2,3,4,5]

    items = []
    assert dedupe_keep_order(items) == []

    print("dedupe_keep_order tests passed")

# Run correctness tests first
test_common_elements()
test_fib()
test_count_pairs()
test_dedupe_keep_order()
print("\nAll correctness tests passed!\n")

# Now run timing benchmarks
import random
random.seed(0)  # for reproducibility

def benchmark(func, *args):
    start = time.time()
    func(*args)
    end = time.time()
    return end - start

print("=== Timing Benchmarks ===")

# common_elements: two 200k-element lists (random ints between 1 and 10000 to have some overlap)
n = 200_000
a = [random.randint(1, 10000) for _ in range(n)]
b = [random.randint(1, 10000) for _ in range(n)]

t = benchmark(common_elements, a, b)
print(f"common_elements: {t:.3f}s")
if t > 2.0:
    print("WARNING: exceeding 2s budget!")

# fib(300) - should be nearly instant with iterative approach
n = 300
t = benchmark(fib, n)
print(f"fib({n}): {t:.4f}s")
if t > 2.0:
    print("WARNING: exceeding 2s budget!")

# count_pairs on 100k elements (random ints between -5000 and 5000, target=0)
m = 100_000
nums = [random.randint(-5000, 5000) for _ in range(m)]

t = benchmark(count_pairs, nums, 0)
print(f"count_pairs: {t:.3f}s")
if t > 2.0:
    print("WARNING: exceeding 2s budget!")

# dedupe_keep_order on 200k items (random ints between 1 and 10000 to have many duplicates)
p = 200_000
items = [random.randint(1, 10000) for _ in range(p)]

t = benchmark(dedupe_keep_order, items)
print(f"dedupe_keep_order: {t:.3f}s")
if t > 2.0:
    print("WARNING: exceeding 2s budget!")

print("\nAll benchmarks completed.")
