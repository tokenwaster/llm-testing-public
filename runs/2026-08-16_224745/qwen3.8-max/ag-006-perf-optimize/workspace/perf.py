def common_elements(a, b):
    # Set intersection is O(len(a) + len(b)) instead of O(len(a) * len(b)).
    # The original kept unique values from `a` that also occur in `b`, then
    # sorted them -- exactly what a sorted intersection produces.
    try:
        return sorted(set(a) & set(b))
    except TypeError:
        # Fallback for unhashable elements: original semantics.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    # Iterative O(n) instead of exponential recursion.
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    # Single pass with a hash map of previously seen values: O(n).
    # For each element x, every earlier element equal to (target - x)
    # forms exactly one pair (i, j) with i < j.
    try:
        seen = {}
        count = 0
        for x in nums:
            count += seen.get(target - x, 0)
            seen[x] = seen.get(x, 0) + 1
        return count
    except TypeError:
        # Fallback for unhashable/non-subtractable elements: original semantics.
        count = 0
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] == target:
                    count += 1
        return count


def dedupe_keep_order(items):
    # Membership test against a set (O(1)) instead of a list (O(n)).
    try:
        seen = set()
        out = []
        for x in items:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out
    except TypeError:
        # Fallback for unhashable elements: original semantics.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
