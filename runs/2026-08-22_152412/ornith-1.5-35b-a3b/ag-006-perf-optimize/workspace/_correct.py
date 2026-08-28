import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order


def orig_common(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def orig_fib(n):
    if n < 2:
        return n
    return orig_fib(n - 1) + orig_fib(n - 2)


def orig_pairs(nums, target):
    c = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                c += 1
    return c


def orig_dedupe(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


for _ in range(500):
    a = [random.randint(-5, 5) for _ in range(random.randint(0, 15))]
    b = [random.randint(-5, 5) for _ in range(random.randint(0, 15))]
    assert common_elements(a, b) == orig_common(a, b)
    nums = [random.randint(-10, 10) for _ in range(random.randint(0, 20))]
    t = random.randint(-5, 5)
    assert count_pairs(nums, t) == orig_pairs(nums, t), (nums, t)
    items = [random.randint(0, 4) for _ in range(random.randint(0, 20))]
    assert dedupe_keep_order(items) == orig_dedupe(items)

assert fib(300) == orig_fib(300)
print("ALL CORRECT")
