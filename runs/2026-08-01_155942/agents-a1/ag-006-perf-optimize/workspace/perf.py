def common_elements(a, b):
    # Use sets for efficient membership testing
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    # Iterative approach, O(n) time
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    # O(n) using hash map to track counts of seen numbers
    from collections import defaultdict
    count_map = defaultdict(int)
    count = 0
    for x in nums:
        complement = target - x
        if complement in count_map:
            count += count_map[complement]
        count_map[x] += 1
    return count


def dedupe_keep_order(items):
    # O(n) using set to track seen items
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
