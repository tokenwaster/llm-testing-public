"""Fast data helpers for production-sized inputs."""


def common_elements(a, b):
    """Return sorted values that appear in both *a* and *b*, without repeats."""
    # A set makes the membership test linear overall rather than scanning b for
    # every item in a.  Keep the scan of a so the output still contains each
    # value only once, just as the original implementation did.
    b_values = set(b)
    out = set()
    for value in a:
        if value in b_values:
            out.add(value)
    return sorted(out)


def fib(n):
    """Return the nth Fibonacci number (with fib(0) == 0)."""
    if n < 2:
        return n

    # Fast doubling: (F(2k), F(2k+1)) from (F(k), F(k+1)).  This uses
    # logarithmically many big-integer operations instead of exponential
    # recursion.
    def doubling(k):
        if k == 0:
            return 0, 1
        a, b = doubling(k // 2)
        c = a * (2 * b - a)
        d = a * a + b * b
        if k & 1:
            return d, c + d
        return c, d

    return doubling(n)[0]


def count_pairs(nums, target):
    """Return the number of index pairs i < j whose sum is *target*."""
    seen = {}
    count = 0
    for value in nums:
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates from *items*, preserving first-seen order."""
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
