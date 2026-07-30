"""Data helpers. Correct, but painfully slow on production-sized inputs."""

from collections import Counter


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    b_set = set(b)
    return sorted(set(x for x in a if x in b_set))


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
    count = 0
    freq = Counter(nums)
    for num in freq:
        complement = target - num
        if complement == num:
            count += freq[num] * (freq[num] - 1) // 2
        elif complement > num and complement in freq:
            count += freq[num] * freq[complement]
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
