"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out
