import time
import random
import perf

def test_correctness():
    # common_elements
    assert perf.common_elements([3, 1, 2, 3], [3, 2, 4]) == [2, 3]
    assert perf.common_elements([], [1, 2]) == []
    
    # fib
    assert perf.fib(0) == 0
    assert perf.fib(1) == 1
    assert perf.fib(2) == 1
    assert perf.fib(3) == 2
    assert perf.fib(10) == 55
    
    # count_pairs
    assert perf.count_pairs([1, 1, 1], 2) == 3
    assert perf.count_pairs([1, 2, 3, 4, 3], 5) == 3
    assert perf.count_pairs([], 10) == 0
    
    # dedupe_keep_order
    assert perf.dedupe_keep_order([3, 1, 2, 3, 1]) == [3, 1, 2]
    assert perf.dedupe_keep_order([]) == []
    
    print("Correctness tests passed!")

def test_performance():
    # common_elements on two 200,000-element lists: under 2 seconds
    a = [random.randint(0, 100000) for _ in range(200000)]
    b = [random.randint(0, 100000) for _ in range(200000)]
    
    t0 = time.perf_counter()
    res = perf.common_elements(a, b)
    t1 = time.perf_counter()
    print(f"common_elements took {t1 - t0:.4f} seconds, result len = {len(res)}")
    
    # fib(300): under 2 seconds
    t0 = time.perf_counter()
    res = perf.fib(300)
    t1 = time.perf_counter()
    print(f"fib(300) took {t1 - t0:.6f} seconds, result = {res}")
    
    # count_pairs on 100,000 elements: under 2 seconds
    nums = [random.randint(0, 100) for _ in range(100000)]
    t0 = time.perf_counter()
    res = perf.count_pairs(nums, 100)
    t1 = time.perf_counter()
    print(f"count_pairs took {t1 - t0:.4f} seconds, result = {res}")
    
    # dedupe_keep_order on 200,000 items: under 2 seconds
    items = [random.randint(0, 100000) for _ in range(200000)]
    t0 = time.perf_counter()
    res = perf.dedupe_keep_order(items)
    t1 = time.perf_counter()
    print(f"dedupe_keep_order took {t1 - t0:.4f} seconds, result len = {len(res)}")

if __name__ == "__main__":
    test_correctness()
    test_performance()
