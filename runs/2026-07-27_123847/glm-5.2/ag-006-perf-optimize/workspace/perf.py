"""Data helpers. Correct and fast on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    if len(a) > len(b):
        a, b = b, a
    bset = set(b)
    out = [x for x in a if x in bset]
    # dedupe while preserving enough info to sort
    return sorted(set(out))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
    return cur


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    count = 0
    seen = {}
    for x in nums:
        complement = target - x
        count += seen.get(complement, 0)
        seen[x] = seen.get(x, 0) + 1
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
