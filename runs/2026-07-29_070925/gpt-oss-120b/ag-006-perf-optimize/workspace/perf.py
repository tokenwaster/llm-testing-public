def common_elements(a, b):
    """Return a sorted list of unique values appearing in both input iterables.

    The original implementation used nested loops resulting in O(len(a) * len(b))
    time which is far too slow for large inputs.  Converting the inputs to sets
    allows us to compute the intersection in linear time and then sort the
    result, which satisfies the required behaviour while meeting the timing
    budget.
    """
    # Convert to sets to eliminate duplicates and enable fast membership tests.
    # Intersection gives the unique common elements.
    return sorted(set(a) & set(b))


def fib(n):
    """Return the nth Fibonacci number (fib(0)=0, fib(1)=1).

    The naïve recursive version has exponential time complexity.  An
    iterative approach runs in O(n) time and O(1) space, which easily handles
    n=300 within the required time limits.
    """
    if n < 0:
        raise ValueError("n must be non‑negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    """Count index pairs (i < j) such that nums[i] + nums[j] == target.

    A hash‑map tracks how many times each value has been seen so far. For each
    element we look for the complement (target - current) among previously
    visited elements; the number of such complements contributes to the total
    count. This runs in O(n) time.
    """
    from collections import Counter

    # We could also use a simple dict, but Counter provides a convenient API.
    seen = Counter()
    count = 0
    for num in nums:
        complement = target - num
        count += seen[complement]
        seen[num] += 1
    return count


def dedupe_keep_order(items):
    """Return a list with duplicates removed, preserving the first occurrence.

    Using a set to record items already emitted reduces the operation to O(n)
    time instead of the original O(n²) approach.
    """
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
