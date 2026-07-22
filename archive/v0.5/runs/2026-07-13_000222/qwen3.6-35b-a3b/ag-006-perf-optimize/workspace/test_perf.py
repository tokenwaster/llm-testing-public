import time
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# Correctness tests
print("=== Correctness ===")

# common_elements
a = [1, 2, 3, 4, 5]
b = [3, 4, 5, 6, 7]
print("common_elements:", common_elements(a, b))  # [3, 4, 5]

# fib
print("fib(0):", fib(0))   # 0
print("fib(1):", fib(1))   # 1
print("fib(10):", fib(10)) # 55
print("fib(20):", fib(20)) # 6765

# count_pairs
nums = [1, 2, 3, 4, 5]
print("count_pairs([1,2,3,4,5], 6):", count_pairs(nums, 6))  # 4 (1+5, 2+4, 3+3, 4+2 but i<j so 1+5,2+4,3+3 wait... let me check)
# pairs: (0,4)=1+5=6, (1,3)=2+4=6, (2,2) not valid since i<j, (1,4)=2+5=7 no, (2,3)=3+4=7 no
# Actually: (0,4)=6, (1,3)=6 => 2 pairs
print("count_pairs([1,2,3,4,5], 6):", count_pairs(nums, 6))

# dedupe_keep_order
items = [3, 1, 2, 1, 3, 4, 2, 5]
print("dedupe:", dedupe_keep_order(items))  # [3, 1, 2, 4, 5]

# Performance tests
print("\n=== Performance ===")

# common_elements on 200k lists
import random
random.seed(42)
a_big = [random.randint(0, 400000) for _ in range(200000)]
b_big = [random.randint(0, 400000) for _ in range(200000)]
t0 = time.time()
common_elements(a_big, b_big)
t1 = time.time()
print(f"common_elements 200k: {t1-t0:.3f}s (budget: 2s)")

# fib(300)
t0 = time.time()
fib(300)
t1 = time.time()
print(f"fib(300): {t1-t0:.3f}s (budget: 2s)")

# count_pairs on 100k elements
nums_big = [random.randint(-100000, 100000) for _ in range(100000)]
t0 = time.time()
count_pairs(nums_big, 0)
t1 = time.time()
print(f"count_pairs 100k: {t1-t0:.3f}s (budget: 2s)")

# dedupe_keep_order on 200k items
items_big = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.time()
dedupe_keep_order(items_big)
t1 = time.time()
print(f"dedupe 200k: {t1-t0:.3f}s (budget: 2s)")

print("\nAll done!")
