"""Efficient data helpers."""


def common_elements(a, b):
    """Return a sorted list of the distinct values appearing in both inputs."""
    # Sets make membership and duplicate elimination constant-time on the
    # ordinary (hashable) values for which this helper is intended.
    try:
        in_b = set(b)
        seen = set()
        out = []
        for value in a:
            if value in in_b and value not in seen:
                seen.add(value)
                out.append(value)
        return sorted(out)
    except TypeError:
        # Retain the original function's useful behaviour for unhashable
        # values as well.
        out = []
        for value in a:
            if value in b and value not in out:
                out.append(value)
        return sorted(out)


def fib(n):
    """Return the nth Fibonacci number."""
    # This also preserves the previous behaviour for negative n.
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def count_pairs(nums, target):
    """Return the number of index pairs whose values sum to *target*."""
    # At each position, all earlier complements form valid pairs with it.
    seen = {}
    count = 0
    for value in nums:
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates while retaining each value's first occurrence."""
    try:
        seen = set()
        out = []
        for value in items:
            if value not in seen:
                seen.add(value)
                out.append(value)
        return out
    except TypeError:
        # A list fallback matches the original semantics for unhashable items.
        out = []
        for value in items:
            if value not in out:
                out.append(value)
        return out
