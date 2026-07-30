"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use sets for O(n+m) intersection, then sort
    return sorted(set(a) & set(b))


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    # Iterative O(n) approach
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use a hash map to count frequencies - O(n)
    from collections import Counter
    freq = Counter(nums)
    count = 0
    
    for num in freq:
        complement = target - num
        if complement in freq:
            if num == complement:
                # Choose 2 from freq[num]
                count += freq[num] * (freq[num] - 1) // 2
            elif num < complement:
                # Count each pair once
                count += freq[num] * freq[complement]
    
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    # Use a set for O(1) membership checks
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out