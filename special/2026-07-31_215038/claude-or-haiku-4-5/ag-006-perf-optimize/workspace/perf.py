def common_elements(a, b):
    """Return sorted list of values appearing in both lists."""
    b_set = set(b)
    seen = {}
    for x in a:
        if x in b_set and x not in seen:
            seen[x] = True
    return sorted(seen.keys())


def fib(n):
    """Return the nth Fibonacci number."""
    if n < 2:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Count index pairs i<j where nums[i]+nums[j] == target."""
    count = 0
    seen = {}
    
    for num in nums:
        complement = target - num
        if complement in seen:
            count += seen[complement]
        
        seen[num] = seen.get(num, 0) + 1
    
    return count


def dedupe_keep_order(items):
    """Remove duplicates, preserving first-seen order."""
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
