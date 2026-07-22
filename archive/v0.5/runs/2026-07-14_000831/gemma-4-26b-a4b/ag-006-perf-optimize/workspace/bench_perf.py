import time
import random
import perf

def benchmark():
    print("Starting benchmarks...")

    # common_elements
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = perf.common_elements(a, b)
    duration = time.time() - start
    print(f"common_elements (200k elements): {duration:.4f}s")
    assert len(res) == 100000

    # fib(300)
    start = time.time()
    res = perf.fib(300)
    duration = time.time() - start
    print(f"fib(300): {duration:.4f}s")
    # Check if it's a large number (just to be sure, though we trust the logic)
    assert res > 0

    # count_pairs
    nums = [random.randint(0, 100000) for _ in range(100000)]
    target = 50000
    start = time.time()
    res = perf.count_pairs(nums, target)
    duration = time.time() - start
    print(f"count_pairs (100k elements): {duration:.4f}s")

    # dedupe_keep_order
    items = [random.randint(0, 200000) for _ in range(200000)]
    start = time.time()
    res = perf.dedupe_keep_order(items)
    duration = time.time() - start
    print(f"dedupe_keep_order (200k elements): {duration:.4f}s")

if __name__ == "__main__":
    benchmark()
