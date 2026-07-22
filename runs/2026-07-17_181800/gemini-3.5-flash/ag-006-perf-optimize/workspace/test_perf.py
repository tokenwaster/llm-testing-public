import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_perf():
    # Test common_elements
    print("Testing common_elements...")
    a = list(range(200000))
    b = list(range(100000, 300000))
    t0 = time.time()
    res = common_elements(a, b)
    t1 = time.time()
    print(f"common_elements took {t1 - t0:.4f}s, result length: {len(res)}")
    assert len(res) == 100000

    # Test fib
    print("Testing fib...")
    t0 = time.time()
    res = fib(300)
    t1 = time.time()
    print(f"fib(300) took {t1 - t0:.4f}s, result: {res}")
    assert res > 0

    # Test count_pairs
    print("Testing count_pairs...")
    nums = [1, 2, 3, 4, 5] * 20000 # 100,000 elements
    target = 6
    t0 = time.time()
    res = count_pairs(nums, target)
    t1 = time.time()
    print(f"count_pairs took {t1 - t0:.4f}s, result: {res}")

    # Test dedupe_keep_order
    print("Testing dedupe_keep_order...")
    items = [1, 2, 3, 4, 5] * 40000 # 200,000 elements
    t0 = time.time()
    res = dedupe_keep_order(items)
    t1 = time.time()
    print(f"dedupe_keep_order took {t1 - t0:.4f}s, result: {res}")
    assert res == [1, 2, 3, 4, 5]

if __name__ == "__main__":
    test_perf()
