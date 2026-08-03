def common_elements(a, b):
    # Use set intersection for O(len(a) + len(b)) time
    return sorted(set(a) & set(b))


def fib(n):
    # Iterative approach: O(n) time, O(1) space
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    # One-pass with frequency map: O(n) time
    seen = {}
    count = 0
    for x in nums:
        complement = target - x
        if complement in seen:
            count += seen[complement]
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    # Use set to track seen items for O(n) average time
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
