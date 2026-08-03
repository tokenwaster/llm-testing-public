def common_elements(a, b):
    """Return sorted list of values appearing in both lists."""
    set_b = set(b)
    return sorted(set(x for x in a if x in set_b))


def fib(n):
    """Return nth Fibonacci number (fib(0)=0, fib(1)=1)."""
    if n < 2:
        return n
    
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


def count_pairs(nums, target):
    """Count index pairs i<j with nums[i]+nums[j] == target."""
    count = 0
    complement_count = {}
    
    for num in nums:
        needed = target - num
        if needed in complement_count:
            count += complement_count[needed]
        complement_count[num] = complement_count.get(num, 0) + 1
    
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
