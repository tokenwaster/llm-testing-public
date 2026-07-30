"""Efficient implementations of a few small collection utilities."""


def common_elements(a, b):
    """Return the distinct values shared by *a* and *b*, in sorted order."""
    # Keep the values from ``a`` (rather than from a set intersection), which
    # also preserves the behaviour for equal, but non-identical, objects.
    try:
        in_b = set(b)
        seen = set()
        out = []
        for value in a:
            if value in in_b and value not in seen:
                seen.add(value)
                out.append(value)
    except TypeError:
        # The original functions also work for unhashable values.  Such input
        # cannot use a set, so retain that behaviour as a compatibility path.
        out = []
        for value in a:
            if value in b and value not in out:
                out.append(value)
    return sorted(out)


def fib(n):
    """Return the nth Fibonacci number."""
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def count_pairs(nums, target):
    """Count index pairs whose values add up to ``target``."""
    seen = {}
    count = 0
    try:
        for value in nums:
            count += seen.get(target - value, 0)
            seen[value] = seen.get(value, 0) + 1
    except TypeError:
        # Compatibility for unhashable numeric-like objects.
        count = 0
        for i, left in enumerate(nums):
            for right in nums[i + 1:]:
                if left + right == target:
                    count += 1
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
        # Match the old equality-based implementation for unhashable values.
        out = []
        for value in items:
            if value not in out:
                out.append(value)
        return out
