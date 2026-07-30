
from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([1, 1, 2], [1, 3]) == [1]
    assert common_elements([], [1, 2]) == []
    print("common_elements passed")

def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(4) == 3
    assert fib(5) == 5
    assert fib(10) == 55
    print("fib passed")

def test_count_pairs():
    assert count_pairs([1, 2, 3, 4, 5], 5) == 2 # (1,4), (2,3)
    assert count_pairs([1, 1, 1], 2) == 3      # (0,1), (0,2), (1,2)
    assert count_pairs([1, 2, 3], 10) == 0
    print("count_pairs passed")

def test_dedupe_keep_order():
    assert dedupe_keep_order([1, 2, 2, 3, 1]) == [1, 2, 3]
    assert dedupe_keep_order(['a', 'b', 'a', 'c']) == ['a', 'b', 'c']
    assert dedupe_keep_order([]) == []
    print("dedupe_keep_order passed")

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
    print("All tests passed!")
