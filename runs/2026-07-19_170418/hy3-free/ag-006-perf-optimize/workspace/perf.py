"""Data helpers. Correct and fast on production-sized inputs."""

from collections import Counter


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


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
    counts = Counter(nums)
    total = 0
    for x, cx in counts.items():
        y = target - x
        if y not in counts:
            continue
        cy = counts[y]
        if x == y:
            total += cx * (cx - 1) // 2
        else:
            total += cx * cy
    # For x != y, each unordered pair was counted twice (once as (x,y), once as (y,x)).
    # The x == y contributions are already correct, so divide only the cross term.
    # Recompute cleanly: total currently = same_pairs + 2*cross_pairs.
    # We want same_pairs + cross_pairs = total - cross_pairs.
    # Easier: subtract the cross contribution by halving the non-equal part.
    # Compute cross separately:
    cross = 0
    for x, cx in counts.items():
        y = target - x
        if y in counts and x < y:
            cross += cx * counts[y]
    same = 0
    if target % 2 == 0:
        h = target // 2
        if h in counts:
            same = counts[h] * (counts[h] - 1) // 2
    return same + cross


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
