"""Data helpers. Optimized for production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    return sorted(set(a) & set(b))


def fib(n):
    """nth Fibonacci number (fib(0)=0, fib(1)=1)."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    from collections import Counter
    freq = Counter(nums)
    total = 0
    seen = set()
    for num in freq:
        if num in seen:
            continue
        complement = target - num
        if complement == num:
            # C(count, 2) pairs when both elements are the same value
            total += freq[num] * (freq[num] - 1) // 2
        elif complement > num:
            total += freq.get(complement, 0) * freq[num]
        seen.add(num)
    return total


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
