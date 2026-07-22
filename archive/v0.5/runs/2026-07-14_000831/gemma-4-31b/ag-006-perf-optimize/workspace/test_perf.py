
from perf import common_elements, fib, count_pairs, dedupe_keep_order
import time

def test_common_elements():
    a = list(range(1000))
    b = list(range(500, 1500))
    expected = list(range(500, 1000))
    result = common_elements(a, b)
    assert result == expected, f"Expected {expected}, got {result}"
    print("common_elements correctness: PASS")

def test_fib():
    # fib(0)=0, fib(1)=1, fib(2)=1, fib(3)=2, fib(4)=3, fib(5)=5, fib(6)=8...
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    print("fib correctness: PASS")

def test_count_pairs():
    nums = [1, 2, 3, 4, 3]
    target = 6
    # Pairs (i, j) with i < j and nums[i]+nums[j]==6:
    # (2, 3): 3 + 4 != 6
    # (1, 3): 2 + 4 == 6  (index 1 and 3)
    # (2, 4): 3 + 3 == 6  (index 2 and 4)
    # Total: 2
    assert count_pairs(nums, target) == 2
    print("count_pairs correctness: PASS")

def test_dedupe_keep_order():
    items = [1, 2, 3, 2, 1, 4]
    expected = [1, 2, 3, 4]
    result = dedupe_keep_order(items)
    assert result == expected, f"Expected {expected}, got {result}"
    print("dedupe_keep_order correctness: PASS")

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
    print("All tests passed!")
