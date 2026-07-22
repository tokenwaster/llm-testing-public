"""Data helpers. Optimized for production-sized inputs."""

from collections import Counter


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
    freq = Counter(nums)
    total = 0
    for num, c in freq.items():
        complement = target - num
        if complement > num:
            total += c * freq[complement]
        elif complement == num and c >= 2:
            total += c * (c - 1) // 2
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
