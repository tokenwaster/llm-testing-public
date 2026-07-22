"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use set intersection for O(N+M) time complexity
    return sorted(list(set(a) & set(b)))


def fib(n):
    """nth Fibonacci number. Optimized using iteration (O(n))."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(2, n + 1):
        # Calculate next Fibonacci number
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target. Optimized to O(N)."""
    count = 0
    # Dictionary to store the frequency of numbers encountered so far (at indices < j)
    seen_counts = {}

    for num in nums:
        complement = target - num
        
        # If the complement has been seen, every previous occurrence forms a valid pair with 'num'
        count += seen_counts.get(complement, 0)
        
        # Record the current number's frequency
        seen_counts[num] = seen_counts.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order. Optimized to O(N)."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
