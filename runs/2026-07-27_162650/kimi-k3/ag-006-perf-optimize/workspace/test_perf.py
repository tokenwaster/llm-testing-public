import time
import perf

# ---- Correctness: compare against independent reference implementations ----

def ref_common_elements(a, b):
    seen = set()
    out = []
    for x in a:
        if x in set(b) and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)

def ref_fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def ref_count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count

def ref_dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# fib
for n in range(0, 31):
    assert perf.fib(n) == ref_fib(n), n
assert perf.fib(90) == 2880067194370816120
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600

# common_elements
cases = [
    ([], []),
    ([1, 2, 3], []),
    ([], [1, 2, 3]),
    ([1, 2, 2, 3], [2, 2, 4]),
    ([3, 1, 2], [2, 3, 1]),
    ([5, 5, 5], [5]),
    (["b", "a", "b"], ["a", "c", "b"]),
    ([7, -1, 0], [0, -1, 8, 7]),
]
for a, b in cases:
    assert perf.common_elements(a, b) == ref_common_elements(a, b), (a, b)

# count_pairs
pair_cases = [
    ([], 5),
    ([1], 2),
    ([1, 2, 3, 4], 5),
    ([2, 2, 2], 4),
    ([0, 0, 0, 0], 0),
    ([-1, 1, 2, -2, 3], 1),
    ([5, 5, 5, 5, 5], 10),
]
for nums, t in pair_cases:
    assert perf.count_pairs(nums, t) == ref_count_pairs(nums, t), (nums, t)

# dedupe_keep_order
dedupe_cases = [
    [],
    [1],
    [1, 1, 1],
    [3, 1, 3, 2, 1],
    ["a", "b", "a", "c", "b"],
    [0, -0, False],          # 0, -0, False are equal keys -> first kept
    [(1, 2), (1, 2), (3,)],
]
for items in dedupe_cases:
    assert perf.dedupe_keep_order(items) == ref_dedupe_keep_order(items), items

print("All correctness checks passed.")

# ---- Timing budgets ----
import random
random.seed(42)

big_a = [random.randint(0, 500000) for _ in range(200000)]
big_b = [random.randint(0, 500000) for _ in range(200000)]

big_nums = [random.randint(-1000, 1000) for _ in range(100000)]
target = random.randint(-1000, 1000)

big_items = [random.randint(0, 100000) for _ in range(200000)]

def bench(label, fn, budget=2.0):
    t0 = time.perf_counter()
    fn()
    dt = time.perf_counter() - t0
    status = "OK" if dt < budget else "FAIL"
    print(f"{label}: {dt:.4f}s  [{status}]")
    assert dt < budget, label

bench("common_elements(200k, 200k)", lambda: perf.common_elements(big_a, big_b))
bench("fib(300)", lambda: perf.fib(300))
bench("count_pairs(100k)", lambda: perf.count_pairs(big_nums, target))
bench("dedupe_keep_order(200k)", lambda: perf.dedupe_keep_order(big_items))

print("All timing budgets met.")
