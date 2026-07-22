"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Using sets for O(1) average time complexity membership checks
    # and then sorting the intersection.
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use a dictionary to store the frequency of numbers seen so far.
    # For each number x, we check how many times (target - x) has appeared.
    count = 0
    seen = {}
    for x in nums:
        complement = target - x
        if complement in seen:
            count += seen[complement]
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    # Use a set for O(1) average time complexity membership checks.
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
