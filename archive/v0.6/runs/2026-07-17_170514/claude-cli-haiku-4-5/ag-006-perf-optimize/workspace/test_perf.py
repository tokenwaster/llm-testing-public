"""Test correctness and timing of perf.py functions."""
import time
import sys
sys.path.insert(0, '.')

from perf import common_elements, fib, count_pairs, dedupe_keep_order


def test_common_elements():
    """Test common_elements correctness."""
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([1, 1, 2], [2, 2, 3]) == [2]
    assert common_elements([], [1, 2]) == []
    assert common_elements([1, 2], []) == []
    print("✓ common_elements correctness")

    # Timing test
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    result = common_elements(a, b)
    elapsed = time.time() - start
    print(f"  common_elements (200k elements): {elapsed:.3f}s")
    assert elapsed < 2.0, f"Exceeded budget: {elapsed}s"


def test_fib():
    """Test fib correctness."""
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    assert fib(20) == 6765
    print("✓ fib correctness")

    # Timing test
    start = time.time()
    result = fib(300)
    elapsed = time.time() - start
    print(f"  fib(300): {elapsed:.3f}s -> {result}")
    assert elapsed < 2.0, f"Exceeded budget: {elapsed}s"


def test_count_pairs():
    """Test count_pairs correctness."""
    assert count_pairs([1, 5, 7, -1], 6) == 2  # (1,5) and (7,-1)
    assert count_pairs([1, 1, 1, 1], 2) == 6   # 4 choose 2 = 6
    assert count_pairs([], 5) == 0
    assert count_pairs([1], 5) == 0
    print("✓ count_pairs correctness")

    # Timing test
    nums = list(range(100000))
    start = time.time()
    result = count_pairs(nums, 100000)
    elapsed = time.time() - start
    print(f"  count_pairs (100k elements): {elapsed:.3f}s")
    assert elapsed < 2.0, f"Exceeded budget: {elapsed}s"


def test_dedupe_keep_order():
    """Test dedupe_keep_order correctness."""
    assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert dedupe_keep_order([1, 1, 1]) == [1]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order([1]) == [1]
    print("✓ dedupe_keep_order correctness")

    # Timing test
    items = list(range(200000)) + list(range(200000))
    start = time.time()
    result = dedupe_keep_order(items)
    elapsed = time.time() - start
    print(f"  dedupe_keep_order (200k items): {elapsed:.3f}s")
    assert elapsed < 2.0, f"Exceeded budget: {elapsed}s"


if __name__ == '__main__':
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
    print("\n✓ All tests passed!")
