"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use sets for O(1) average lookup time
    set_a = set(a)
    set_b = set(b)
    # Intersection of two sets is efficient
    common = set_a.intersection(set_b)
    return sorted(list(common))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    # Use iterative approach to avoid exponential recursion O(n)
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use a hash map to store counts of numbers seen so far O(n)
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
    # Use a set to track seen items and a list for the result O(n)
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
