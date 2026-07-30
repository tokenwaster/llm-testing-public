from collections import defaultdict
import perf

def orig_common_elements(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)

def orig_fib(n):
    if n < 2:
        return n
    return orig_fib(n - 1) + orig_fib(n - 2)

def orig_count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count

def orig_dedupe_keep_order(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


# Proposed implementations
def common_elements(a, b):
    return sorted(set(a) & set(b))

def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def count_pairs(nums, target):
    freq = defaultdict(int)
    count = 0
    for x in nums:
        count += freq[target - x]
        freq[x] += 1
    return count

def dedupe_keep_order(items):
    return list(dict.fromkeys(items))


# Tests
test_cases_common = [
    ([], []),
    ([1, 2, 3], []),
    ([], [1, 2, 3]),
    ([1, 2, 2, 3], [2, 3, 3, 4]),
    (["a", "b", "c"], ["b", "c", "d"]),
    ([-5, 0, 5], [5, -5]),
]

for a, b in test_cases_common:
    assert orig_common_elements(a, b) == common_elements(a, b), f"Failed on common_elements({a}, {b})"

for n in range(-5, 25):
    assert orig_fib(n) == fib(n), f"Failed on fib({n})"

test_cases_pairs = [
    ([], 5),
    ([1], 1),
    ([1, 1], 2),
    ([1, 2, 3, 4, 5], 5),
    ([1, 2, 3, 4, 3, 2, 1], 5),
    ([-2, -1, 0, 1, 2], 0),
    ([0, 0, 0, 0], 0),
]

for nums, target in test_cases_pairs:
    assert orig_count_pairs(nums, target) == count_pairs(nums, target), f"Failed on count_pairs({nums}, {target})"

test_cases_dedupe = [
    [],
    [1],
    [1, 1, 1],
    [3, 1, 2, 3, 1, 4],
    ["a", "b", "a", "c"],
]

for items in test_cases_dedupe:
    assert orig_dedupe_keep_order(items) == dedupe_keep_order(items), f"Failed on dedupe_keep_order({items})"

print("All edge case tests passed!")
