"""Data helpers. Correct, but painfully slow on production-sized inputs."""

from typing import List, Iterable


def common_elements(a: Iterable[int], b: Iterable[int]) -> List[int]:
    """Sorted list of values that appear in both a and b."""
    # Convert to sets for O(1) membership checks.
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n: int) -> int:
    """nth Fibonacci number."""
    # Use iterative DP to avoid recursion overhead.
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums: List[int], target: int) -> int:
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    # Use hash map to store counts of seen numbers.
    from collections import defaultdict
    freq = defaultdict(int)
    count = 0
    for num in nums:
        complement = target - num
        count += freq[complement]
        freq[num] += 1
    return count


def dedupe_keep_order(items: Iterable[int]) -> List[int]:
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
