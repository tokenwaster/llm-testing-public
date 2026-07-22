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
    print(f"common_elements took {end - start:.4f}s. Result length: {len(res)}")
    assert len(res) == 100000

    # Test fib
    print("Testing fib(300)...")
    start = time.time()
    res = fib(300)
    end = time.time()
    print(f"fib(300) took {end - start:.4f}s.")
    # Check if it's a large number (approx 10^62)
    assert res > 0

    # Test count_pairs
    print("Testing count_pairs...")
    nums = list(range(1000)) # Smaller range for easy verification
    target = 1000
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time()
    print(f"count_pairs took {end - start:.4f}s.")
    # For range(1000), pairs summing to 1000:
    # (x, 1000-x) where x < 1000-x => 2x < 1000 => x < 500.
    # Since nums is range(1000), values are 0 to 999.
    # The smallest x such that 1000-x <= 999 is x=1.
    # So x can be 1, 2, ..., 499.
    # Total count = 499.
    assert res == 499

    # Test dedupe_keep_order
    print("Testing dedupe_keep_order...")
    items = list(range(200000)) + list(range(100000))
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time()
    print(f"dedupe_keep_order took {end - start:.4f}s.")
    assert len(res) == 200000

if __name__ == "__main__":
    test()
