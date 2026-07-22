from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    assert common_elements([1, 2, 3, 4, 5], [3, 4, 5, 6, 7]) == [3, 4, 5]
    assert common_elements([1, 1, 2, 2], [2, 2, 3]) == [2]
    assert common_elements([1, 2, 3], [4, 5, 6]) == []
    print("test_common_elements passed")

def test_fib():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(3) == 2
    assert fib(4) == 3
    assert fib(5) == 5
    assert fib(10) == 55
    print("test_fib passed")

def test_count_pairs():
    assert count_pairs([1, 2, 3, 4, 5], 5) == 2  # (1,4), (2,3)
    assert count_pairs([1, 1, 1, 1], 2) == 6      # (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
    assert count_pairs([1, 2, 3], 10) == 0
    print("test_count_pairs passed")

def test_dedupe_keep_order():
    assert dedupe_keep_order([1, 2, 2, 3, 4, 4, 5, 1]) == [1, 2, 3, 4, 5]
    assert dedupe_keep_order(['a', 'b', 'a', 'c']) == ['a', 'b', 'c']
    assert dedupe_keep_order([]) == []
    print("test_dedupe_keep_order passed")

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
