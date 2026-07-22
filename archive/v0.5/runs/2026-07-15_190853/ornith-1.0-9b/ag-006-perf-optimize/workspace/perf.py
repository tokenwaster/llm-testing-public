"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    return sorted(set(a) & set(b))


def fib(n):
    """nth Fibonacci number (iterative)."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    from collections import Counter
    freq = Counter(nums)
    total = 0
    for x in freq:
        y = target - x
        if y < x:
            continue
        if y == x:
            n = freq[x]
            total += n * (n - 1) // 2
        else:
            total += freq[x] * freq[y]
    return total


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
