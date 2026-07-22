"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    sa = set(a)
    sb = set(b) if not isinstance(b, (set, frozenset)) else b
    return sorted(sa & sb)


def fib(n):
    """nth Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    from collections import Counter
    freq = Counter()
    count = 0
    for x in nums:
        complement = target - x
        if complement in freq:
            count += freq[complement]
        freq[x] += 1
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
