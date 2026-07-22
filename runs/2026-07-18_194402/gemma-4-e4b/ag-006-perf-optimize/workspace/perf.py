"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Optimization: Use set intersection for O(N+M) time complexity.
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number."""
    # Optimization: Iterative approach (Dynamic Programming) for O(N) time complexity.
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Optimization: Use a hash map (dictionary) to achieve O(N) time complexity.
    count = 0
    seen_counts = {} # Stores frequency of numbers encountered so far
    for num in nums:
        complement = target - num
        if complement in seen_counts:
            # Every previous occurrence of the complement forms a valid pair with the current 'num'
            count += seen_counts[complement]
        
        # Update the count for the current number
        seen_counts[num] = seen_counts.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    # Optimization: Use a set for O(1) lookups while maintaining insertion order using dict keys (Python >= 3.7).
    # For compatibility and clarity, we use an ordered approach with a set tracker.
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
