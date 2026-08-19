import random
import time

import perf


# ---------- reference (original slow) implementations ----------
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


def check(name, got, expected):
    assert got == expected, f"{name}: got {got!r}, expected {expected!r}"
    print(f"  OK  {name}")


random.seed(42)

# ---------- correctness ----------
print("correctness:")

# common_elements: small cases vs reference
for trial in range(30):
    a = [random.randint(0, 20) for _ in range(random.randint(0, 60))]
    b = [random.randint(0, 20) for _ in range(random.randint(0, 60))]
    check(f"common_elements trial {trial}", perf.common_elements(a, b), ref_common_elements(a, b))

check("common_elements empty", perf.common_elements([], [1, 2]), [])
check("common_elements basic", perf.common_elements([3, 1, 2, 1], [2, 4, 3]), [2, 3])
check("common_elements strings", perf.common_elements(["b", "a", "b"], ["a", "c"]), ["a"])
check("common_elements negatives", perf.common_elements([-1, -2, 5], [-2, 7]), [-2])

# fib: exact known values
known = {0: 0, 1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 10: 55, 20: 6765, 30: 832040}
for n, v in known.items():
    check(f"fib({n})", perf.fib(n), v)
for n in range(25):
    check(f"fib({n}) vs ref", perf.fib(n), ref_fib(n))
# exact fib(300)
fib300 = 222232244629420445529739893461909967206666939096499764990979600
check("fib(300)", perf.fib(300), fib300)

# count_pairs: small cases vs reference
for trial in range(30):
    nums = [random.randint(-10, 10) for _ in range(random.randint(0, 40))]
    target = random.randint(-10, 10)
    check(f"count_pairs trial {trial}", perf.count_pairs(nums, target), ref_count_pairs(nums, target))

check("count_pairs basic", perf.count_pairs([1, 2, 3, 4, 5], 5), 2)
check("count_pairs dupes", perf.count_pairs([1, 1, 1, 1], 2), 6)
check("count_pairs none", perf.count_pairs([1, 2, 3], 100), 0)
check("count_pairs empty", perf.count_pairs([], 0), 0)
# pairs in [-1, 0, 1, 2, -1] summing to 0: (-1,1) at (0,2) and (1,-1) at (2,4)
check("count_pairs negatives", perf.count_pairs([-1, 0, 1, 2, -1], 0),
      ref_count_pairs([-1, 0, 1, 2, -1], 0))
check("count_pairs zeros", perf.count_pairs([0, 0, 0], 0), 3)
check("count_pairs floats", perf.count_pairs([1.5, 0.5, 2.5], 3.0), 1)

# dedupe_keep_order
check("dedupe basic", perf.dedupe_keep_order([3, 1, 3, 2, 1]), [3, 1, 2])
check("dedupe empty", perf.dedupe_keep_order([]), [])
check("dedupe strings", perf.dedupe_keep_order(["a", "b", "a"]), ["a", "b"])
for trial in range(30):
    items = [random.randint(0, 15) for _ in range(random.randint(0, 60))]
    check(f"dedupe trial {trial}", perf.dedupe_keep_order(items), ref_dedupe_keep_order(items))
# unhashable fallback still correct
check("dedupe unhashable", perf.dedupe_keep_order([[1], [2], [1]]), [[1], [2]])
check("common_elements unhashable", perf.common_elements([[1], [2]], [[2], [3]]), [[2]])

# ---------- timing ----------
print("\ntiming:")


def timed(name, fn, budget=2.0):
    t0 = time.perf_counter()
    result = fn()
    dt = time.perf_counter() - t0
    status = "PASS" if dt < budget else "FAIL"
    print(f"  {status}  {name}: {dt:.4f}s (budget {budget}s)")
    assert dt < budget, f"{name} over budget"
    return result


big1 = [random.randint(0, 1_000_000) for _ in range(200_000)]
big2 = [random.randint(0, 1_000_000) for _ in range(200_000)]
timed("common_elements 200k x 200k", lambda: perf.common_elements(big1, big2))

timed("fib(300)", lambda: perf.fib(300))

nums100k = [random.randint(0, 1000) for _ in range(100_000)]
timed("count_pairs 100k", lambda: perf.count_pairs(nums100k, 1000))

items200k = [random.randint(0, 50_000) for _ in range(200_000)]
timed("dedupe_keep_order 200k", lambda: perf.dedupe_keep_order(items200k))

print("\nAll checks passed.")
