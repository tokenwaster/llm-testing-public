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
    # Intersection of [0..199999] and [100000..299999] is [100000..199999]
    assert res == list(range(100000, 200000)), f"Expected range(100k-200k), got length {len(res)}"

def test_fib():
    print("Testing fib...")
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    # Fib(300) is a large number, just check it's an integer and positive
    assert isinstance(res, int) and res > 0

def test_count_pairs():
    print("Testing count_pairs...")
    nums = [1] * 100000
    target = 2
    # Pairs i < j: n*(n-1)//2
    expected = 100000 * 99999 // 2
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert res == expected

def test_dedupe():
    print("Testing dedupe_keep_order...")
    items = [i % 100 for i in range(200000)]
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time()
    print(f"Time: {end - start:.4f}s")
    assert len(res) == 100
    assert res == list(range(100))

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe()
    print("All tests passed!")
