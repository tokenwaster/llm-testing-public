#!/usr/bin/env python3
"""Quick verification and timing tests for perf.py optimizations."""

import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order


def test_correctness():
    """Verify functions produce correct results."""
    # Test common_elements
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([3, 1, 2], [2, 3, 4]) == [2, 3]
    assert common_elements([], [1, 2]) == []
    print("OK: common_elements correct")

    # Test fib
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    assert fib(20) == 6765
    print("OK: fib correct")

    # Test count_pairs
    assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,4) and (2,3)
    assert count_pairs([1, 1, 1], 2) == 3     # all three pairs sum to 2
    assert count_pairs([1, 2], 5) == 0
    print("OK: count_pairs correct")

    # Test dedupe_keep_order
    assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order([1]) == [1]
    print("OK: dedupe_keep_order correct")


def test_timing():
    """Verify functions meet timing budgets."""
    print("\nTiming tests:")

    # common_elements: 200k elements, under 2 seconds
    start = time.time()
    a = list(range(200000))
    b = list(range(100000, 300000))
    result = common_elements(a, b)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"common_elements took {elapsed:.3f}s (budget: 2s)"
    print(f"  common_elements(200k): {elapsed:.3f}s OK")

    # fib(300): under 2 seconds
    start = time.time()
    result = fib(300)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"fib(300) took {elapsed:.3f}s (budget: 2s)"
    print(f"  fib(300): {elapsed:.3f}s OK")

    # count_pairs: 100k elements, under 2 seconds
    start = time.time()
    nums = [random.randint(0, 1000) for _ in range(100000)]
    result = count_pairs(nums, 500)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"count_pairs took {elapsed:.3f}s (budget: 2s)"
    print(f"  count_pairs(100k): {elapsed:.3f}s OK")

    # dedupe_keep_order: 200k items, under 2 seconds
    start = time.time()
    items = [random.randint(0, 10000) for _ in range(200000)]
    result = dedupe_keep_order(items)
    elapsed = time.time() - start
    assert elapsed < 2.0, f"dedupe_keep_order took {elapsed:.3f}s (budget: 2s)"
    print(f"  dedupe_keep_order(200k): {elapsed:.3f}s OK")


if __name__ == "__main__":
    test_correctness()
    test_timing()
    print("\n[PASS] All tests passed!")
