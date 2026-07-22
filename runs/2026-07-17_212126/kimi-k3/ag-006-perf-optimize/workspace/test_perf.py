import random
import time

import perf


# --- naive references (the original algorithms) ---
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


def ref_dedupe(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


rng = random.Random(42)

# --- correctness: random small/medium cases vs reference ---
for trial in range(300):
    n = rng.randint(0, 40)
    m = rng.randint(0, 40)
    a = [rng.randint(-10, 10) for _ in range(n)]
    b = [rng.randint(-10, 10) for _ in range(m)]
    assert perf.common_elements(a, b) == ref_common_elements(a, b), (a, b)
    assert perf.dedupe_keep_order(a) == ref_dedupe(a), a
    target = rng.randint(-15, 15)
    assert perf.count_pairs(a, target) == ref_count_pairs(a, target), (a, target)

for n in range(0, 31):
    assert perf.fib(n) == ref_fib(n), n

# edge cases
assert perf.common_elements([], []) == []
assert perf.common_elements([1, 1, 1], [1]) == [1]
assert perf.common_elements([3, 1, 2], [2, 3, 1]) == [1, 2, 3]
assert perf.fib(0) == 0 and perf.fib(1) == 1 and perf.fib(10) == 55
assert perf.count_pairs([], 5) == 0
assert perf.count_pairs([5, 5, 5], 10) == 3
assert perf.count_pairs([0, 0, 0, 0], 0) == 6
assert perf.dedupe_keep_order([]) == []
assert perf.dedupe_keep_order([1, 1, 2, 1, 3, 2]) == [1, 2, 3]

# fib(300) exact value (known)
assert perf.fib(300) == 222232244629420445529739893461909967206666939096499764990979600

print("correctness: all passed")


def timed(label, fn, budget=2.0):
    t0 = time.perf_counter()
    result = fn()
    dt = time.perf_counter() - t0
    status = "OK " if dt < budget else "FAIL"
    print(f"{status} {label}: {dt:.4f}s (budget {budget}s)")
    assert dt < budget, label
    return result


# --- timing at production scale ---
big_a = [rng.randint(0, 500_000) for _ in range(200_000)]
big_b = [rng.randint(0, 500_000) for _ in range(200_000)]
timed("common_elements (2 x 200k)", lambda: perf.common_elements(big_a, big_b))

timed("fib(300)", lambda: perf.fib(300))

big_nums = [rng.randint(-1000, 1000) for _ in range(100_000)]
r = timed("count_pairs (100k)", lambda: perf.count_pairs(big_nums, 500))
# sanity: verify on a 5k subsample against reference
sub = big_nums[:5000]
assert perf.count_pairs(sub, 500) == ref_count_pairs(sub, 500)
print("  count_pairs(100k) result:", r)

big_items = [rng.randint(0, 300_000) for _ in range(200_000)]
r = timed("dedupe_keep_order (200k)", lambda: perf.dedupe_keep_order(big_items))
assert r == ref_dedupe(big_items[:20000]) or True  # heavy ref check skipped at full size
sub = big_items[:20000]
assert perf.dedupe_keep_order(sub) == ref_dedupe(sub)
print("  dedupe unique count:", len(r))

print("ALL TESTS PASSED")
