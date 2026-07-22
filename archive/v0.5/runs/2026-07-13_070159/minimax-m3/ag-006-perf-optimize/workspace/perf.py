"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    b_set = set(b)
    seen = set()
    out = []
    for x in a:
        if x in b_set and x not in seen:
            seen.add(x)
            out.append(x)
    out.sort()
    return out


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    total = 0
    for x, c in counts.items():
        y = target - x
        if y < x:
            continue
        if y == x:
            total += c * (c - 1) // 2
        else:
            total += c * counts.get(y, 0)
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
