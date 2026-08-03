def common_elements(a, b):
    """Return sorted list of values appearing in both lists."""
    b_set = set(b)
    seen = set()
    result = []
    for x in a:
        if x in b_set and x not in seen:
            result.append(x)
            seen.add(x)
    return sorted(result)


def fib(n):
    """Return nth Fibonacci number (fib(0)=0, fib(1)=1)."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    """Count number of index pairs i<j with nums[i]+nums[j] == target."""
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
            out.append(x)
            seen.add(x)
    return out
