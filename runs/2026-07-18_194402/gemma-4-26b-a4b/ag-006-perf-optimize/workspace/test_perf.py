import unittest
from perf import common_elements, fib, count_pairs, dedupe_keep_order

class TestPerf(unittest.TestCase):
    def test_common_elements(self):
        self.assertEqual(common_elements([1, 2, 3], [2, 3, 4]), [2, 3])
        self.assertEqual(common_elements([1, 1, 2], [1, 3]), [1])
        self.assertEqual(common_elements([], [1, 2]), [])
        self.assertEqual(common_elements([1, 2], []), [])

    def test_fib(self):
        self.assertEqual(fib(0), 0)
        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(2), 1)
        self.assertEqual(fib(3), 2)
        self.assertEqual(fib(10), 55)

    def test_count_pairs(self):
        self.assertEqual(count_pairs([1, 1, 1, 1], 2), 6) # (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
        self.assertEqual(count_pairs([1, 5, 7, -1, 5], 6), 3) # (1,5), (7,-1), (1,5) is wrong... wait.
        # Let's re-check: nums[i]+nums[j] == target with i < j
        # [1, 5, 7, -1, 5], target=6
        # pairs: (1,5) at indices 0,1; (1,5) at indices 0,4; (7,-1) at indices 2,3. Total 3. Correct.
        self.assertEqual(count_pairs([1, 2, 3, 4, 5], 6), 2) # (1,5), (2,4)

    def test_dedupe_keep_order(self):
        self.assertEqual(dedupe_keep_order([1, 2, 2, 3, 1, 4]), [1, 2, 3, 4])
        self.assertEqual(dedupe_keep_order(['a', 'b', 'a', 'c']), ['a', 'b', 'c'])
        self.assertEqual(dedupe_keep_order([]), [])

if __name__ == "__main__":
    unittest.main()
