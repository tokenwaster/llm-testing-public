"""Fast data helpers for production-sized inputs."""


def common_elements(a, b):
    """Return sorted values that appear in both *a* and *b*.

    Sets make membership and duplicate elimination linear rather than requiring
    a scan of the other input for every value.
    """
    b_values = set(b)
    return sorted({x for x in a if x in b_values})


def fib(n):
    """Return the nth Fibonacci number (with fib(0) == 0)."""
    if n < 2:
        return n

    # Fast doubling, processing the binary representation in O(log n) steps.
    # If (a, b) = (F(k), F(k+1)), doubling gives the pair for 2*k.
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * (2 * b - a)       # F(2k)
        d = a * a + b * b         # F(2k + 1)
        if bit == "0":
            a, b = c, d
        else:
            a, b = d, c + d
    return a


def count_pairs(nums, target):
    """Count index pairs ``i < j`` whose values sum to *target*."""
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
