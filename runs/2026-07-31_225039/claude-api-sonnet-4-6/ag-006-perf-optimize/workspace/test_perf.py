import time
import random
from perf import common_elements, fib, count_pairs, dedupe_keep_order

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

def check(label, got, expected, elapsed, budget):
    ok_val  = got == expected
    ok_time = elapsed < budget
    status  = PASS if (ok_val and ok_time) else FAIL
    print(f"[{status}] {label}")
    if not ok_val:
        print(f"       expected: {expected!r}")
        print(f"       got:      {got!r}")
    print(f"       time: {elapsed:.4f}s  (budget: {budget}s)")


# ── correctness fixtures ────────────────────────────────────────────────────

# common_elements
assert common_elements([3,1,2], [2,4,1]) == [1, 2]
assert common_elements([1,1,2], [1,2,2]) == [1, 2]
assert common_elements([], [1])          == []

# fib
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(20) == 6765

# count_pairs — small known cases
assert count_pairs([1,2,3,4], 5) == 2          # (1,4) and (2,3)
assert count_pairs([1,1,1], 2)   == 3          # all three pairs
assert count_pairs([0,0,0,0], 0) == 6          # C(4,2)

# count_pairs reference using frequency map (O(n)) — correct by construction
def count_pairs_ref(nums, target):
    """O(n) reference implementation using frequency counting."""
    from collections import Counter
    freq = Counter(nums)
    count = 0
    seen_keys = set()
    for x in freq:
        comp = target - x
        if comp in freq:
            if x == comp:
                n = freq[x]
                count += n * (n - 1) // 2
            elif comp not in seen_keys:
                count += freq[x] * freq[comp]
        seen_keys.add(x)
    return count

# dedupe_keep_order
assert dedupe_keep_order([1,2,1,3,2]) == [1, 2, 3]
assert dedupe_keep_order([])          == []

print("All correctness checks passed.\n")

# ── timing benchmarks ───────────────────────────────────────────────────────

random.seed(42)

# common_elements — 200 000-element lists
a = [random.randint(0, 300_000) for _ in range(200_000)]
b = [random.randint(0, 300_000) for _ in range(200_000)]
expected_ce = sorted(set(a) & set(b))

t0 = time.perf_counter()
result_ce = common_elements(a, b)
elapsed_ce = time.perf_counter() - t0
check("common_elements (200k each)", result_ce, expected_ce, elapsed_ce, 2.0)

# fib(300)
import sys; sys.setrecursionlimit(10_000)
expected_fib = 222232244629420445529739893461909967206666939096499764990979600

t0 = time.perf_counter()
result_fib = fib(300)
elapsed_fib = time.perf_counter() - t0
check("fib(300)", result_fib, expected_fib, elapsed_fib, 2.0)

# count_pairs — 100 000 elements
nums = [random.randint(0, 1000) for _ in range(100_000)]
target = 1000
expected_cp = count_pairs_ref(nums, target)   # fast O(n) reference

t0 = time.perf_counter()
result_cp = count_pairs(nums, target)
elapsed_cp = time.perf_counter() - t0
check("count_pairs (100k)", result_cp, expected_cp, elapsed_cp, 2.0)

# dedupe_keep_order — 200 000 items
items = [random.randint(0, 100_000) for _ in range(200_000)]
expected_dd = list(dict.fromkeys(items))

t0 = time.perf_counter()
result_dd = dedupe_keep_order(items)
elapsed_dd = time.perf_counter() - t0
check("dedupe_keep_order (200k)", result_dd, expected_dd, elapsed_dd, 2.0)
