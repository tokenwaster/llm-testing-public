"""Data helpers. Correct, but painfully slow on production-sized inputs."""

from collections import Counter


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    return sorted(set(a) & set(b))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    counts = Counter(nums)
    total = 0
    for value, c in counts.items():
        complement = target - value
        if complement == value:
            total += c * (c - 1)
        elif complement in counts:
            total += c * counts[complement]
    return total // 2


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
