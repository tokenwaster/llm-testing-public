
from perf import common_elements, fib, count_pairs, dedupe_keep_order
import time

def benchmark(name, func, *args):
    start = time.time()
    result = func(*args)
    end = time.time()
    duration = end - start
    print(f"{name} took {duration:.4f} seconds")
    return duration

def run_benchmarks():
    # common_elements: two 200,000-element lists
    a = list(range(200000))
    b = list(range(100000, 300000))
    benchmark("common_elements", common_elements, a, b)

    # fib(300)
    benchmark("fib(300)", fib, 300)

    # count_pairs: 100,000 elements
    nums = list(range(100000))
    target = 99999
    benchmark("count_pairs", count_pairs, nums, target)

    # dedupe_keep_order: 200,000 items
    items = list(range(100000)) + list(range(100000)) # 200k total, with duplicates
    benchmark("dedupe_keep_order", dedupe_keep_order, items)

if __name__ == "__main__":
    run_benchmarks()
