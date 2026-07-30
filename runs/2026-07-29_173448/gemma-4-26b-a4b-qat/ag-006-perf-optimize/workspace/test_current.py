from perf import common_elements, fib, count_pairs, dedupe_keep_order

def test_common_elements():
    assert common_elements([1, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_elements([1, 1, 2], [1, 3]) == [1]
    assert common_elements([1, 2], [3, 4]) == []
    assert common_elements([], [1, 2]) == []
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
    assert count_pairs([1, 1, 1], 2) == 3 # (0,1), (0,2), (1,2)
    assert count_pairs([1, 2, 3, 4, 5], 6) == 2 # (1,5) and (2,4) is not right.
    # wait, indices for (1,2,3,4,5) are 0,1,2,3,4.
    # target 6: 1+5 (indices 0,4), 2+4 (indices 1,3). Total 2.
    assert count_pairs([1, 2, 3, 4, 5], 6) == 2
    assert count_pairs([1, 5, 1, 5], 6) == 4
    assert count_pairs([1, 2, 3], 4) == 1 # (1,3) -> index (0,2)
    print("test_count_pairs passed")

def test_dedupe_keep_order():
    assert dedupe_keep_order([1, 2, 2, 3, 1, 4]) == [1, 2, 3, 4]
    assert dedupe_keep_order([5, 5, 5]) == [5]
    assert dedupe_keep_order([]) == []
    assert dedupe_keep_order([1, 2, 3]) == [1, 2, 3]
    print("test_dedupe_keep_order passed")

if __name__ == "__main__":
    test_common_elements()
    test_fib()
    test_count_pairs()
    test_dedupe_keep_order()
