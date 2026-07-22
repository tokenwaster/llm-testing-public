"""Data helpers. Optimized for production performance."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Use sets for O(1) membership testing
    set_a = set(a)
    set_b = set(b)
    # Intersection gives common elements, then sort
    return sorted(set_a & set_b)


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
    from collections import Counter
    count = 0
    freq = Counter(nums)
    
    for x in freq:
        y = target - x
        if y in freq:
            if x == y:
                # Count pairs within same value: C(n,2) = n*(n-1)/2
                count += freq[x] * (freq[x] - 1) // 2
            else:
                # Count pairs between different values
                count += freq[x] * freq[y]
    
    # Each pair counted twice (once for x, once for y)
    return count // 2


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out