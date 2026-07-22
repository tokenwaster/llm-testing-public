"""Efficient data helpers."""


def common_elements(a, b):
    """Return a sorted list of the distinct values present in both lists."""
    try:
        values_in_b = set(b)
        seen = set()
        out = []
        for value in a:
            if value in values_in_b and value not in seen:
                seen.add(value)
                out.append(value)
        return sorted(out)
    except TypeError:
        # Retain the original behavior for unusual lists containing
        # unhashable values.
        out = []
        for value in a:
            if value in b and value not in out:
                out.append(value)
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
    """Return the number of index pairs whose values sum to target."""
    counts = {}
    pair_count = 0
    try:
        for value in nums:
            pair_count += counts.get(target - value, 0)
            counts[value] = counts.get(value, 0) + 1
        return pair_count
    except (TypeError, AttributeError):
        # Preserve support for values which can be added and compared but
        # cannot be hashed or subtracted.
        pair_count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    pair_count += 1
        return pair_count


def dedupe_keep_order(items):
    """Remove duplicate items while preserving their first-seen order."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        # Equality-based fallback for unhashable values.
        out = []
        for value in items:
            if value not in out:
                out.append(value)
        return out
