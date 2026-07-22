"""Data helpers. Correct, but painfully slow on production-sized inputs."""

from __future__ import annotations


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    # Convert the second list to a set for O(1) membership checks.
    b_set = set(b)
    seen: set = set()
    out = []
    for x in a:
        if x in b_set and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    """nth Fibonacci number.

    Uses the fast‑doubling algorithm which runs in O(log n) time.
    """
    def _fib(k: int):
        if k == 0:
            return (0, 1)
        else:
            a, b = _fib(k >> 1)
            c = a * ((b << 1) - a)
            d = a * a + b * b
            if k & 1:
                return (d, c + d)
            else:
                return (c, d)
    return _fib(n)[0]


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target.

    Uses a single pass with a frequency dictionary for O(n) time.
    """
    freq: dict[int, int] = {}
    count = 0
    for x in nums:
        complement = target - x
        count += freq.get(complement, 0)
        freq[x] = freq.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first‑seen order."""
    seen: set = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
