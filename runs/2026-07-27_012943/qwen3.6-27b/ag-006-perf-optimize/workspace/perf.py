"""Data helpers. Correct, and now fast on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    set_b = set(b)
    out = []
    seen = set()
    for x in a:
        if x in set_b and x not in seen:
            out.append(x)
            seen.add(x)
    return sorted(out)


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    count = 0
    seen = {}
    for x in nums:
        complement = target - x
        if complement in seen:
            count += seen[complement]
        if x in seen:
            seen[x] += 1
        else:
            seen[x] = 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
