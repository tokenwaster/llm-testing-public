"""Quick verification of perf.py optimizations."""
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order


def test_common_elements():
    # Small test
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([5, 5, 1], [1, 5]) == [1, 5]

    # Large test
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    result = common_elements(a, b)
    elapsed = time.time() - start
    assert result == list(range(100000, 200000))
    print(f"common_elements (200k + 200k): {elapsed:.3f}s (budget: <2s)")
    assert elapsed < 2


def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(10) == 55

    start = time.time()
    result = fib(300)
    elapsed = time.time() - start
    print(f"fib(300): {elapsed:.3f}s (budget: <2s)")
    assert elapsed < 2


def test_count_pairs():
    assert count_pairs([1, 2, 3], 5) == 1  # (2, 3)
    assert count_pairs([1, 1, 1, 1], 2) == 6  # all pairs of the four 1s

    # Large test
    nums = list(range(100000))
    start = time.time()
    result = count_pairs(nums, 100000)
    elapsed = time.time() - start
    print(f"count_pairs (100k elements): {elapsed:.3f}s (budget: <2s)")
    assert elapsed < 2


def test_dedupe_keep_order():
    assert dedupe_keep_order([1, 2, 1, 3]) == [1, 2, 3]
    assert dedupe_keep_order([5, 5, 5]) == [5]
    assert dedupe_keep_order([]) == []

    # Large test
    items = list(range(100000)) + list(range(100000))
    start = time.time()
    result = dedupe_keep_order(items)
    elapsed = time.time() - start
    assert result == list(range(100000))
    print(f"dedupe_keep_order (200k items): {elapsed:.3f}s (budget: <2s)")
    assert elapsed < 2


if __name__ == "__main__":
    print("Testing common_elements...")
    test_common_elements()
    print("[PASS]\n")

    print("Testing fib...")
    test_fib()
    print("[PASS]\n")

    print("Testing count_pairs...")
    test_count_pairs()
    print("[PASS]\n")

    print("Testing dedupe_keep_order...")
    test_dedupe_keep_order()
    print("[PASS]\n")

    print("All tests passed!")
