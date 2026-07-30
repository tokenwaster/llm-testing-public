import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order
import random

def benchmark():
    print("Starting benchmarks...")

    # 1. common_elements on two 200,000-element lists
    a = list(range(200000))
    b = list(range(100000, 300000))
    start = time.time()
    res = common_elements(a, b)
    end = time.append = time.time() - start
    print(f"common_elements: {end:.4f}s (Result length: {len(res)})")
    assert len(res) == 100000

    # 2. fib(300)
    start = time.time()
    res = fib(300)
    end = time.time() - start
    print(f"fib(300): {end:.4f}s")
    # Check if it's a large number (just to be sure)
    assert res > 10**50

    # 3. count_pairs on 100,000 elements
    nums = [random.randint(0, 100000) for _ in range(100000)]
    target = 50000
    start = time.time()
    res = count_pairs(nums, target)
    end = time.time() - start
    print(f"count_pairs: {end:.4f}s")

    # 4. dedupe_keep_order on 200,000 items
    items = [random.randint(0, 100000) for _ in range(200000)]
    start = time.time()
    res = dedupe_keep_order(items)
    end = time.time() - start
    print(f"dedupe_keep_order: {end:.4f}s (Result length: {len(res)})")

if __name__ == "__main__":
    benchmark()
