from collections import Counter


def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    if n < 2:
        return n
    x, y = 0, 1
    for _ in range(n - 1):
        x, y = y, x + y
    return y


def count_pairs(nums, target):
    seen = Counter()
    count = 0
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
