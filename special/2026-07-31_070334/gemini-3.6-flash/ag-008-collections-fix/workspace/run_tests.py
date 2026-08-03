import sys
import unittest

sys.path.insert(0, ".")
from tests.test_collkit import (
    TestChunk, TestFlatten, TestGroupBy, TestPartition, TestTakeWhile, TestUnique, TestWindows
)

if __name__ == "__main__":
    unittest.main()
