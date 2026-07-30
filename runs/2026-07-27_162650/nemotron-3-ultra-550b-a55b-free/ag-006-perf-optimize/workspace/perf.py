def common_elements(a, b):
    # Use sets for O(n+m) lookup instead of O(n*m)
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    # Iterative O(n) instead of exponential recursion
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    # Use a hash map for O(n) instead of O(n^2)
    from collections import Counter
    counts = Counter(nums)
    count = 0
    for num in counts:
        complement = target - num
        if complement in counts:
            if complement == num:
                # Choose 2 from count[num]
                count += counts[num] * (counts[num] - 1) // 2
            elif complement > num:
                # Avoid double counting
                count += counts[num] * counts[complement]
    return count


def dedupe_keep_order(items):
    # Use a set for O(1) lookup instead of O(n) list lookup
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out