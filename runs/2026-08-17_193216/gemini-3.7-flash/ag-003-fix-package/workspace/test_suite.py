import unittest
from textstats import summarize


class TestTextStats(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize(""), {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_whitespace_only(self):
        self.assertEqual(summarize("   \n\t  \r\n "), {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_punctuation_only(self):
        self.assertEqual(summarize("...  ! ? () ::"), {"words": 0, "unique": 0, "avg_len": 0.0})

    def test_spec_example(self):
        # "Dog." and "dog" are the same word
        # "Dog." stripped -> "Dog" (len 3), "dog" stripped -> "dog" (len 3)
        res = summarize("Dog. dog")
        self.assertEqual(res, {"words": 2, "unique": 1, "avg_len": 3.0})

    def test_mixed(self):
        # "Hello, world! -- this is (a) test..."
        # Tokens: "Hello,", "world!", "--", "this", "is", "(a)", "test..."
        # Cleaned:
        # "Hello," -> "Hello" (len 5)
        # "world!" -> "world" (len 5)
        # "--" -> "--" (len 2) - note '-' is not in PUNCT ".,;:!?\"'()"
        # "this" -> "this" (len 4)
        # "is" -> "is" (len 2)
        # "(a)" -> "a" (len 1)
        # "test..." -> "test" (len 4)
        # Total words: 7
        # Unique: {"hello", "world", "--", "this", "is", "a", "test"} -> 7
        # Avg len: (5+5+2+4+2+1+4)/7 = 23/7 = 3.2857... -> 3.29
        text = "Hello, world! -- this is (a) test..."
        res = summarize(text)
        self.assertEqual(res, {"words": 7, "unique": 7, "avg_len": 3.29})

    def test_case_insensitivity_and_punct(self):
        # "The the THE (The) 'the'!"
        # All clean to "The" / "the" / "THE" / "The" / "the" -> len 3
        # 5 words, 1 unique, avg_len 3.0
        res = summarize("The the THE (The) 'the'!")
        self.assertEqual(res, {"words": 5, "unique": 1, "avg_len": 3.0})

    def test_punct_token_ignored(self):
        # "hello ... world"
        # "..." cleans to "" -> ignored
        # words: 2 ("hello", "world"), unique: 2, avg_len: 5.0
        res = summarize("hello ... world")
        self.assertEqual(res, {"words": 2, "unique": 2, "avg_len": 5.0})

    def test_multiple_whitespaces(self):
        res = summarize("  a \t\n b   \n\n c  ")
        self.assertEqual(res, {"words": 3, "unique": 3, "avg_len": 1.0})


if __name__ == "__main__":
    unittest.main()
