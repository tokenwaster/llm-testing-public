import time, random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

# --- Correctness checks ---

# common_elements
a = [random.randint(0, 1000) for _ in range(500)]
b = [random.randint(500, 1500) for _ in range(500)]
expected = sorted(set([x for x in a if x in set(b)]))
assert common_elements(a, b) == expected

# fib
def fib_slow(n):
    if n < 2: return n
    return fib_slow(n - 1) + fib_slow(n - 2)
for k in [0, 1, 2, 5, 10, 20, 50, 100]:
    assert fib(k) == fib_slow(k) if k < 25 else True
# Reference for larger: known Fibonacci values
known = {0:0,1:1,2:1,3:2,4:3,5:5,6:8,7:13,8:21,9:34,10:55,20:6765,50:12586269025}
for k,v in known.items():
    assert fib(k) == v

# count_pairs
nums = [random.randint(0, 50) for _ in range(300)]
target = 25
def cp_slow(nums, target):
    c=0
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if nums[i]+nums[j]==target: c+=1
    return c
for _ in range(5):
    nums = [random.randint(0, 50) for _ in range(200)]
    target = random.randint(0, 100)
    assert count_pairs(nums, target) == cp_slow(nums, target)

# Edge: target = 2*x with same value
nums = [1,1,1,1]
assert count_pairs(nums, 2) == 6  # 4 choose 2
assert count_pairs([5], 10) == 0
assert count_pairs([], 0) == 0

# dedupe_keep_order
def dko_slow(items):
    out=[]
    for x in items:
        if x not in out: out.append(x)
    return out
items = [random.randint(0, 20) for _ in range(500)]
assert dedupe_keep_order(items) == dko_slow(items)
# unhashable list items? Test with strings
assert dedupe_keep_order(['a','b','a','c','b','d']) == ['a','b','c','d']

print("Correctness OK")

# --- Timing ---
random.seed(0)

t=time.perf_counter()
a = [random.randint(0, 10_000_000) for _ in range(200_000)]
b = [random.randint(0, 10_000_000) for _ in range(200_000)]
common_elements(a, b)
print(f"common_elements 200k x 200k: {time.perf_counter()-t:.3f}s")

t=time.perf_counter()
print(f"fib(300) = {fib(300)}; {time.perf_counter()-t:.3f}s")

t=time.perf_counter()
nums = [random.randint(0, 1000) for _ in range(100_000)]
target = random.randint(0, 2000)
print(f"count_pairs 100k: {count_pairs(nums, target)}; {time.perf_counter()-t:.3f}s")

t=time.perf_counter()
items = [random.randint(0, 1000) for _ in range(200_000)]
print(f"dedupe_keep_order 200k: {len(dedupe_keep_order(items))} unique; {time.perf_counter()-t:.3f}s")
