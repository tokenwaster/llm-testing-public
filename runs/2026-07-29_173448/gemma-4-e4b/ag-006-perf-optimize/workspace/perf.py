def common_elements(a, b):
    # Optimization: Use set intersection for O(N) performance.
    return sorted(set(a) & set(b))


def fib(n):
    # Optimization: Use iterative approach (DP) for O(N) performance.
    if n < 0:
        raise ValueError("Fibonacci is defined for non-negative integers.")
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_pairs(nums, target):
    # Optimization: Use a frequency map/hash table for O(N) performance.
    count = 0
    seen = {} # Maps number to its count of occurrences up to the current index i-1

    for num in nums:
        complement = target - num
        if complement in seen:
            # Every time we see 'num', it forms a pair with all previously seen 'complement' numbers.
            count += seen[complement]
        
        # Update the count of the current number
        seen[num] = seen.get(num, 0) + 1
        
    return count


def dedupe_keep_order(items):
    # Optimization: Use dict.fromkeys() (Python >= 3.7) for O(N) performance while maintaining order.
    return list(dict.fromkeys(items))
