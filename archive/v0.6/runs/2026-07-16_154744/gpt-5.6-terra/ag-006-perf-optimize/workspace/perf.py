"""Efficient data helpers."""


def common_elements(a, b):
    """Return the sorted, unique values that occur in both lists."""
    try:
        return sorted(set(a).intersection(b))
    except TypeError:
        # Retain the original list-membership semantics for unhashable input.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """Return the nth Fibonacci number."""
    # This also preserves the prior behaviour for negative values.
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def count_pairs(nums, target):
    """Count index pairs whose values sum to ``target``."""
    # Each earlier occurrence of target - value forms a pair with value.
    seen = {}
    count = 0
    for value in nums:
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates while retaining each value's first occurrence."""
    seen = set()
    out = []
    iterator = iter(items)
    for value in iterator:
        try:
            is_new = value not in seen
        except TypeError:
            # Values seen so far are already represented in out.  Once an
            # unhashable value occurs, use the original general list logic
            # for it and the remaining values.
            if value not in out:
                out.append(value)
            for remaining in iterator:
                if remaining not in out:
                    out.append(remaining)
            return out
        if is_new:
            seen.add(value)
            out.append(value)
    return out
