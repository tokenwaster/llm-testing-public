

def common_elements(a, b):
    try:
        candidates = set(b)
        seen = set()
        out = []
        for x in a:
            if x in candidates and x not in seen:
                seen.add(x)
                out.append(x)
    except TypeError:
        # Preserve the original equality-based behavior for unhashable values.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
    return sorted(out)


def fib(n):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current
    return current


def count_pairs(nums, target):
    count = 0
    seen = {}
    for value in nums:
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        # Preserve the original equality-based behavior for unhashable values.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
        return out
