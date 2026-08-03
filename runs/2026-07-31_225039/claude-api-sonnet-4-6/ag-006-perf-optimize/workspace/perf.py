from functools import lru_cache


def common_elements(a, b):
    # O(n+m): convert b to a set for O(1) lookup; use a set to track seen values
    b_set = set(b)
    seen = set()
    out = []
    for x in a:
        if x in b_set and x not in seen:
            seen.add(x)
            out.append(x)
    return sorted(out)


@lru_cache(maxsize=None)
def fib(n):
    # O(n): memoised recursion collapses exponential tree to linear work
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def count_pairs(nums, target):
    # O(n): for each number, check whether its complement has been seen
    seen = {}          # value -> count of occurrences so far
    count = 0
    for x in nums:
        complement = target - x
        if complement in seen:
            count += seen[complement]
        seen[x] = seen.get(x, 0) + 1
    return count


def dedupe_keep_order(items):
    # O(n): use a set for O(1) membership test instead of scanning the list
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
