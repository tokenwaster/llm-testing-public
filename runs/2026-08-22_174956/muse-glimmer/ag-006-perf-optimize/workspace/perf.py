def common_elements(a, b):
    # Intersection of sets, sorted
    return sorted(set(a) & set(b))


def fib(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def count_pairs(nums, target):
    seen = {}
    count = 0
    for num in nums:
        complement = target - num
        count += seen.get(complement, 0)
        seen[num] = seen.get(num, 0) + 1
    return count


def dedupe_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
