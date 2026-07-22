"""Verify that optimizations pass timing budgets and remain correct."""
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order


def test_common_elements():
    """Test correctness and timing for common_elements."""
    # Correctness
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([], [1, 2]) == []
    assert common_elements([1, 1, 2], [2, 2, 3]) == [2]

    # Timing: 200k elements
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    result = common_elements(a, b)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"common_elements took {elapsed:.2f}s (budget: 2s)"
    assert result == list(range(100000, 200000))
    print(f"[OK] common_elements: {elapsed:.3f}s")


def test_fib():
    """Test correctness and timing for fib."""
    # Correctness
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(10) == 55

    # Timing: fib(300)
    start = time.time()
    result = fib(300)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"fib(300) took {elapsed:.2f}s (budget: 2s)"
    # Known value for fib(300)
    expected = 222232244629420445529739893461909967206666333054025051891477282865129674205335143187413
    assert result == expected, f"fib(300) = {result}, expected {expected}"
    print(f"[OK] fib(300): {elapsed:.3f}s")


def test_count_pairs():
    """Test correctness and timing for count_pairs."""
    # Correctness
    assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,4), (2,3)
    assert count_pairs([1, 1, 1], 2) == 3  # (0,1), (0,2), (1,2)
    assert count_pairs([], 5) == 0
    assert count_pairs([5], 10) == 0

    # Timing: 100k elements
    nums = list(range(100000))
    start = time.time()
    result = count_pairs(nums, 100000)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"count_pairs took {elapsed:.2f}s (budget: 2s)"
    # For range(100k), pairs summing to 100k: (0,100k), (1,99999), ..., (50k-1, 50k+1)
    # That's 50k pairs
    assert result == 50000
    print(f"[OK] count_pairs: {elapsed:.3f}s")


def test_dedupe_keep_order():
    """Test correctness and timing for dedupe_keep_order."""
    # Correctness
    assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order([1]) == [1]
    assert dedupe_keep_order([1, 1, 1]) == [1]

    # Timing: 200k items
    items = list(range(200000)) + list(range(200000))
    start = time.time()
    result = dedupe_keep_order(items)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"dedupe_keep_order took {elapsed:.2f}s (budget: 2s)"
    assert result == list(range(200000))
    print(f"[OK] dedupe_keep_order: {elapsed:.3f}s")


if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
    print("\nAll tests passed!")
