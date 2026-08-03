import sys
sys.path.insert(0, '.')

from collkit import (chunk, flatten, group_by, partition, take_while, unique, windows)
import pytest

def run_tests():
    # Run each test manually by calling the functions and checking assertions
    
    print("Running tests...")
    
    # chunk tests
    try:
        assert chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
        assert chunk([], 3) == []
        with pytest.raises(ValueError):
            chunk([1], 0)
        print("test_chunk: PASS")
    except Exception as e:
        print(f"test_chunk: FAIL - {e}")

    # flatten tests
    try:
        assert flatten([1, [2, 3], [4], 5]) == [1, 2, 3, 4, 5]
        assert flatten(["ab", ["c"]]) == ["ab", "c"]
        print("test_flatten: PASS")
    except Exception as e:
        print(f"test_flatten: FAIL - {e}")

    # group_by test
    try:
        assert group_by([1, 2, 3, 4], lambda x: x % 2) == {1: [1, 3], 0: [2, 4]}
        print("test_group_by: PASS")
    except Exception as e:
        print(f"test_group_by: FAIL - {e}")

    # take_while test
    try:
        assert take_while([2, 4, 5, 6], lambda x: x % 2 == 0) == [2, 4]
        assert take_while([1, 2], lambda x: x > 5) == []
        print("test_take_while: PASS")
    except Exception as e:
        print(f"test_take_while: FAIL - {e}")

    # unique test (sorted order expected in some tests)
    try:
        assert sorted(unique([3, 1, 3, 2, 1])) == [1, 2, 3]
        print("test_unique_values: PASS")
    except Exception as e:
        print(f"test_unique_values: FAIL - {e}")

    # partition union test
    try:
        y, n = partition([1, 2, 3, 4], lambda x: x > 2)
        assert sorted(y + n) == [1, 2, 3, 4]
        print("test_partition_union: PASS")
    except Exception as e:
        print(f"test_partition_union: FAIL - {e}")

    # windows first test
    try:
        assert windows([1, 2, 3, 4], 2)[0] == [1, 2]
        print("test_windows_first: PASS")
    except Exception as e:
        print(f"test_windows_first: FAIL - {e}")

    # unique order test (order-preserving de-duplication)
    try:
        assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]
        print("test_unique_order: PASS")
    except Exception as e:
        print(f"test_unique_order: FAIL - {e}")

    # partition orientation test (matches first)
    try:
        y, n = partition([1, 2, 3, 4], lambda x: x > 2)
        assert y == [3, 4] and n == [1, 2]
        print("test_partition_orientation: PASS")
    except Exception as e:
        print(f"test_partition_orientation: FAIL - {e}")

    # windows complete test (include final window)
    try:
        assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]
        print("test_windows_complete: PASS")
    except Exception as e:
        print(f"test_windows_complete: FAIL - {e}")

if __name__ == "__main__":
    run_tests()
