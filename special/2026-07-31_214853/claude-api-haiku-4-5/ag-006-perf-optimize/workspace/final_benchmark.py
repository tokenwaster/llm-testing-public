"""Final performance benchmark against timing budgets."""
import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

BUDGET = 2.0

print("=== FINAL PERFORMANCE BENCHMARK ===\n")

print("1. common_elements on 200,000 elements")
a = list(range(100000)) + list(range(100000, 200000))
b = list(range(50000, 250000))
start = time.time()
result = common_elements(a, b)
elapsed = time.time() - start
status = "PASS" if elapsed < BUDGET else "FAIL"
print(f"   Time: {elapsed:.4f}s / {BUDGET}s [{status}]")
print(f"   Result: {len(result)} common elements\n")

print("2. fib(300)")
start = time.time()
result = fib(300)
elapsed = time.time() - start
status = "PASS" if elapsed < BUDGET else "FAIL"
print(f"   Time: {elapsed:.4f}s / {BUDGET}s [{status}]")
print(f"   Result: {str(result)[:50]}... ({len(str(result))} digits)\n")

print("3. count_pairs on 100,000 elements")
random.seed(42)
nums = [random.randint(0, 100000) for _ in range(100000)]
start = time.time()
result = count_pairs(nums, 100000)
elapsed = time.time() - start
status = "PASS" if elapsed < BUDGET else "FAIL"
print(f"   Time: {elapsed:.4f}s / {BUDGET}s [{status}]")
print(f"   Result: {result} pairs\n")

print("4. dedupe_keep_order on 200,000 items")
items = list(range(100000)) + list(range(100000))
start = time.time()
result = dedupe_keep_order(items)
elapsed = time.time() - start
status = "PASS" if elapsed < BUDGET else "FAIL"
print(f"   Time: {elapsed:.4f}s / {BUDGET}s [{status}]")
print(f"   Result: {len(result)} unique items\n")

print("=== ALL TESTS COMPLETED ===")
