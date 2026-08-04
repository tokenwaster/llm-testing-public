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
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    freq = {}
    count = 0
    for num in nums:
        complement = target - num
        count += freq.get(complement, 0)
        freq[num] = freq.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out