from perf import common_elements, fib, count_pairs, dedupe_keep_order


def common_elements_slow(a, b):
    out = []
    for x in a:
        if x in b and x not in out:
            out.append(x)
    return sorted(out)


def fib_slow(n):
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)


def count_pairs_slow(nums, target):
    count = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                count += 1
    return count


def dedupe_keep_order_slow(items):
    out = []
    for x in items:
        if x not in out:
            out.append(x)
    return out


assert common_elements([3, 1, 2, 2, 4], [2, 5, 1, 1]) == common_elements_slow([3, 1, 2, 2, 4], [2, 5, 1, 1])
assert common_elements([], [1]) == []
assert common_elements([1, 1], [1, 1]) == [1]
assert common_elements([5, 3, 1], [1, 3, 5]) == [1, 3, 5]

for i in range(20):
    assert fib(i) == fib_slow(i), i
assert fib(0) == 0
assert fib(1) == 1
assert fib(10) == 55
assert fib(300) == 222232244629420445529739893461909967206666939096499764990979600

assert count_pairs([1, 2, 3, 4], 5) == count_pairs_slow([1, 2, 3, 4], 5)
assert count_pairs([1, 1, 1, 1], 2) == count_pairs_slow([1, 1, 1, 1], 2)
assert count_pairs([0, -1, 1, 0], 0) == count_pairs_slow([0, -1, 1, 0], 0)
assert count_pairs([], 1) == 0
assert count_pairs([5], 10) == 0
assert count_pairs([1, 5, 3, 3, 2], 6) == count_pairs_slow([1, 5, 3, 3, 2], 6)

assert dedupe_keep_order([1, 2, 1, 3, 2]) == [1, 2, 3]
assert dedupe_keep_order([]) == []
assert dedupe_keep_order(["a", "b", "a"]) == ["a", "b"]
assert dedupe_keep_order([None, 0, None, 0, 1]) == [None, 0, 1]

print("all ok")
print("fib(300)", fib(300))
