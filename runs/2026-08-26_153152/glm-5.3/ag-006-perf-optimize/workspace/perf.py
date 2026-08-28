"""Optimized versions of the original (correct but slow) helpers.

Every function keeps its exact original semantics; only the algorithms
were improved.  Slow brute-force paths are retained purely as fallbacks
for exotic inputs (e.g. unhashable elements) where the fast paths cannot
be applied.
"""


def common_elements(a, b):
    """Sorted list of values appearing in both lists.

    Original cost: O(len(a) * len(b)).  New cost: O(len(a) + len(b)) plus
    the final sort.
    """
    try:
        out = set(a) & set(b)
    except TypeError:
        # Unhashable elements: fall back to the original semantics.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
    return sorted(out)


def fib(n):
    """nth Fibonacci number (fib(0)=0, fib(1)=1).

    Original cost: exponential (recursive tree).  New cost: O(log n) big-int
    multiplications via the fast-doubling identities:

        F(2k)   = F(k) * (2*F(k+1) - F(k))
        F(2k+1) = F(k)^2 + F(k+1)^2
    """
    if n < 2:
        return n
    a, b = 0, 1  # (F(0), F(1))
    for bit in bin(n)[2:]:
        # Double:  (F(k), F(k+1)) -> (F(2k), F(2k+1))
        c = a * ((b << 1) - a)
        d = a * a + b * b
        if bit == '1':
            a, b = d, c + d
        else:
            a, b = c, d
    return a


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i]+nums[j] == target.

    Original cost: O(n^2).  New cost: O(n) using a value -> multiplicity
    table.  Each unordered pair of values is counted from both sides, so
    the accumulated total is halved at the end; equal value/complement
    pairs contribute c*(c-1) (already even), i.e. C(c, 2) after halving.
    """
    try:
        counts = {}
        for x in nums:
            counts[x] = counts.get(x, 0) + 1

        total = 0
        for value, c in counts.items():
            complement = target - value
            c2 = counts.get(complement)
            if c2 is None or value + complement != target:
                continue  # not present, or inexact arithmetic
            if complement == value:
                total += c * (c - 1)
            else:
                total += c * c2
        return total // 2
    except TypeError:
        pass

    # Fallback for unhashable / non-numeric values: original semantics.
    count = 0
    n = len(nums)
    for i in range(n):
        vi = nums[i]
        for j in range(i + 1, n):
            if vi + nums[j] == target:
                count += 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order.

    Original cost: O(n^2) (linear membership scans).  New cost: O(n) using
    an insertion-ordered dict as an ordered set.
    """
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        # Unhashable items: fall back to the original semantics.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
