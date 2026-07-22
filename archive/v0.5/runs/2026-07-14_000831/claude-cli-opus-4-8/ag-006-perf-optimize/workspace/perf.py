"""Data helpers. Correct and fast on production-sized inputs."""

from collections import Counter


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    return sorted(set(a) & set(b))        # O(n+m) via hash sets


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(2, n + 1):             # O(n) iterative
        prev, cur = cur, prev + cur
    return cur


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    count = 0
    seen = Counter()
    for x in nums:                        # O(n) single pass
        count += seen[target - x]
        seen[x] += 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    return list(dict.fromkeys(items))     # O(n) ordered dedupe
