import pytest

from collkit import (chunk, flatten, group_by, partition, take_while, unique,
                     windows)


def _guards_intact():
    assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunk([], 3) == []
    with pytest.raises(ValueError):
        chunk([1], 0)
    assert flatten([1, [2, 3], [4], 5]) == [1, 2, 3, 4, 5]
    assert flatten(["ab", ["c"]]) == ["ab", "c"]
    assert group_by([1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}
    assert take_while([2, 4, 5, 6], lambda x: x % 2 == 0) == [2, 4]
    assert take_while([1, 2], lambda x: x > 5) == []
    assert sorted(unique([3, 1, 3, 2, 1])) == [1, 2, 3]
    y, n = partition([1, 2, 3, 4], lambda x: x > 2)
    assert sorted(y + n) == [1, 2, 3, 4]
    assert windows([1, 2, 3, 4], 2)[0] == [1, 2]
    with pytest.raises(ValueError):
        windows([1], 0)


def test_fix_unique_preserves_order():
    _guards_intact()
    assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert unique(["b", "a", "b", "c"]) == ["b", "a", "c"]


def test_fix_partition_matches_first():
    _guards_intact()
    y, n = partition([1, 2, 3, 4, 5], lambda x: x % 2 == 0)
    assert y == [2, 4] and n == [1, 3, 5]


def test_fix_windows_includes_last():
    _guards_intact()
    assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]
    assert windows([1, 2, 3], 3) == [[1, 2, 3]]
    assert windows([1, 2], 3) == []
