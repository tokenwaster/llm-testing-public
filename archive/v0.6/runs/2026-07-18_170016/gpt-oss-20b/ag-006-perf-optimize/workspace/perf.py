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
    # Count occurrences using a dictionary.
    counts = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    seen = set()
    total = 0
    for num in nums:
        complement = target - num
        if complement in counts:
            # For each occurrence of the current number, add pairs with its complement.
            total += counts[complement]
            # If complement equals num, we counted the pair (num,num) once too many;
            # subtract one to exclude pairing the element with itself.
            if complement == num:
                total -= 1
        seen.add(num)
    # Each unordered pair was counted twice (once for each order), so halve the result.
    return total // 2


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
