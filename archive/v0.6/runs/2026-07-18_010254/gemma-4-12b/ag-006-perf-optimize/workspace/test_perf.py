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
    print("Testing fib(300)...")
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"fib(300) took {end - start:.4f}s")
    # Check a few values to ensure correctness (e.g., fib(10)=55, fib(20)=6765)
    assert fib(10) == 55
    assert fib(20) == 6765

    # Test count_pairs
    print("Testing count_pairs...")
    nums = list(range(100000))
    target = 100000
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"count_pairs took {end - start:.4f}s")
    # For nums = range(100000), target = 100000:
    # Pairs are (x, y) with x+y=100000 and x < y.
    # Since values are unique, this means x < 50000 and y > 50000.
    # Also y = 100000 - x <= 99999 => x >= 1.
    # So x is in [1, 49999]. Total count = 49999.
    assert res == 49999

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
