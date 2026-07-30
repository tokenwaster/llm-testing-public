
# Optimised implementations of the original functions.
# The behaviour and signatures are unchanged, but performance has been
# improved so that the unit tests pass under stricter timing budgets.

from __future__ import annotations


def common_elements(a: list, b: list) -> list:
    """Return a sorted list of values that appear in both *a* and *b*.

    The original implementation performed an O(n²) membership test.  We
    now convert the second list to a set for constant‑time look‑ups and
    use a temporary set to avoid duplicates before sorting.
    """
    # Convert ``b`` to a set for fast membership checks.
    b_set = set(b)
    # Use a set to deduplicate elements that appear in both lists.
    common_set = {x for x in a if x in b_set}
    return sorted(common_set)


def fib(n: int) -> int:
    """Return the *n*th Fibonacci number (fib(0)=0, fib(1)=1).

    A simple iterative approach is sufficient for ``n`` up to a few thousand
    and runs in O(n) time.
    """
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums: list[int], target: int) -> int:
    """Count pairs ``i < j`` such that ``nums[i] + nums[j] == target``.

    The algorithm builds a frequency dictionary of the numbers seen so far
    and for each element looks up how many complementary values have been
    encountered earlier.  This runs in O(n) time.
    """
    freq: dict[int, int] = {}
    count = 0
    for num in nums:
        complement = target - num
        count += freq.get(complement, 0)
        freq[num] = freq.get(num, 0) + 1
    return count


def dedupe_keep_order(items: list) -> list:
    """Return a list with duplicates removed while preserving first‑seen order.

    The original implementation performed an O(n²) containment test.  We now
    keep a ``set`` of seen items and build the result in a single pass.
    """
    seen = set()
    out: list = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out

# The module is intentionally lightweight and only uses the standard library.
