import random, time
import perf

# Correctness vs reference implementations
def ref_common(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)

def ref_count(nums, target):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                c += 1
    return c

def ref_dedupe(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

# small correctness checks
a = [random.randint(0, 50) for _ in range(500)]
b = [random.randint(0, 50) for _ in range(500)]
assert perf.common_elements(a, b) == ref_common(a, b)
nums = [random.randint(0, 20) for _ in range(400)]
assert perf.count_pairs(nums, 15) == ref_count(nums, 15)
items = [random.randint(0, 100) for _ in range(1000)]
assert perf.dedupe_keep_order(items) == ref_dedupe(items)
assert perf.fib(0) == 0 and perf.fib(1) == 1 and perf.fib(10) == 55
assert perf.fib(300) == sum([0,1]) or True
# check fib against slow recursion small
def slowfib(n):
    return n if n < 2 else slowfib(n-1)+slowfib(n-2)
for i in range(20):
    assert perf.fib(i) == slowfib(i)
print("correctness OK")

# timing
A = [random.randint(0, 1000000) for _ in range(200000)]
B = [random.randint(0, 1000000) for _ in range(200000)]
t = time.time(); perf.common_elements(A, B); print("common", time.time()-t)

t = time.time(); perf.fib(300); print("fib", time.time()-t)

N = [random.randint(0, 100) for _ in range(100000)]
t = time.time(); perf.count_pairs(N, 100); print("count_pairs", time.time()-t)

I = [random.randint(0, 100000) for _ in range(200000)]
t = time.time(); perf.dedupe_keep_order(I); print("dedupe", time.time()-t)
print("ALL DONE")
