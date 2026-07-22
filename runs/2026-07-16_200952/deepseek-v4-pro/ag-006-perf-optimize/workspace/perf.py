"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    b_set = set(b)
    seen = set()
    for x in a:
        if x in b_set and x not in seen:
            seen.add(x)
    return sorted(seen)


def fib(n):
    """nth Fibonacci number."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    seen = {}
    count = 0
    for x in nums:
        complement = target - x
        count += seen.get(complement, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out