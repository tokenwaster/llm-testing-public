import random
import time
from collections import Counter

import perf


def ref_common_elements(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
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
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


failures = []


def check(name, got, want):
    if got != want:
        failures.append(f"{name}: got {got!r} want {want!r}")


def check_same_exc(name, fn, ref, *args):
    try:
        got = fn(*args)
        got_exc = None
    except Exception as e:
        got, got_exc = None, type(e)
    try:
        want = ref(*args)
        want_exc = None
    except Exception as e:
        want, want_exc = None, type(e)
    if got_exc is not want_exc or (got_exc is None and got != want):
        failures.append(f"{name}: got {got!r}/{got_exc} want {want!r}/{want_exc}")


rng = random.Random(42)

# ------------------------------------------------------------------ fib
for n in list(range(0, 60)) + [64, 100, 250, 299, 300, 301, 1000, 5000]:
    check(f"fib({n})", perf.fib(n), ref_fib(n))

# ------------------------------------------------------- common_elements
for _ in range(300):
    a = [rng.randrange(-15, 15) for _ in range(rng.randrange(0, 25))]
    b = [rng.randrange(-15, 15) for _ in range(rng.randrange(0, 25))]
    check("common ints", perf.common_elements(a, b), ref_common_elements(a, b))
for _ in range(150):
    a = [rng.choice("abcxyz") for _ in range(rng.randrange(0, 20))]
    b = [rng.choice("abcqw") for _ in range(rng.randrange(0, 20))]
    check("common strs", perf.common_elements(a, b), ref_common_elements(a, b))
check("common empty", perf.common_elements([], []), [])
check_same_exc("common mixed", perf.common_elements, ref_common_elements,
               [1, 2.0, "a", None, True], [1.0, "a", None, 3])
check("common unhashable", perf.common_elements([[1], [2], [1]], [[1], [3]]),
      ref_common_elements([[1], [2], [1]], [[1], [3]]))
check("common floats", perf.common_elements([0.1, 0.2, 0.3], [0.3, 0.1]),
      ref_common_elements([0.1, 0.2, 0.3], [0.3, 0.1]))
check("common tuples", perf.common_elements([(1, 2), (1, 2)], [(1, 2)]),
      ref_common_elements([(1, 2), (1, 2)], [(1, 2)]))
check("common bool/int", perf.common_elements([True, False, 0, 1], [0, 1, 2]),
      ref_common_elements([True, False, 0, 1], [0, 1, 2]))

# ---------------------------------------------------------- count_pairs
for _ in range(400):
    n = rng.randrange(0, 30)
    nums = [rng.randrange(-8, 8) for _ in range(n)]
    target = rng.randrange(-10, 10)
    check("pairs ints", perf.count_pairs(nums, target), ref_count_pairs(nums, target))
for _ in range(150):
    n = rng.randrange(0, 20)
    nums = [rng.choice([0.5, 1.5, 2.5, -0.5]) for _ in range(n)]
    target = rng.choice([1.0, 2.0, 3.0, 4.0])
    check("pairs floats", perf.count_pairs(nums, target), ref_count_pairs(nums, target))
check("pairs empty", perf.count_pairs([], 5), 0)
check("pairs single", perf.count_pairs([5], 10), 0)
check("pairs all same", perf.count_pairs([7] * 60, 14), ref_count_pairs([7] * 60, 14))
check("pairs zeros", perf.count_pairs([0] * 40, 0), ref_count_pairs([0] * 40, 0))
check("pairs bool/int", perf.count_pairs([True, 1, 2, 1.0], 3),
      ref_count_pairs([True, 1, 2, 1.0], 3))
check("pairs float prec", perf.count_pairs([0.1, 0.2, 0.19999999999999998], 0.3),
      ref_count_pairs([0.1, 0.2, 0.19999999999999998], 0.3))
check("pairs nan", perf.count_pairs([float("nan"), 1.0, 2.0], float("nan")),
      ref_count_pairs([float("nan"), 1.0, 2.0], float("nan")))
check("pairs unhashable", perf.count_pairs([[1], [2], [3]], 1),
      ref_count_pairs([[1], [2], [3]], 1))
check("pairs negative", perf.count_pairs([-5, -4, -1, 6, 11], -5),
      ref_count_pairs([-5, -4, -1, 6, 11], -5))
check("pairs big ints", perf.count_pairs([10**20, 5, -(10**20) + 5], 5),
      ref_count_pairs([10**20, 5, -(10**20) + 5], 5))
check("pairs strings", perf.count_pairs(["a", "b", "ab"], "ab"),
      ref_count_pairs(["a", "b", "ab"], "ab"))

# ---------------------------------------------------- dedupe_keep_order
for _ in range(300):
    items = [rng.randrange(-10, 10) for _ in range(rng.randrange(0, 30))]
    check("dedupe ints", perf.dedupe_keep_order(items), ref_dedupe_keep_order(items))
for _ in range(150):
    items = [rng.choice(["x", "y", None, 1.5, True]) for _ in range(20)]
    check("dedupe mixed", perf.dedupe_keep_order(items), ref_dedupe_keep_order(items))
check("dedupe empty", perf.dedupe_keep_order([]), [])
check("dedupe unhashable", perf.dedupe_keep_order([[1], [2], [1], [3], [2]]),
      ref_dedupe_keep_order([[1], [2], [1], [3], [2]]))
check("dedupe str", perf.dedupe_keep_order("abca"), ref_dedupe_keep_order("abca"))
check("dedupe all same", perf.dedupe_keep_order([9] * 1000),
      ref_dedupe_keep_order([9] * 1000))
check("dedupe bool/int", perf.dedupe_keep_order([True, 1, 0, False, 1.0]),
      ref_dedupe_keep_order([True, 1, 0, False, 1.0]))

# ------------------------------------------------------------- timing
budget = 2.0
results = []

big_a = [rng.randrange(0, 500000) for _ in range(200000)]
big_b = [rng.randrange(0, 500000) for _ in range(200000)]
t = time.perf_counter()
r1 = perf.common_elements(big_a, big_b)
dt = time.perf_counter() - t
exp1 = sorted(set(big_a) & set(big_b))
results.append(("common_elements 200k", dt, r1 == exp1))

t = time.perf_counter()
r2 = perf.fib(300)
dt = time.perf_counter() - t
results.append(("fib(300)", dt, r2 == ref_fib(300)))

big_nums = [rng.randrange(0, 1000) for _ in range(100000)]
target = 999
t = time.perf_counter()
r3 = perf.count_pairs(big_nums, target)
dt = time.perf_counter() - t
cnt = Counter(big_nums)
exp3 = sum(v * (cnt.get(target - k, 0) if k != target - k else v - 1)
           for k, v in cnt.items()) // 2
# second independent method: streaming prefix counts
seen, exp3b = {}, 0
for x in big_nums:
    exp3b += seen.get(target - x, 0)
    seen[x] = seen.get(x, 0) + 1
results.append(("count_pairs 100k", dt, r3 == exp3 == exp3b))

big_items = [rng.randrange(0, 50000) for _ in range(200000)]
t = time.perf_counter()
r4 = perf.dedupe_keep_order(big_items)
dt = time.perf_counter() - t
seen, exp4 = set(), []
for x in big_items:
    if x not in seen:
        seen.add(x)
        exp4.append(x)
results.append(("dedupe 200k", dt, r4 == exp4))

t = time.perf_counter()
r5 = perf.common_elements(list(range(200000)), list(range(100000, 400000)))
results.append(("common 200k dense", time.perf_counter() - t,
                r5 == list(range(100000, 200000))))

t = time.perf_counter()
v = perf.count_pairs([5] * 100000, 10)
results.append(("pairs 100k all-same", time.perf_counter() - t,
                v == 100000 * 99999 // 2))

t = time.perf_counter()
r7 = perf.dedupe_keep_order(list(range(200000)))
results.append(("dedupe 200k all-unique", time.perf_counter() - t,
                r7 == list(range(200000))))

t = time.perf_counter()
perf.fib(100000)
results.append(("fib(100000) stress", time.perf_counter() - t, True))

ok = True
for name, dt, good in results:
    status = "PASS" if (dt < budget and good) else "FAIL"
    if status == "FAIL":
        ok = False
    print(f"  {status}  {name:24s} {dt:.4f}s  correct={good}")

print()
if failures:
    print(f"CORRECTNESS FAILURES: {len(failures)}")
    for f in failures[:20]:
        print("   ", f)
elif ok:
    print("ALL CORRECTNESS AND TIMING CHECKS PASSED")
else:
    print("TIMING FAILURE")
