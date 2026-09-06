def common_elements(a, b):
    try:
        return sorted(set(a).intersection(b))
    except TypeError:
        return sorted(dedupe_keep_order(x for x in a if x in b))


def fib(n):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def count_pairs(nums, target):
    count = 0
    seen = {}
    for value in nums:
        count += seen.get(target - value, 0)
        seen[value] = seen.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    out = []
    seen = set()
    unhashable = []
    for value in items:
        try:
            hash(value)
        except TypeError:
            if value not in out:
                out.append(value)
                unhashable.append(value)
        else:
            if value not in seen and value not in unhashable:
                seen.add(value)
                out.append(value)
    return out
