import time
import perf

def test_common_elements():
    a = [1, 2, 3, 4, 5]
    b = [3, 4, 5, 6, 7]
    assert perf.common_elements(a, b) == [3, 4, 5]
    
    a = [1, 2, 2, 3]
    b = [2, 2, 4]
    assert perf.common_elements(a, b) == [2]

    # Large test
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = perf.common_elements(a, b)
    end = time.time()
    assert res == list(range(100000, 200000))
    assert end - start < 2

def test_fib():
    assert perf.fib(0) == 0
    assert perf.fib(1) == 1
    assert perf.fib(2) == 1
    assert perf.fib(3) == 2
    assert perf.fib(10) == 55
    assert perf.fib(300) > 0 # Should not hang
    
    start = time.time()
    res = perf.fib(300)
    end = time.time()
    assert end - start < 2
    # Check a known value for fib(300) if possible, or just ensure it's an int
    assert isinstance(res, int)

def test_count_pairs():
    nums = [1, 2, 3, 4, 3]
    target = 6
    # (2,4) -> 2+4=6, (3,3) -> 3+3=6. Wait, indices i < j.
    # nums[1]=2, nums[3]=4 -> 2+4=6.
    # nums[2]=3, nums[4]=3 -> 3+3=6.
    # Total 2 pairs.
    assert perf.count_pairs(nums, target) == 2

    nums = [1, 1, 1, 1]
    target = 2
    # (0,1), (0,2), (0,3), (1,2), (1,3), (2,3) -> 6 pairs
    assert perf.count_pairs(nums, target) == 6

    # Large test
    nums = [1] * 100000
    target = 2
    start = time.time()
    res = perf.count_pairs(nums, target)
    end = time.time()
    # n=100,000, pairs = n*(n-1)/2 = 100000 * 99999 / 2 = 4999950000
    assert res == 4999950000
    assert end - start < 2

def test_dedupe_keep_order():
    assert perf.dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    assert perf.dedupe_keep_order([]) == []
    assert perf.dedupe_keep_order([1, 1, 1]) == [1]

    # Large test
    items = list(range(200000)) + [0]
    start = time.time()
    res = perf.dedupe_keep_order(items)
    end = time.time()
    assert res == list(range(200000))
    assert end - start < 2

if __name__ == "__main__":
    print("Testing common_elements...")
    test_common_elements()
    print("Testing fib...")
    test_fib()
    print("Testing count_pairs...")
    test_count_pairs()
    print("Testing dedupe_keep_order...")
    test_dedupe_keep_order()
    print("All tests passed!")
