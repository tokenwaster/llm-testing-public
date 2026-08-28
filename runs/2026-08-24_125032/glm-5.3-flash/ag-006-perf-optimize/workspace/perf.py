"""Optimized versions of the perf module functions.

Same names, signatures and results as the original (correct but slow)
implementations -- only the algorithms changed.
"""

from collections import Counter


def common_elements(a, b):
    """Sorted list of values appearing in both lists."""
    try:
        # O(len(a) + len(b)) via hash sets.
        return sorted(set(a) & set(b))
    except TypeError:
        # Unhashable elements: fall back to the original O(n*m) logic,
        # which is still correct (just slower).
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """nth Fibonacci number (fib(0)=0, fib(1)=1), iteratively."""
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i]+nums[j] == target."""
    seen = Counter()
    count = 0
    for x in nums:
        # Every previously-seen occurrence of the complement forms a
        # valid pair (i, j) with i < j.
        count += seen[target - x]
        seen[x] += 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    try:
        seen = set()
        out = []
        append = out.append
        add = seen.add
        for x in items:
            if x not in seen:
                add(x)
                append(x)
        return out
    except TypeError:
        # Unhashable elements: fall back to the original linear-scan logic.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
