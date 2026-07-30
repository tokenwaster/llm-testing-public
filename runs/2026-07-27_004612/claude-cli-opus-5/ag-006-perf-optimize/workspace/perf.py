"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    try:
        return sorted(set(a) & set(b))
    except TypeError:                       # unhashable values
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


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
    seen = {}
    count = 0
    for x in nums:
        count += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:                       # unhashable items
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
