"""Efficient data helpers."""


def common_elements(a, b):
    """Return a sorted list of the distinct values present in both lists."""
    # Hash-based intersection avoids repeatedly scanning either input.
    try:
        return sorted(set(a).intersection(b))
    except TypeError:
        # Retain the original behavior for uncommon unhashable values.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """Return the nth Fibonacci number (with fib(0) == 0)."""
    if n < 2:
        return n

    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def count_pairs(nums, target):
    """Return the number of index pairs whose values sum to *target*."""
    count = 0
    seen = {}
    for value in nums:
        # Every earlier complement forms exactly one index pair with value.
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates while preserving first-seen order."""
    out = []
    seen = set()
    unhashable = []

    for item in items:
        try:
            if item in seen:
                continue
            seen.add(item)
        except TypeError:
            # Lists and other unhashable values still receive the behavior of
            # the original implementation without slowing the common case.
            if item in out:
                continue
            unhashable.append(item)
        out.append(item)

    return out
