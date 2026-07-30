def common_elements(a, b):
    """Sorted list of values that appear in both a and b."""
    set_a = set(a)
    set_b = set(b)
    return sorted(set_a & set_b)

def fib(n):
    """nth Fibonacci number."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def count_pairs(nums, target):
    """Number of index pairs i<j with nums[i] + nums[j] == target."""
    freq = {}
    total = 0
    for num in nums:
        complement = target - num
        if complement in freq:
            total += freq[complement]
        freq[num] = freq.get(num, 0) + 1
    return total

def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out