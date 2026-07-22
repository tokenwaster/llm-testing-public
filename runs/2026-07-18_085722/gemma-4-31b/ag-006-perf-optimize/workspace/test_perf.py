import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    print("Testing common_elements...")
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = common_elements(a, b)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert res == list(range(100000, 200000))
    print("Passed!")

def test_fib():
    print("Testing fib...")
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    # Fib(10) is 55, Fib(20) is 6765
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    assert fib(20) == 6765
    print("Passed!")

def test_count_pairs():
    print("Testing count_pairs...")
    nums = [1] * 100000
    target = 2
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    # Pairs in [1]*100k with sum 2 is n*(n-1)//2
    assert res == (100000 * 99999) // 2
    print("Passed!")

def test_dedupe():
    print("Testing dedupe_keep_order...")
    items = [1, 2, 3, 1, 2, 4] * 33333 # ~200k elements
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert res == [1, 2, 3, 4]
    print("Passed!")

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe()
