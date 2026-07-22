import textstats
import unittest

class TestTextStats(unittest.TestCase):
    def test_basic_summary(self):
        # Standard case: "Hello world, this is a test."
        text = "Hello world, this is a test."
        expected = {"words": 5, "unique": 4, "avg_len": 4.2} # Hello (5), world (1), this (1), is (1), a (1), test (1). Unique: hello, world, this, is, a, test -> 6 unique? Wait, punctuation stripping changes things.
        # Words: "Hello", "world,", "this", "is", "a", "test."
        # Cleaned: ["hello", "world", "this", "is", "a", "test"] (Assuming clean handles case and punctuation)
        # Let's trace manually based on the specification rules.
        # 1. Tokenize: ["Hello", "world,", "this", "is", "a", "test."]
        # 2. Clean: ["Hello", "world", "this", "is", "a", "test"] (Assuming clean strips punctuation but keeps case for now, though the unique count must be case-insensitive later)
        # The implementation uses `clean(t)` which only strips surrounding punctuation. Let's assume it returns the stripped string.
        # Tokens: ["Hello", "world,", "this", "is", "a", "test."]
        # Cleaned (after stripping): ["Hello", "world", "this", "is", "a", "test"]
        # Words list: ["Hello", "world", "this", "is", "a", "test"] -> 6 words.
        # Unique (case-insensitive): {"hello", "world", "this", "is", "a", "test"} -> 6 unique.
        # Lengths: 5+5+4+2+1+4 = 21. Avg len: 21/6 = 3.5.
        
        # Let's use a simpler example to verify the logic flow based on my fixed code structure.
        text_simple = "Word one, word two! Word One."
        # Tokens: ["Word", "one,", "word", "two!", "Word", "One."]
        # Cleaned: ["Word", "one", "word", "two", "Word", "One"] (6 words)
        # Unique lower: {"word", "one", "two"} -> 3 unique.
        # Lengths: 4+3+4+3+4+3 = 21. Avg len: 21/6 = 3.5.
        expected_simple = {"words": 6, "unique": 3, "avg_len": 3.5}
        result = textstats.summarize(text_simple)
        self.assertEqual(result['words'], expected_simple['words'])
        self.assertEqual(result['unique'], expected_simple['unique'])
        # Use assertAlmostEqual for float comparison due to rounding
        self.assertAlmostEqual(result['avg_len'], expected_simple['avg_len'], places=2)

    def test_whitespace_handling(self):
        # Test various whitespace separators (spaces, tabs, newlines, multiple in a row)
        text = "Word1\t Word2 \n Word3"
        # Tokens: ["Word1", "Word2", "Word3"] -> 3 words. Unique: 3. Lengths: 5+5+5=15. Avg len: 5.0
        expected = {"words": 3, "unique": 3, "avg_len": 5.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_punctuation_and_case_insensitivity(self):
        # Test unique count and word definition based on punctuation stripping/casing
        text = "Dog. dog, DOG! (dog)"
        # Tokens: ["Dog.", "dog,", "DOG!", "(dog)"]
        # Cleaned: ["Dog", "dog", "DOG", "dog"] -> 4 words.
        # Unique lower: {"dog"} -> 1 unique.
        # Lengths: 3+3+3+3 = 12. Avg len: 12/4 = 3.0.
        expected = {"words": 4, "unique": 1, "avg_len": 3.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_only_punctuation_tokens(self):
        # Test tokens that are only punctuation (should not count as words)
        text = "Hello... world! ? ;"
        # Tokens: ["Hello...", "world!", "?", ";"]
        # Cleaned: ["Hello", "world", "", ""] -> Filtered to ["Hello", "world"]. 2 words.
        # Unique lower: {"hello", "world"} -> 2 unique.
        # Lengths: 5+5 = 10. Avg len: 10/2 = 5.0.
        expected = {"words": 2, "unique": 2, "avg_len": 5.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_empty_input(self):
        # Test empty string input
        text = ""
        expected = {"words": 0, "unique": 0, "avg_len": 0.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_only_whitespace(self):
        # Test input with only whitespace
        text = " \t \n "
        expected = {"words": 0, "unique": 0, "avg_len": 0.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)