def common_elements(a, b):
    bs = set(b)
    out = []
    seen = set()
    for x in a:
        if x in bs and x not in seen:
            seen.add(x)
            out.append(x)
    out.sort()
    return out


def fib(n):
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    count = 0
    freq = {}
    for x in nums:
        complement = target - x
        if complement in freq:
            count += freq[complement]
        freq[x] = freq.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    out = []
    seen = set()
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
