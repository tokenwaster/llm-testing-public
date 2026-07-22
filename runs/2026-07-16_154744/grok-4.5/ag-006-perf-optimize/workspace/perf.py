"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    return sorted(set(a) & set(b))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    from collections import Counter
    counts = Counter(nums)
    count = 0
    seen = set()
    for x in counts:
        y = target - x
        if y in counts and y not in seen:
            if x == y:
                c = counts[x]
                count += c * (c - 1) // 2
            else:
                count += counts[x] * counts[y]
            seen.add(x)
            seen.add(y)
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
