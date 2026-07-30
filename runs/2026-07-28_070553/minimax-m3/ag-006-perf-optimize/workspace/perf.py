def common_elements(a, b):
    return sorted(set(a) & set(b))


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    counts = {}
    for x in nums:
        c = counts.get(x)
        if c is None:
            counts[x] = 1
        else:
            counts[x] = c + 1
    total = 0
    for x, c in counts.items():
        need = target - x
        if need in counts:
            c2 = counts[need]
            if x == need:
                total += c * (c - 1) // 2
            elif x < need:
                total += c * c2
    return total


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
