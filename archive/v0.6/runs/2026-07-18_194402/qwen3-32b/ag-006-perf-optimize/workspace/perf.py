def common_elements(a, b):
    set_a = set(a)
    set_b = set(b)
    return sorted(set_a & set_b)

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

from collections import defaultdict

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
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result