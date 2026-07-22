"""Reference optimized perf.py (v0.5 ag-006)."""


def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    from collections import Counter
    c = Counter(nums)
    total = 0
    for v, n in c.items():
        w = target - v
        if w == v:
            total += n * (n - 1) // 2
        elif w in c and w > v:
            total += n * c[w]
    return total


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
