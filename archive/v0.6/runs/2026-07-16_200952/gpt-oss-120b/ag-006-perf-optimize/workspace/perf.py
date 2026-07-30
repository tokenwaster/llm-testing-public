"""Data helpers. Optimized for performance.

The original implementations were correct but used naive algorithms that
scaled poorly (quadratic or exponential).  The functions below retain the
exact same public behaviour while using efficient standard‑library
techniques so they meet the timing budgets required by the benchmark.
"""


def common_elements(a, b):
    """Return a sorted list of values that appear in both *a* and *b*.

    The original version performed a linear scan with ``x in b`` and
    ``x not in out`` which is O(n·m).  Converting the inputs to ``set`` objects
    gives O(n + m) membership checks, and the intersection yields the unique
    common values.  Finally we sort the result to match the documented output.
    """
    # Using set intersection automatically removes duplicates and provides
    # O(1) average‑time membership tests.
    return sorted(set(a) & set(b))


def fib(n):
    """Return the *n*th Fibonacci number (fib(0)=0, fib(1)=1).

    The naïve recursive definition has exponential time complexity.  An
    iterative loop runs in O(n) time and O(1) space, which is trivial for the
    required ``n <= 300`` but also scales to much larger inputs.
    """
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Count index pairs ``i < j`` with ``nums[i] + nums[j] == target``.

    A hash map (dictionary) stores how many times each value has been seen so
    far while iterating from left to right.  For each element ``x`` we look for
    its complement ``target - x`` among the previously‑seen numbers; the stored
    count of that complement contributes directly to the answer.  This yields
    O(n) time and O(n) additional space.
    """
    seen = {}
    count = 0
    for x in nums:
        complement = target - x
        count += seen.get(complement, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Return a list with duplicates removed, preserving the first occurrence.

    The original implementation used ``x not in out`` which is O(n²).  By
    keeping a ``set`` of items already encountered we achieve O(n) time while
    still returning the elements in their original order.
    """
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
