def common_elements(a, b):
    b_set = set(b)
    seen = set()
    out = []
    for x in a:
        if x in b_set and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    from collections import Counter
    counts = Counter(nums)
    result = 0
    for num in counts:
        complement = target - num
        if complement in counts:
            if num == complement:
                result += counts[num] * (counts[num] - 1) // 2
            elif num < complement:
                result += counts[num] * counts[complement]
    return result


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
