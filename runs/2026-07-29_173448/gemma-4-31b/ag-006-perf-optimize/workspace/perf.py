
def common_elements(a, b):
    return sorted(list(set(a) & set(b)))


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    counts = {}
    pair_count = 0
    for x in nums:
        complement = target - x
        if complement in counts:
            pair_count += counts[complement]
        counts[x] = counts.get(x, 0) + 1
    return pair_count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
