"""Data helpers. Correct, and fast on production-sized inputs."""


def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    try:
        in_b = set(b)
        # dict.fromkeys keeps the first occurrence from `a`, so equal-but-
        # distinct values (1 vs True) resolve the same way the scan did.
        return sorted(dict.fromkeys(x for x in a if x in in_b))
    except TypeError:
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    prev, cur = 0, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    try:
        count = 0
        seen = {}
        for x in nums:
            count += seen.get(target - x, 0)
            seen[x] = seen.get(x, 0) + 1
        return count
    except TypeError:
        count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    count += 1
        return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
