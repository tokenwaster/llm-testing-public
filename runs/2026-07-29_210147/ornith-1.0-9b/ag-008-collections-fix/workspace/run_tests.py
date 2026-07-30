import sys
sys.path.insert(0, ".")
from collkit import chunk, flatten, group_by, partition, take_while, unique, windows

# Test test_chunk
assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
assert chunk([], 3) == []
try:
    chunk([1], 0)
    assert False
except ValueError:
    pass

# Test test_flatten
assert flatten([1, [2, 3], [4], 5]) == [1, 2, 3, 4, 5]
assert flatten(["ab", ["c"]]) == ["ab", "c"]

# Test test_group_by
assert group_by([1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}

# Test test_take_while
assert take_while([2, 4, 5, 6], lambda x: x % 2 == 0) == [2, 4]
assert take_while([1, 2], lambda x: x > 5) == []

# Test test_unique_values (sorted version)
assert sorted(unique([3, 1, 3, 2, 1])) == [1, 2, 3]

# Test test_partition_union
y, n = partition([1, 2, 3, 4], lambda x: x > 2)
assert sorted(y + n) == [1, 2, 3, 4]

# Test test_windows_first
assert windows([1, 2, 3, 4], 2)[0] == [1, 2]

# Test test_unique_order (order-preserving)
assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]

# Test test_partition_orientation (yes first, then no)
y, n = partition([1, 2, 3, 4], lambda x: x > 2)
assert y == [3, 4] and n == [1, 2]

# Test test_windows_complete (include final window)
assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]

print("All tests passed!")
