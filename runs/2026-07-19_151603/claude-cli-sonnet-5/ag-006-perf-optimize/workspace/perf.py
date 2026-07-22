"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    b_set = set(b)
    return sorted(set(x for x in a if x in b_set))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(n - 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    counts = {}
    count = 0
    for x in nums:
        need = target - x
        count += counts.get(need, 0)
        counts[x] = counts.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
