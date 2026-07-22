"""Reference optimized implementations (all within the 2s budget)."""
from collections import Counter


def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    c = Counter(nums)
    count = 0
    for v, n in c.items():
        w = target - v
        if w == v:
            count += n * (n - 1) // 2
        elif w in c and w > v:
            count += n * c[w]
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
