

def common_elements(a, b):
    try:
        return sorted(set(a).intersection(b))
    except TypeError:
        # Preserve support for unhashable values.
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
    try:
        for number in nums:
            count += seen.get(target - number, 0)
            seen[number] = seen.get(number, 0) + 1
        return count
    except TypeError:
        # Preserve the original behavior for non-hashable numeric-like values.
        return sum(
            nums[i] + nums[j] == target
            for i in range(len(nums))
            for j in range(i + 1, len(nums))
        )


def dedupe_keep_order(items):
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        # Preserve support for unhashable values.
        out = []
        for item in items:
            if item not in out:
                out.append(item)
        return out
