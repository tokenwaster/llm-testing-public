"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use set intersection for O(n + m) average time complexity
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    
    # Iterative approach for O(n) time and O(1) space complexity
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use a hash map to store counts of numbers seen so far for O(n) time complexity
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
    # Use a set to track seen elements for O(n) time complexity
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
