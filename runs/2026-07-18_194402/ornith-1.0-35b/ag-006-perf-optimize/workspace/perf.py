"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Convert to sets for O(1) lookup, then intersect
    set_a = set(a)
    set_b = set(b)
    return sorted(set_a & set_b)


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    
    # Iterative approach - O(n) time complexity
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use hash map to count occurrences - O(n) time complexity
    from collections import Counter
    
    counts = Counter(nums)
    count = 0
    
    for num in counts:
        complement = target - num
        if complement in counts:
            if num == complement:
                # For pairs with same value, use combination formula n*(n-1)/2
                count += counts[num] * (counts[num] - 1) // 2
            else:
                # For different values, multiply their counts
                # Only process when num < complement to avoid double counting
                if num < complement:
                    count += counts[num] * counts[complement]
    
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
