import random
import time

import perf


def ref_common(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def ref_fib(n, _memo={0: 0, 1: 1}):
    if n in _memo:
        return _memo[n]
    r = ref_fib(n - 1) + ref_fib(n - 2)
    _memo[n] = r
    return r


def ref_pairs(nums, target):
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


random.seed(0)

# correctness on small random inputs
for trial in range(200):
    a = [random.randint(-10, 10) for _ in range(random.randint(0, 30))]
    b = [random.randint(-10, 10) for _ in range(random.randint(0, 30))]
    assert perf.common_elements(a, b) == ref_common(a, b), (a, b)
    t = random.randint(-20, 20)
    assert perf.count_pairs(a, t) == ref_pairs(a, t), (a, t)
    assert perf.dedupe_keep_order(a) == ref_dedupe(a)

# strings / mixed hashables
s = ["a", "b", "a", "c", "b"]
assert perf.common_elements(s, ["b", "c", "z"]) == ["b", "c"]
assert perf.dedupe_keep_order(s) == ["a", "b", "a", "c", "b"][:0] + ref_dedupe(s)

# unhashable fallback
la = [[1], [2], [1]]
assert perf.dedupe_keep_order(la) == [[1], [2]]
assert perf.common_elements(la, [[2], [3]]) == [[2]]

for n in range(0, 40):
    assert perf.fib(n) == ref_fib(n), n
assert perf.fib(300) == ref_fib(300)
assert perf.fib(0) == 0 and perf.fib(1) == 1

# timings
N = 200000
a = [random.randint(0, 500000) for _ in range(N)]
b = [random.randint(0, 500000) for _ in range(N)]
t0 = time.perf_counter()
r = perf.common_elements(a, b)
t1 = time.perf_counter()
print(f"common_elements: {t1-t0:.4f}s (len={len(r)})")
assert t1 - t0 < 2

t0 = time.perf_counter()
f = perf.fib(300)
t1 = time.perf_counter()
print(f"fib(300): {t1-t0:.6f}s -> {f}")
assert t1 - t0 < 2
assert f == 222232244629420445529739893461909967206666939096499764990979600

nums = [random.randint(0, 1000) for _ in range(100000)]
t0 = time.perf_counter()
c = perf.count_pairs(nums, 1000)
t1 = time.perf_counter()
print(f"count_pairs: {t1-t0:.4f}s (count={c})")
assert t1 - t0 < 2

items = [random.randint(0, 100000) for _ in range(200000)]
t0 = time.perf_counter()
d = perf.dedupe_keep_order(items)
t1 = time.perf_counter()
print(f"dedupe_keep_order: {t1-t0:.4f}s (len={len(d)})")
assert t1 - t0 < 2

print("ALL OK")
