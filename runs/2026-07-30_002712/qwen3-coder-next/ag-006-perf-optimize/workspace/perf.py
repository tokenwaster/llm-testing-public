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
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    
    total = 0
    for x in nums:
        complement = target - x
        total += counts.get(complement, 0)
        if complement == x:
            total -= 1
    
    return total // 2


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
