

def common_elements(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def dedupe_keep_order(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out
