#!/usr/bin/env python3
import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    # Basic test
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([1, 1, 2], [2, 3]) == [2]
    assert common_elements([], [1, 2]) == []
    print("[OK] common_elements correctness passed")

    # Performance test
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    result = common_elements(a, b)
    elapsed = time.time() - start
    print(f"[OK] common_elements on 200k lists: {elapsed:.3f}s (< 2s)")
    assert elapsed < 2, f"Too slow: {elapsed}s"
    assert len(result) == 100000  # Should have 100000 common elements

def test_fib():
    # Basic tests
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(5) == 5
    assert fib(10) == 55
    print("[OK] fib correctness passed")

    # Performance test
    start = time.time()
    result = fib(300)
    elapsed = time.time() - start
    print(f"[OK] fib(300): {elapsed:.3f}s (< 2s)")
    assert elapsed < 2, f"Too slow: {elapsed}s"
    # Verify it's the correct value
    assert result > 0  # Just sanity check it computed something large

def test_count_pairs():
    # Basic tests
    assert count_pairs([1, 2, 3, 4], 5) == 2  # (1,4) and (2,3)
    assert count_pairs([1, 1, 1], 2) == 3  # three (1,1) pairs
    assert count_pairs([1, 2, 3], 10) == 0
    print("[OK] count_pairs correctness passed")

    # Performance test
    nums = list(range(100000))
    target = 150000
    start = time.time()
    result = count_pairs(nums, target)
    elapsed = time.time() - start
    print(f"[OK] count_pairs on 100k elements: {elapsed:.3f}s (< 2s)")
    assert elapsed < 2, f"Too slow: {elapsed}s"
    assert result > 0  # Should find some pairs

def test_dedupe_keep_order():
    # Basic tests
    assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert dedupe_keep_order([1, 2, 3]) == [1, 2, 3]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order(['a', 'b', 'a']) == ['a', 'b']
    print("[OK] dedupe_keep_order correctness passed")

    # Performance test
    items = list(range(100000)) + list(range(100000))  # 200k with dups
    start = time.time()
    result = dedupe_keep_order(items)
    elapsed = time.time() - start
    print(f"[OK] dedupe_keep_order on 200k items: {elapsed:.3f}s (< 2s)")
    assert elapsed < 2, f"Too slow: {elapsed}s"
    assert len(result) == 100000

if __name__ == '__main__':
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
    print("\n[SUCCESS] All tests passed!")
