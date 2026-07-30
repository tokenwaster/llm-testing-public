"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Optimization: Use set intersection for O(N+M) complexity instead of O(N*M).
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number. Optimized using iteration (O(N))."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        # Calculate the next Fibonacci number
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target. Optimized to O(N)."""
    count = 0
    # Use a dictionary (hash map) to store counts of numbers encountered so far.
    seen_counts = {}

    for num in nums:
        complement = target - num
        
        # If the complement was seen before, every instance contributes to the count.
        if complement in seen_counts:
            count += seen_counts[complement]
        
        # Update the count for the current number
        seen_counts[num] = seen_counts.get(num, 0) + 1
        
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order. Optimized to O(N)."""
    # Use a set for fast lookups (O(1) average time complexity).
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
