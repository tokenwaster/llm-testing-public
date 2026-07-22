def common_elements(a, b):
    return sorted(set(a) & set(b))

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n+1):
        a, b = b, a + b
    return b

def count_pairs(nums, target):
    counts = {}
    total = 0
    for num in nums:
        complement = target - num
        if complement in counts:
            total += counts[complement]
        counts[num] = counts.get(num, 0) + 1
    return total

def dedupe_keep_order(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result