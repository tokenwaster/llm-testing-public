"""Verify optimized perf.py matches original semantics and meets timing budgets."""

import random
import time
from collections import Counter

import perf


# --- Original (slow but correct) reference implementations -----------------

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


# --- Correctness checks -----------------------------------------------------

rng = random.Random(12345)
failures = []

def check(name, got, want):
    ok = got == want
    print(f"{name}: {'OK' if ok else 'FAIL'}")
    if not ok:
        failures.append(name)

# common_elements: random lists with overlaps, duplicates, negatives
for trial in range(20):
    a = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
    b = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
    check(f"common_elements trial {trial}",
          perf.common_elements(a, b), ref_common_elements(a, b))

check("common_elements empty", perf.common_elements([], [1, 2]), [])
check("common_elements strings",
      perf.common_elements(["b", "a", "b"], ["a", "b", "c"]), ["a", "b"])

# fib: small values vs recursive reference
for n in range(25):
    check(f"fib({n})", perf.fib(n), ref_fib(n))
check("fib(0)", perf.fib(0), 0)
check("fib(1)", perf.fib(1), 1)

# fib(300) exact known value
FIB300 = 222232244629420445529739893461909967206666939096499764990979600
check("fib(300) exact", perf.fib(300), FIB300)

# count_pairs: brute force comparison on random data
for trial in range(15):
    nums = [rng.randint(-8, 8) for _ in range(rng.randint(0, 40))]
    target = rng.randint(-10, 10)
    check(f"count_pairs trial {trial} (t={target})",
          perf.count_pairs(nums, target), ref_count_pairs(nums, target))
check("count_pairs empty", perf.count_pairs([], 5), 0)

# dedupe_keep_order: mixed types incl. unhashables
data = [3, 1, 3, 2, 1, "a", "a", None, None, True, 2.0, (1, 2), (1, 2)]
check("dedupe mixed", perf.dedupe_keep_order(data),
      ref_dedupe_keep_order(data))
unhashable = [[1], [2], [1], [], []]
check("dedupe unhashable", perf.dedupe_keep_order(unhashable),
      ref_dedupe_keep_order(unhashable))
check("dedupe bool/int edge", perf.dedupe_keep_order([True, 1, 0, False]),
      ref_dedupe_keep_order([True, 1, 0, False]))
check("dedupe empty", perf.dedupe_keep_order([]), [])

print()
if failures:
    print(f"CORRECTNESS FAILURES: {len(failures)} -> {failures}")
else:
    print("All correctness checks passed.")

# --- Timing budgets ---------------------------------------------------------

def timed(label, fn, budget):
    t0 = time.perf_counter()
    result = fn()
    dt = time.perf_counter() - t0
    status = "OK" if dt < budget else "TOO SLOW"
    print(f"{label}: {dt:.4f}s (budget {budget}s) {status}")
    return result

print()
list_a = [rng.randint(0, 10**6) for _ in range(200_000)]
list_b = [rng.randint(0, 10**6) for _ in range(200_000)]
r1 = timed("common_elements 200k x 200k",
           lambda: perf.common_elements(list_a, list_b), 2.0)
r2 = timed("fib(300)", lambda: perf.fib(300), 2.0)
nums = [rng.randint(0, 100) for _ in range(100_000)]
r3 = timed("count_pairs 100k", lambda: perf.count_pairs(nums, 150), 2.0)
items = [rng.randint(0, 50_000) for _ in range(200_000)]
r4 = timed("dedupe_keep_order 200k",
           lambda: perf.dedupe_keep_order(items), 2.0)

# --- Sanity assertions on big-input results ---------------------------------

assert r2 == FIB300

# Independent O(n) cross-check for count_pairs via Counter
c = Counter(nums)
expected_r3 = 0
for v, cnt in c.items():
    comp = 150 - v
    if comp == v:
        expected_r3 += cnt * (cnt - 1) // 2
    elif comp > v and comp in c:
        expected_r3 += cnt * c[comp]
assert r3 == expected_r3, f"count_pairs mismatch: {r3} != {expected_r3}"

assert len(r4) == len(set(items))

# common_elements result matches set intersection
assert r1 == sorted(set(list_a) & set(list_b))

print("\nBig-input sanity assertions passed.")
