"""Data helpers. Correct, but painfully slow on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    try:
        return sorted(set(a) & set(b))
    except TypeError:
        out = []
        seen_a = set()
        for x in a:
            try:
                if x not in seen_a:
                    seen_a.add(x)
            except TypeError:
                pass
        for x in b:
            try:
                if x in seen_a and x not in out:
                    out.append(x)
            except TypeError:
                if x in a and x not in out:
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
    freq = {}
    count = 0
    for x in nums:
        complement = target - x
        if complement in freq:
            count += freq[complement]
        freq[x] = freq.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        seen = set()
        out = []
        for x in items:
            try:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            except TypeError:
                if x not in out:
                    out.append(x)
        return out
