import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    print("Testing common_elements...")
    # Test 1: Large inputs
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = common_elements(a, b)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert res == list(range(100000, 200000))
    # Test 2: No common elements
    assert common_elements([1, 2, 3], [4, 5, 6]) == []
    # Test 3: All common elements
    assert common_elements([1, 2, 3], [1, 2, 3]) == [1, 2, 3]
    # Test 4: Duplicates in input
    assert common_elements([1, 1, 2], [1, 1, 3]) == [1]

def test_fib():
    print("Testing fib...")
    # Correctness tests
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(4) == 3
    assert fib(5) == 5
    assert fib(10) == 55
    # Performance test
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert isinstance(res, int)

def test_count_pairs():
    print("Testing count_pairs...")
    # Correctness tests
    assert count_pairs([1, 2, 3, 4, 5], 6) == 2 # (1,5), (2,4)
    assert count_pairs([1, 1, 1], 2) == 3       # (0,1), (0,2), (1,2)
    assert count_pairs([1, 2, 3], 10) == 0
    # Performance test
    nums = list(range(100000))
    target = 100001
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    # For range(100000), pairs are (2, 99999), ..., (50000, 50001)
    # Wait, let's calculate exactly.
    # x + y = 100001 where 0 <= x < y < 100000
    # x can be from 2 to 50000. (If x=1, y=100000 which is out of range)
    # Number of values for x: 50000 - 2 + 1 = 49999.
    assert res == 49999

def test_dedupe():
    print("Testing dedupe...")
    # Correctness tests
    assert dedupe_keep_order([1, 2, 3, 1, 2]) == [1, 2, 3]
    assert dedupe_keep_order([1, 1, 1]) == [1]
    assert dedupe_keep_order([]) == []
    # Performance test
    items = [i % 100 for i in range(200000)]
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert len(res) == 100

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe()
    print("All tests passed!")
