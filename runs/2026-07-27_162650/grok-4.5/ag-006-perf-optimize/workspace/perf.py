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
    freq = Counter(nums)
    count = 0
    seen = set()
    for x in freq:
        y = target - x
        if y in freq and y not in seen:
            if x == y:
                count += freq[x] * (freq[x] - 1) // 2
            elif y in freq:
                count += freq[x] * freq[y]
            seen.add(x)
            seen.add(y)
    return count


def dedupe_keep_order(items):
    return list(dict.fromkeys(items))
