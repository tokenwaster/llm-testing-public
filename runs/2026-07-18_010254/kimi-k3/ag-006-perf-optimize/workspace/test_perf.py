import random
import time

import perf


# --- Reference (original slow) implementations, used only on small inputs ---
def ref_common_elements(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def ref_fib(n):
    if n < 2:
        return n
    return ref_fib(n - 1) + ref_fib(n - 2)


def ref_count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def ref_dedupe_keep_order(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


rng = random.Random(42)

# Correctness: many small random cases compared against reference versions
for trial in range(300):
    la, lb = rng.randrange(0, 12), rng.randrange(0, 12)
    a = [rng.randrange(-5, 6) for _ in range(la)]
    b = [rng.randrange(-5, 6) for _ in range(lb)]
    assert perf.common_elements(a, b) == ref_common_elements(a, b)

    n = rng.randrange(0, 20)
    assert perf.fib(n) == ref_fib(n)

    nums = [rng.randrange(-6, 7) for _ in range(rng.randrange(0, 12))]
    target = rng.randrange(-8, 9)
    assert perf.count_pairs(nums, target) == ref_count_pairs(nums, target)

    items = [rng.randrange(0, 8) for _ in range(rng.randrange(0, 15))]
    assert perf.dedupe_keep_order(items) == ref_dedupe_keep_order(items)

# Edge cases
assert perf.common_elements([], []) == []
assert perf.common_elements([1, 1, 1], [1]) == [1]
assert perf.fib(0) == 0 and perf.fib(1) == 1 and perf.fib(10) == 55
assert perf.count_pairs([], 5) == 0
assert perf.count_pairs([2, 2, 2], 4) == 3
assert perf.count_pairs([1, 2, 3], 10) == 0
assert perf.dedupe_keep_order([]) == []
assert perf.dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600
print("all correctness checks passed")


def time_it(fn, *args):
    t0 = time.perf_counter()
    result = fn(*args)
    return time.perf_counter() - t0, result


# Timing budgets
a = [rng.randrange(0, 300000) for _ in range(200000)]
b = [rng.randrange(0, 300000) for _ in range(200000)]
t, _ = time_it(perf.common_elements, a, b)
print(f"common_elements(200k x 200k): {t:.4f}s")
assert t < 2

t, r = time_it(perf.fib, 300)
print(f"fib(300): {t:.6f}s")
assert t < 2

nums = [rng.randrange(-100000, 100001) for _ in range(100000)]
t, _ = time_it(perf.count_pairs, nums, 5000)
print(f"count_pairs(100k): {t:.4f}s")
assert t < 2

items = [rng.randrange(0, 50000) for _ in range(200000)]
t, res = time_it(perf.dedupe_keep_order, items)
print(f"dedupe_keep_order(200k): {t:.4f}s")
assert t < 2
assert sorted(res) == sorted(set(items)) and len(res) == len(set(items))

print("all timing budgets met")
