import sys
import os
sys.path.append(os.getcwd())
from collkit import (chunk, flatten, group_by, partition, take_while, unique, windows)

def test_unique_order():
    assert unique([3, 1, 3, 2, 1]) == [3, 1, 2]

def test_partition_orientation():
    y, n = partition([1, 2, 3, 4], lambda x: x > 2)
    assert y == [3, 4] and n == [1, 2]

def test_windows_complete():
    assert windows([1, 2, 3, 4], 2) == [[1, 2], [2, 3], [3, 4]]

if __name__ == "__main__":
    try:
        test_unique_order()
        test_partition_orientation()
        test_windows_complete()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
