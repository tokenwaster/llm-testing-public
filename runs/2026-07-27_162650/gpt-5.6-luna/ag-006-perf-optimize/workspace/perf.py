"""Small collection of performance-sensitive helpers."""


def common_elements(a, b):
    """Return the distinct values shared by *a* and *b*, in sorted order."""
    # Membership in a set makes both the lookup and the de-duplication
    # constant-time on the (normal) hashable input types.
    try:
        in_b = set(b)
        seen = set()
        out = []
        for x in a:
            if x in in_b and x not in seen:
                out.append(x)
                seen.add(x)
        return sorted(out)
    except TypeError:
        # Retain the old function's useful behavior for unhashable values.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """Return the nth Fibonacci number."""
    if n < 2:
        return n

    # Fast doubling, taking only O(log n) big-integer operations rather than
    # expanding the exponential recursive call tree.
    a, b = 0, 1  # F(0), F(1)
    for bit in bin(n)[2:]:
        c = a * (2 * b - a)       # F(2k)
        d = a * a + b * b         # F(2k + 1)
        if bit == "0":
            a, b = c, d
        else:
            a, b = d, c + d
    return a


def count_pairs(nums, target):
    """Count index pairs whose values sum to *target*."""
    # At each position, prior occurrences of its complement are precisely
    # the pairs ending at this position.
    frequencies = {}
    count = 0
    for x in nums:
        complement = target - x
        count += frequencies.get(complement, 0)
        frequencies[x] = frequencies.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove repeated values while retaining their first-seen order."""
    try:
        seen = set()
        out = []
        for x in items:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out
    except TypeError:
        # Lists/dicts and other unhashable values are supported as before.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
