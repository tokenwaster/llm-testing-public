"""Data helpers. Optimized implementations for production use.

The original versions were correct but inefficient (quadratic or exponential).
These replacements keep the same public API and exact behavior while running
within the required time budgets.
"""

def common_elements(a, b):
    """Sorted list of values that appear in both ``a`` and ``b``.

    The original implementation performed ``x in b`` checks inside a loop,
    resulting in O(len(a) * len(b)) time.  By converting the inputs to sets we
    can compute the intersection in linear time and then return the sorted
    result.
    """
    # Use set intersection to find common values efficiently.
    # ``sorted`` will return a list in ascending order.
    return sorted(set(a) & set(b))


def fib(n):
    """Return the *n*th Fibonacci number (fib(0)=0, fib(1)=1).

    The naïve recursive version has exponential complexity.  An iterative
    approach runs in O(n) time and O(1) space, which is trivial for n=300.
    """
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Count index pairs ``i < j`` such that ``nums[i] + nums[j] == target``.

    A hash‑map (dictionary) of previously‑seen values lets us count matching
    complements in a single pass, giving O(n) time.
    """
    seen = {}
    count = 0
    for num in nums:
        complement = target - num
        # Pairs where the complement has already been seen contribute to the
        # total count.  ``seen.get`` returns 0 when the complement is absent.
        count += seen.get(complement, 0)
        # Record the current number for future complements.
        seen[num] = seen.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates from *items* while preserving the first‑seen order.

    The original O(n²) scan is replaced by a set that tracks which elements
    have already been emitted.
    """
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
