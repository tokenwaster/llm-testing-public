import unittest
from textstats import summarize

class TestTextStats(unittest.TestCase):
    def test_basic(self):
        # "Dog." and "dog" are the same word
        res = summarize("Dog. dog")
        self.assertEqual(res, {"words": 2, "unique": 1, "avg_len": 3.0})

    def test_empty(self):
        res = summarize("")
        self.assertEqual(res, {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_whitespace(self):
        res = summarize("  \n\t  ")
        self.assertEqual(res, {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_punctuation_only(self):
        res = summarize("... !!! ,,,")
        self.assertEqual(res, {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_punctuation_and_words(self):
        res = summarize("... hello !!! world ,,,")
        self.assertEqual(res, {"words": 2, "unique": 2, "avg_len": 5.0})

    def test_avg_len_rounding(self):
        # words: "abc" (3), "abcd" (4), "ab" (2) -> sum = 9, len = 3 -> 3.0
        # let's do something that results in repeating decimal, e.g. sum = 8, len = 3 -> 2.6666... -> 2.67
        res = summarize("abc abcd ab")
        self.assertEqual(res["avg_len"], 3.0)
        
        res = summarize("abc abcd a")
        # lengths: 3, 4, 1 -> sum=8, count=3 -> 2.67
        self.assertEqual(res["avg_len"], 2.67)

    def test_punctuation_strip(self):
        # Leading and trailing punctuation
        res = summarize("(Hello), 'world'!")
        # "Hello", "world"
        self.assertEqual(res["words"], 2)
        self.assertEqual(res["unique"], 2)
        self.assertEqual(res["avg_len"], 5.0)

if __name__ == "__main__":
    unittest.main()
