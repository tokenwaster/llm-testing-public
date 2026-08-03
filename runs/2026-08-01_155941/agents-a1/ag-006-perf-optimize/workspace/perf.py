def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    seen = {}
    count = 0
    for x in nums:
        needed = target - x
        if needed in seen:
            count += seen[needed]
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
