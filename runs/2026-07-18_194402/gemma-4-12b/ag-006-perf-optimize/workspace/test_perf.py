import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test():
    # Test common_elements
    print("Testing common_elements...")
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = common_elements(a, b)
    end = time.time()
    print(f"common_elements took {end - start:.4f}s")
    assert len(res) == 100000
    assert res == list(range(100000, 200000))

    # Test fib
    print("Testing fib...")
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"fib(300) took {end - start:.4f}s")
    assert res == 222232244629420445529739893461909967206666939096499764990979600

    # Test count_pairs
    print("Testing count_pairs...")
    nums = list(range(100000))
    target = 150000
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"count_pairs took {end - start:.4f}s")
    # For range(100000), pairs summing to 150000:
    # Pairs (x, y) such that x+y=150000 and 0 <= x < y <= 99999.
    # x must be at least 150000 - 99999 = 50001.
    # x must be less than 150000 / 2 = 75000.
    # So x is in [50001, 74999]. Number of values = 74999 - 50001 + 1 = 24999.
    assert res == 24999

    # Test dedupe_keep_order
    print("Testing dedupe_keep_order...")
    items = list(range(200000)) + list(range(100000))
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time()
    print(f"dedupe_keep_order took {end - start:.4f}s")
    assert len(res) == 200000
    assert res == list(range(200000))

if __name__ == "__main__":
    test()
