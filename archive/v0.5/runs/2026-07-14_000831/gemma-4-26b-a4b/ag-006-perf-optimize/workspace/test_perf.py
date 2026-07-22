import perf

def original_common_elements(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)

def original_fib(n):
    if n < 2:
        return n
    return original_fib(n - 1) + original_fib(n - 2)

def original_count_pairs(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count

def original_dedupe_keep_order(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out

def test():
    # Test common_elements
    a = [1, 2, 3, 4, 5]
    b = [3, 4, 5, 6, 7]
    assert perf.common_elements(a, b) == original_common_elements(a, b), "common_elements failed"

    # Test fib
    for n in range(10):
        assert perf.fib(n) == original_fib(n), f"fib({n}) failed"

    # Test count_pairs
    nums = [1, 2, 3, 4, 5, 1, 2]
    target = 5
    assert perf.count_pairs(nums, target) == original_count_pairs(nums, target), "count_pairs failed"

    # Test dedupe_keep_order
    items = [1, 2, 2, 3, 4, 4, 5, 1]
    assert perf.dedupe_keep_order(items) == original_dedupe_keep_order(items), "dedupe_keep_order failed"

    print("All tests passed!")

if __name__ == "__main__":
    test()
