def common_elements(a, b):
    set_b = set(b)
    seen = set()
    out = []
    for x in a:
        if x in set_b and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


def fib(n):
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    total = 0
    seen_vals = set()
    for x in counts:
        if x in seen_vals:
            continue
        y = target - x
        if y in counts:
            if x == y:
                c = counts[x]
                total += c * (c - 1) // 2
            else:
                total += counts[x] * counts[y]
        seen_vals.add(x)
        seen_vals.add(y)
    return total


def dedupe_keep_order(items):
    seen = set()
    out = []
    append = out.append
    for x in items:
        if x not in seen:
            seen.add(x)
            append(x)
    return out
