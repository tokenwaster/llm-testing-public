import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collkit import chunk, flatten, group_by, take_while, unique, partition, windows

# test_chunk
assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
assert chunk([], 3) == []
try:
    chunk([1], 0)
    assert False
except ValueError: pass

# test_flatten
assert flatten([1, [2, 3], [4], 5]) == [1, 2, 3, 4, 5]
assert flatten(["ab", ["c"]]) == ["ab", "c"]

# test_group_by
assert group_by([1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}

# test_take_while
assert take_while([2, 4, 5, 6], lambda x: x % 2 == 0) == [2, 4]
assert take_while([1, 2], lambda x: x > 5) == []

# test_unique_values (order doesn't matter for values)
assert sorted(unique([3, 1, 3, 2, 1])) == [1, 2, 3]

# test_partition_union
y, n = partition([1, 2, 3, 4], lambda x: x > 2)
assert sorted(y + n) == [1, 2, 3, 4]

# test_windows_first
assert windows([1, 2, 3, 4], 2)[0] == [1, 2]

# failing tests - now should pass:
assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]
y, n = partition([1, 2, 3, 4], lambda x: x > 2)
assert y == [3, 4] and n == [1, 2]
assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]

print("All assertions passed!")
