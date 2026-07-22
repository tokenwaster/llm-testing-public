"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Using set intersection is O(N + M) and then sorting is O(K log K) where K is the size of the intersection.
    # Since we want values appearing in both lists, we can do set(a) & set(b) and then sort.
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number."""
    # Iterative O(n) approach
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # We can use a hash map (dict) to count occurrences of each number.
    # For each number x, we need to find how many times (target - x) has appeared before it.
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
    # In Python 3.7+, dict preserves insertion order.
    # dict.fromkeys(items) creates a dictionary with items as keys, preserving order, and we convert it back to a list.
    # This is O(n) and extremely fast.
    return list(dict.fromkeys(items))
