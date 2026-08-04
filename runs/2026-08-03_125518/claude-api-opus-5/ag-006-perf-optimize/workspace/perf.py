"""Optimized implementations (same behavior, much faster algorithms)."""

from collections import Counter


def common_elements(a, b):
    """Sorted list of distinct values appearing in both lists."""
    try:
        return sorted(set(a) & set(b))
    except TypeError:
        # Fallback for unhashable elements: slow but still correct.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """nth Fibonacci number, iteratively (fib(0)=0, fib(1)=1)."""
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


def _count_pairs_bruteforce(nums, target):
    count = 0
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def count_pairs(nums, target):
    """Number of index pairs i < j with nums[i] + nums[j] == target."""
    try:
        counts = Counter(nums)
    except TypeError:
        return _count_pairs_bruteforce(nums, target)

    items = list(counts.items())
    position = {value: i for i, (value, _) in enumerate(items)}

    total = 0
    for i, (value, c) in enumerate(items):
        try:
            other = target - value
        except TypeError:
            return _count_pairs_bruteforce(nums, target)
        try:
            j = position[other]
        except (KeyError, TypeError):
            continue
        if j == i:
            total += c * (c - 1) // 2
        elif j > i:
            total += c * counts[other]
    return total


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
