

def common_elements(a, b):
    b_set = set(b)
    seen = set()
    out = []
    for x in a:
        if x in b_set and x not in seen:
            out.append(x)
            seen.add(x)
    return sorted(out)


def fib(n):
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    count = 0
    seen = {}
    for num in nums:
        complement = target - num
        if complement in seen:
            count += seen[complement]
        seen[num] = seen.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out
