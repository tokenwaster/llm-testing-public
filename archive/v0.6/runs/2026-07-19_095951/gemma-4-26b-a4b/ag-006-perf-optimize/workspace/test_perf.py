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
    assert count_pairs([1, 2, 3, 4, 3], 6) == 2  # (2,4), (3,3) - wait, indices i < j.
    # Let's re-check: nums[0]=1, nums[1]=2, nums[2]=3, nums[3]=4, nums[4]=3. target=6.
    # Pairs: (nums[2], nums[3]) is 3+4=7 NO.
    # Pairs: (nums[1], nums[3]) is 2+4=6 YES.
    # Pairs: (nums[2], nums[4]) is 3+3=6 YES.
    # So count should be 2 if we consider indices.
    # Let's re-verify the original code logic for count_pairs.
    # Original:
    # for i in range(len(nums)):
    #     for j in range(i + 1, len(nums)):
    #         if nums[i] + nums[j] == target:
    #             count += 1
    # For [1, 2, 3, 4, 3], target=6:
    # i=0 (1): j=1(2) sum 3; j=2(3) sum 4; j=3(4) sum 5; j=4(3) sum 4.
    # i=1 (2): j=2(3) sum 5; j=3(4) sum 6 (YES); j=4(3) sum 5.
    # i=2 (3): j=3(4) sum 7; j=4(3) sum 6 (YES).
    # i=3 (4): j=4(3) sum 7.
    # Total count = 2. Correct.
    assert count_pairs([1, 2, 3, 4, 3], 6) == 2
    assert count_pairs([1, 1, 1, 1], 2) == 6 # (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
    
    # dedupe_keep_order
    assert dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order([1, 1, 1]) == [1]

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
    assert duration < 2.0
    assert len(res) == 100000

    # fib(300) < 2s
    start = time.time()
    res = fib(300)
    duration = time.time() - start
    print(f"fib(300): {duration:.4f}s")
    assert duration < 2.0
    # Check a known value if possible, or just that it's large.
    # fib(300) is huge, so we don't need to check the exact value unless we want to.

    # count_pairs: 100,000 elements < 2s
    nums = [random.randint(0, 1000000) for _ in range(100000)]
    target = 500000
    start = time.time()
    res = count_pairs(nums, target)
    duration = time.time() - start
    print(f"count_pairs (100k): {duration:.4f}s")
    assert duration < 2.0

    # dedupe_keep_order: 200,000 items < 2s
    items = [random.randint(0, 100000) for _ in range(200000)]
    start = time.time()
    res = dedupe_keep_order(items)
    duration = time.time() - start
    print(f"dedupe_keep_order (200k): {duration:.4f}s")
    assert duration < 2.0

if __name__ == "__main__":
    test_correctness()
    test_performance()
