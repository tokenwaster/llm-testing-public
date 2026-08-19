from collections import defaultdict


def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    count = 0
    seen = defaultdict(int)
    for x in nums:
        complement = target - x
        if complement in seen:
            count += seen[complement]
        seen[x] += 1
    return count


def dedupe_keep_order(items):
    return list(dict.fromkeys(items))
