"""Correctness + timing checks: optimized perf.py vs. the original logic."""
import random
import time

import perf


# ---------------- original (slow but known-correct) implementations ----------
def common_elements_ref(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def fib_ref(n):
    if n < 2:
        return n
    return fib_ref(n - 1) + fib_ref(n - 2)


def count_pairs_ref(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def dedupe_keep_order_ref(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


# ------------------------------- correctness --------------------------------
rng = random.Random(1234)
fails = 0


def check(name, got, want):
    global fails
    if got != want:
        fails += 1
        print(f"FAIL {name}: got {got!r} want {want!r}")


# fib: small values against the reference, plus known big values
for n in range(0, 26):
    check(f"fib({n})", perf.fib(n), fib_ref(n))
known = {30: 832040, 50: 12586269025, 90: 2880067194370816120,
         300: 222232244629420445529739893461909967206666939096499764990979600}
for n, want in known.items():
    check(f"fib({n})", perf.fib(n), want)
check("fib(-3)", perf.fib(-3), fib_ref(-3))
check("fib(-1)", perf.fib(-1), fib_ref(-1))

# randomized cross-checks on the three list functions
for trial in range(300):
    n = rng.randint(0, 60)
    a = [rng.randint(-8, 12) for _ in range(n)]
    b = [rng.randint(-8, 12) for _ in range(n)]
    check("common_elements", perf.common_elements(a, b), common_elements_ref(a, b))
    check("count_pairs", perf.count_pairs(a, 7), count_pairs_ref(a, 7))
    check("dedupe", perf.dedupe_keep_order(a), dedupe_keep_order_ref(a))

# edge cases
check("common empty", perf.common_elements([], [1, 2]), [])
check("common no overlap", perf.common_elements([1, 2], [3]), [])
check("common dupes", perf.common_elements([3, 1, 3, 2], [3, 3, 2]), [2, 3])
check("common strings", perf.common_elements(["b", "a", "b"], ["a", "c"]), ["a"])
check("pairs empty", perf.count_pairs([], 5), 0)
check("pairs single", perf.count_pairs([5], 10), 0)
check("pairs dupes", perf.count_pairs([1, 1, 1], 2), 3)
check("pairs neg", perf.count_pairs([-1, 5, 6, -6], 0), 1)
check("dedupe empty", perf.dedupe_keep_order([]), [])
check("dedupe order", perf.dedupe_keep_order([3, 1, 3, 2, 1]), [3, 1, 2])
check("dedupe mixed", perf.dedupe_keep_order(["a", 1, "a", 1.0]), ["a", 1])

# unhashable fallback paths still work
check("common unhashable", perf.common_elements([[1], [2], [1]], [[1]]), [[1]])
check("dedupe unhashable", perf.dedupe_keep_order([[1], [2], [1]]), [[1], [2]])

print("correctness:", "ALL PASS" if fails == 0 else f"{fails} FAILURES")


# --------------------------------- timing -----------------------------------
def timeit(label, fn, budget):
    t0 = time.perf_counter()
    result = fn()
    dt = time.perf_counter() - t0
    status = "OK " if dt < budget else "SLOW"
    print(f"{status} {label}: {dt:.4f}s (budget {budget}s)")
    return result


big_a = [rng.randint(0, 400_000) for _ in range(200_000)]
big_b = [rng.randint(0, 400_000) for _ in range(200_000)]
timeit("common_elements 200k", lambda: perf.common_elements(big_a, big_b), 2.0)
timeit("fib(300)", lambda: perf.fib(300), 2.0)

nums = [rng.randint(0, 50_000) for _ in range(100_000)]
timeit("count_pairs 100k", lambda: perf.count_pairs(nums, 50_000), 2.0)

items = [rng.randint(0, 300_000) for _ in range(200_000)]
timeit("dedupe_keep_order 200k", lambda: perf.dedupe_keep_order(items), 2.0)

# sanity: big-input results match the reference too (smaller sizes for the O(n^2) ref)
sa = [rng.randint(0, 300) for _ in range(1500)]
sb = [rng.randint(0, 300) for _ in range(1500)]
check("common big-ish", perf.common_elements(sa, sb), common_elements_ref(sa, sb))
check("pairs big-ish", perf.count_pairs(sa, 300), count_pairs_ref(sa, 300))
check("dedupe big-ish", perf.dedupe_keep_order(sa), dedupe_keep_order_ref(sa))
print("final:", "ALL PASS" if fails == 0 else f"{fails} FAILURES")
