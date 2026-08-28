

def common_elements(a, b):
    # Keep the representation and ordering semantics of the original loop,
    # but make membership checks constant-time for the usual hashable inputs.
    try:
        b_values = set(b)
        out = []
        seen = set()
        for x in a:
            if x in b_values and x not in seen:
                out.append(x)
                seen.add(x)
        return sorted(out)
    except TypeError:
        # The original accepts unhashable, equality-comparable values too.
        out = []
        for x in a:
            if x in b and x not in out:
                out.append(x)
        return sorted(out)


def fib(n):
    if n < 2:
        return n
    previous, current = 0, 1
    for _ in range(n):
        previous, current = current, previous + current
    return previous


def count_pairs(nums, target):
    count = 0
    complements = {}
    for value in nums:
        count += complements.get(target - value, 0)
        complements[value] = complements.get(value, 0) + 1
    return count


def dedupe_keep_order(items):
    # Materialize once so the fallback also works for one-shot iterables.
    items = list(items)
    out = []
    try:
        seen = set()
        for x in items:
            if x not in seen:
                seen.add(x)
                out.append(x)
    except TypeError:
        # Preserve the equality-based behavior for unhashable items.
        out = []
        for x in items:
            if x not in out:
                out.append(x)
    return out
