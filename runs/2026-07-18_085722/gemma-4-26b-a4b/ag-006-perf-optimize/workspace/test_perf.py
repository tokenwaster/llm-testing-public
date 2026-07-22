import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_correctness():
    print("Running correctness tests...")
    # common_elements
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([1, 1, 2], [1, 3]) == [1]
    assert common_elements([], [1, 2]) == []

    # fib
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(5) == 5
    assert fib(10) == 55

    # count_pairs
    assert count_pairs([1, 2, 3, 4, 3], 6) == 2  # (2,4), (3,3) - wait, indices i<j.
    # Let's re-check: nums[0]=1, nums[1]=2, nums[2]=3, nums[3]=4, nums[4]=3. target=6.
    # Pairs: (nums[1], nums[3]) = 2+4=6; (nums[2], nums[4]) = 3+3=6. Yes, 2 pairs.
    assert count_pairs([1, 1, 1], 2) == 3 # (0,1), (0,2), (1,2)

    # dedupe_keep_order
    assert dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    assert dedupe_keep_order([]) == []
    print("Correctness tests passed!")

def test_performance():
    print("\nRunning performance tests...")
    
    # common_elements: two 200,000-element lists < 2s
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = common_elements(a, b)
    duration = time.time() - start
    print(f"common_elements (200k): {duration:.4f}s")
    assert duration < 2

    # fib(300) < 2s
    start = time.time()
    res = fib(300)
    duration = time.time() - start
    print(f"fib(300): {duration:.4f}s")
    assert duration < 2

    # count_pairs: 100,000 elements < 2s
    nums = [random.randint(0, 100000) for _ in range(100000)]
    target = 50000
    start = time.time()
    res = count_pairs(nums, target)
    duration = time.time() - start
    print(f"count_pairs (100k): {duration:.4f}s")
    assert duration < 2

    # dedupe_keep_order: 200,000 items < 2s
    items = [random.randint(0, 50000) for _ in range(200000)]
    start = time.time()
    res = dedupe_keep_order(items)
    duration = time.time() - start
    print(f"dedupe_keep_order (200k): {duration:.4f}s")
    assert duration < 2

if __name__ == "__main__":
    test_correctness()
    test_performance()
