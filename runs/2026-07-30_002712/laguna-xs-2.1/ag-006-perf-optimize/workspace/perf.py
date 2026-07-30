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
    from collections import Counter
    counts = Counter(nums)
    total = 0
    seen = set()
    for num, cnt in counts.items():
        complement = target - num
        if complement not in counts:
            continue
        pair_key = (min(num, complement), max(num, complement))
        if pair_key[0] == pair_key[1]:  # num == complement
            total += cnt * (cnt - 1) // 2
        elif pair_key not in seen:
            total += cnt * counts[complement]
            seen.add(pair_key)
    return total


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out