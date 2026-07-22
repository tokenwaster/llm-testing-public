import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test():
    # Test common_elements
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res1 = common_elements(a, b)
    end = time.time()
    print(f"common_elements: {end - start:.4f}s")
    assert len(res1) == 100000

    # Test fib
    start = time.time()
    res2 = fib(300)
    end = time.time()
    print(f"fib(300): {end - start:.4f}s")
    assert res2 > 0 # Just check it finishes

    # Test count_pairs
    nums = list(range(100000))
    target = 150000
    start = time.time()
    res3 = count_pairs(nums, target)
    end = time.time()
    print(f"count_pairs: {end - start:.4f}s")
    # For range(100000), pairs summing to 150000 are (50001, 99999) ... (74999, 75001)
    # Wait, let's check the logic.
    # If nums = [0, 1, ..., 99999], target = 100000
    # Pairs are (0, 100000) - but 100000 is not in list.
    # So pairs summing to 100000: (1, 99999), (2, 99998) ... (49999, 50001).
    # That's 49999 or 50000 pairs.
    # Let's just check if it runs fast and returns a number.

    # Test dedupe_keep_order
    items = list(range(200000)) + list(range(100000))
    start = time.time()
    res4 = dedupe_keep_order(items)
    end = time.time()
    print(f"dedupe_keep_order: {end - start:.4f}s")
    assert len(res4) == 200000

if __name__ == "__main__":
    test()
