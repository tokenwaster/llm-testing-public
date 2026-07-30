import time
import perf

def test_correctness():
    # common_elements
    assert perf.common_elements([1, 2, 3, 2, 1], [2, 3, 4]) == [2, 3]
    assert perf.common_elements([], [1, 2]) == []
    assert perf.common_elements([5, 4, 3], [3, 4, 5]) == [3, 4, 5]

    # fib
    assert perf.fib(0) == 0
    assert perf.fib(1) == 1
    assert perf.fib(2) == 1
    assert perf.fib(10) == 55
    assert perf.fib(20) == 6765

    # count_pairs
    assert perf.count_pairs([1, 2, 3, 4], 5) == 2  # (1,4), (2,3)
    assert perf.count_pairs([1, 1, 1, 1], 2) == 6  # C(4,2) = 6
    assert perf.count_pairs([1, 2, 3], 10) == 0

    # dedupe_keep_order
    assert perf.dedupe_keep_order([3, 1, 2, 3, 1]) == [3, 1, 2]
    assert perf.dedupe_keep_order([]) == []
    assert perf.dedupe_keep_order(['a', 'b', 'a', 'c']) == ['a', 'b', 'c']

    print("All correctness tests passed!")

def test_performance():
    # Budget 1: common_elements on two 200,000-element lists under 2s
    a = list(range(200000))
    b = list(range(100000, 300000))
    t0 = time.perf_counter()
    res1 = perf.common_elements(a, b)
    t1 = time.perf_counter()
    dt1 = t1 - t0
    print(f"common_elements 200k time: {dt1:.4f}s (len res: {len(res1)})")
    assert dt1 < 2.0

    # Budget 2: fib(300) under 2s
    t0 = time.perf_counter()
    res2 = perf.fib(300)
    t1 = time.perf_counter()
    dt2 = t1 - t0
    print(f"fib(300) time: {dt2:.4f}s (res digits: {len(str(res2))})")
    assert dt2 < 2.0

    # Budget 3: count_pairs on 100,000 elements under 2s
    nums = (list(range(50000)) + list(range(50000)))
    t0 = time.perf_counter()
    res3 = perf.count_pairs(nums, 50000)
    t1 = time.perf_counter()
    dt3 = t1 - t0
    print(f"count_pairs 100k time: {dt3:.4f}s (count: {res3})")
    assert dt3 < 2.0

    # Budget 4: dedupe_keep_order on 200,000 items under 2s
    items = list(range(100000)) * 2
    t0 = time.perf_counter()
    res4 = perf.dedupe_keep_order(items)
    t1 = time.perf_counter()
    dt4 = t1 - t0
    print(f"dedupe_keep_order 200k time: {dt4:.4f}s (len res: {len(res4)})")
    assert dt4 < 2.0

if __name__ == '__main__':
    test_correctness()
    test_performance()
