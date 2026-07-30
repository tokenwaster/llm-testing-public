"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use set intersection for O(n) membership checks.
    return sorted(set(a).intersection(b))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    freq = {}
    for num in nums:
        freq[num] = freq.get(num, 0) + 1
    count = 0
    for num in nums:
        # decrement current number's frequency as we move forward
        freq[num] -= 1
        complement = target - num
        if complement in freq:
            count += freq[complement]
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
