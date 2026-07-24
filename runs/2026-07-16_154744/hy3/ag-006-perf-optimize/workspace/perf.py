"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    counts = {}
    total = 0
    for x in nums:
        need = target - x
        total += counts.get(need, 0)
        counts[x] = counts.get(x, 0) + 1
    return total


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
