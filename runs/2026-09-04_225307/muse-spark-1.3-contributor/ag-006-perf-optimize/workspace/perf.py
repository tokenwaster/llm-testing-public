def common_elements(a, b):
    try:
        return sorted(set(a) & set(b))
    except TypeError:
        # Fallback for unhashable elements (small inputs only)
        out = []
        for x in a:
            if x in b and x not in out:
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
    # Single-pass hashmap: count complements seen so far
    freq = {}
    count = 0
    get = freq.get
    for num in nums:
        count += get(target - num, 0)
        freq[num] = get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    # dict preserves insertion order and is fast; fallback for unhashable
    try:
        return list(dict.fromkeys(items))
    except TypeError:
        seen_hashable = set()
        out = []
        # track unhashable seen separately via list scan (rare case)
        unhashable_seen = []
        for x in items:
            try:
                if x not in seen_hashable:
                    seen_hashable.add(x)
                    out.append(x)
            except TypeError:
                if x not in unhashable_seen:
                    unhashable_seen.append(x)
                    out.append(x)
        return out
