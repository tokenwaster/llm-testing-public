def common_elements(a, b):
    # Original semantics: each value appearing in both lists, once, sorted.
    # Sets give O(n) membership instead of scanning b for every element of a.
    return sorted(set(a) & set(b))


def fib(n):
    # Same recurrence, computed iteratively in O(n) instead of exponential recursion.
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    # One pass: for each x, every previously seen value equal to target - x
    # forms a valid i<j pair. O(n) instead of O(n^2).
    seen = {}
    count = 0
    for x in nums:
        count += seen.get(target - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    # dict preserves insertion order and ignores duplicate keys: O(n), first-seen order kept.
    return list(dict.fromkeys(items))
