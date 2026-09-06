"""Optimized implementations (results identical to the original slow versions).

All four functions keep their original names/signatures and semantics; only the
algorithmic complexity changed:

  common_elements   O(n*m) membership scans  ->  O(n + m) set intersection
  fib               O(phi**n) recursion      ->  O(log n) fast doubling
  count_pairs       O(n**2) double loop      ->  O(n) running frequency table
  dedupe_keep_order O(n**2) list scans       ->  O(n) hash-set dedupe

Each function falls back to the original (slower) strategy if it is handed
unhashable values, so behaviour stays identical for any input type.
"""


def common_elements(a, b):
    """Sorted list of the distinct values that appear in both ``a`` and ``b``."""
    try:
        # set() removes duplicates and gives O(1) membership; '&' is O(min(n, m)).
        return sorted(set(a) & set(b))
    except TypeError:
        # Unhashable elements: fall back to the original scan-based approach.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """nth Fibonacci number with fib(0) == 0 and fib(1) == 1."""
    if n < 2:
        return n
    # Fast doubling: (F(k), F(k+1)) is advanced one bit of n at a time.
    a, b = 0, 1
    for bit in format(n, "b"):
        c = a * (2 * b - a)          # F(2k)
        d = a * a + b * b            # F(2k+1)
        if bit == "1":
            a, b = d, c + d          # (F(2k+1), F(2k+2))
        else:
            a, b = c, d              # (F(2k),   F(2k+1))
    return a


def count_pairs(nums, target):
    """Number of index pairs i < j with nums[i] + nums[j] == target."""
    try:
        seen = {}
        count = 0
        get = seen.get
        for x in nums:
            # Every earlier index holding target - x forms exactly one pair.
            count += get(target - x, 0)
            seen[x] = get(x, 0) + 1
        return count
    except TypeError:
        # Unhashable elements: fall back to the original O(n**2) scan.
        count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    count += 1
        return count


def dedupe_keep_order(items):
    """Drop duplicates from ``items``, keeping the first occurrence of each."""
    try:
        seen = set()
        seen_add = seen.add
        out = []
        append = out.append
        for x in items:
            if x not in seen:
                seen_add(x)
                append(x)
        return out
    except TypeError:
        # Unhashable elements: fall back to the original O(n**2) scan.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
