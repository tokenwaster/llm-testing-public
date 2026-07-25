import random
import time

from perf import common_elements, fib, count_pairs, dedupe_keep_order


# --- Reference implementations (the original slow ones) ---
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


# --- Correctness on small/edge cases ---
assert common_elements([], []) == []
assert common_elements([1, 2], [3]) == []
assert common_elements([3, 1, 2, 3, 1], [2, 3, 3]) == [2, 3]
assert common_elements([5], [5]) == [5]
assert common_elements([-1, 0, -1], [0, -1]) == [-1, 0]

rng = random.Random(0)
for trial in range(50):
    a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
    b = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
    assert common_elements(a, b) == ref_common_elements(a, b), (a, b)

for n in range(0, 25):
    assert fib(n) == ref_fib(n), n
assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600
assert fib(0) == 0 and fib(1) == 1

assert count_pairs([], 5) == 0
assert count_pairs([5], 5) == 0
assert count_pairs([1, 4, 1, 4], 5) == 4
assert count_pairs([2, 2, 2], 4) == 3
assert count_pairs([0, 0], 0) == 1
for trial in range(50):
    nums = [rng.randint(-10, 10) for _ in range(rng.randint(0, 40))]
    target = rng.randint(-15, 15)
    assert count_pairs(nums, target) == ref_count_pairs(nums, target)

assert dedupe_keep_order([]) == []
assert dedupe_keep_order([1, 1, 1]) == [1]
assert dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2]
for trial in range(50):
    items = [rng.randint(0, 10) for _ in range(rng.randint(0, 50))]
    assert dedupe_keep_order(items) == ref_dedupe(items)

print("Correctness: all passed")

# --- Timing budgets ---
def time_it(fn, *args):
    t0 = time.perf_counter()
    result = fn(*args)
    return time.perf_counter() - t0, result


big_a = [rng.randint(0, 500_000) for _ in range(200_000)]
big_b = [rng.randint(0, 500_000) for _ in range(200_000)]
t, r = time_it(common_elements, big_a, big_b)
print(f"common_elements(200k x 200k): {t:.3f}s  (budget 2s), {len(r)} common")
assert t < 2.0
assert sorted(set(big_a) & set(big_b)) == r

t, r = time_it(fib, 300)
print(f"fib(300): {t:.6f}s  (budget 2s)")
assert t < 2.0

big_nums = [rng.randint(-1000, 1000) for _ in range(100_000)]
t, r = time_it(count_pairs, big_nums, 7)
print(f"count_pairs(100k): {t:.3f}s  (budget 2s), {r} pairs")
assert t < 2.0
# verify with the math: sum over complements
from collections import Counter
c = Counter(big_nums)
expected = sum(v * c[7 - k] for k, v in c.items() if k < 7 - k)
expected += sum(v * (v - 1) // 2 for k, v in c.items() if k == 7 - k)
assert r == expected, (r, expected)

big_items = [rng.randint(0, 300_000) for _ in range(200_000)]
t, r = time_it(dedupe_keep_order, big_items)
print(f"dedupe_keep_order(200k): {t:.3f}s  (budget 2s), {len(r)} unique")
assert t < 2.0
assert r == list(dict.fromkeys(big_items))

print("Timing: all within budget")
