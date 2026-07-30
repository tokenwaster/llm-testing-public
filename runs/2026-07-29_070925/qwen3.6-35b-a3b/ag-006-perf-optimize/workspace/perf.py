def common_elements(a, b):
    set_a = set(a)
    set_b = set(b)
    return sorted(set_a & set_b)


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    count = 0
    seen = {}
    for x in nums:
        needed = target - x
        if needed in seen:
            count += seen[needed]
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
