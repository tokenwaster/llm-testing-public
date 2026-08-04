from collections import Counter


def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    count = 0
    seen = Counter()
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
