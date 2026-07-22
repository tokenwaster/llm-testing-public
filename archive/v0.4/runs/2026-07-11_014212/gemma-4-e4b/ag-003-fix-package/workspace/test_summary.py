import textstats
import unittest

class TestTextStats(unittest.TestCase):

    def test_basic_summary(self):
        # Simple case, standard punctuation handling
        text = "Hello world. This is a test."
        expected = {"words": 5, "unique": 4, "avg_len": 3.2} # Hello (5), world (1), This (1), is (1), a (0) -> Wait, 'a' has length 1. Let's recalculate manually:
        # Words: Hello(5), world(5), This(4), is(2), a(1), test(4). Total words = 6. Unique: hello, world, this, is, a, test (6 unique if case matters) -> Case insensitive: {hello, world, this, is, a, test}. Wait, 'world.' and 'world' are the same word? No, they are separated by whitespace in the input text.
        # Input: "Hello world. This is a test."
        # Tokens (after fix): ['Hello', 'world.', 'This', 'is', 'a', 'test.'] -> 6 words
        # Cleaned: ['Hello', 'world', 'This', 'is', 'a', 'test']
        # Words list: ['Hello', 'world', 'This', 'is', 'a', 'test'] (Length 6)
        # Unique (lower): {'hello', 'world', 'this', 'is', 'a', 'test'} (Count 6)
        # Lengths: 5 + 5 + 4 + 2 + 1 + 4 = 21. Avg: 21 / 6 = 3.5.
        expected = {"words": 6, "unique": 6, "avg_len": 3.5}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        # Use assertAlmostEqual for float comparison due to rounding
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_whitespace_handling(self):
        # Test various whitespace types and multiple separators
        text = "Word1\tWord2 \n Word3"
        # Tokens: ['Word1', 'Word2', 'Word3'] -> 3 words. Unique: 3. Lengths: 5+5+5=15. Avg: 5.0
        expected = {"words": 3, "unique": 3, "avg_len": 5.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_case_insensitivity_and_punctuation(self):
        # Test case insensitivity and punctuation stripping
        text = "Dog. dog, DOG! (dog)"
        # Tokens: ['Dog.', 'dog,', 'DOG!', '(dog)'] -> 4 words
        # Cleaned: ['Dog', 'dog', 'DOG', 'dog']
        # Words list: ['Dog', 'dog', 'DOG', 'dog'] (Length 4)
        # Unique (lower): {'dog'} (Count 1)
        # Lengths: 3 + 3 + 3 + 3 = 12. Avg: 12 / 4 = 3.0
        expected = {"words": 4, "unique": 1, "avg_len": 3.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_pure_punctuation_filtering(self):
        # Test tokens that are only punctuation (should not count as words)
        text = "Hello... world! ? ; : ."
        # Tokens: ['Hello...', 'world!', '?', ';', ':', '.']
        # Cleaned: ['Hello', 'world', '', '', '', '']
        # Words list: ['Hello', 'world'] (Length 2)
        # Unique: {'hello', 'world'} (Count 2)
        # Lengths: 5 + 5 = 10. Avg: 10 / 2 = 5.0
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

    def test_only_punctuation_input(self):
        # Test input consisting only of punctuation (should result in 0 words)
        text = ".,;:!?\"'() "
        expected = {"words": 0, "unique": 0, "avg_len": 0.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

    def test_mixed_empty_and_punctuation(self):
        # Test a mix of empty strings and punctuation-only tokens
        text = "word1  ...   ? word2"
        # Tokens: ['word1', '...', '?', 'word2']
        # Cleaned: ['word1', '', '', 'word2']
        # Words list: ['word1', 'word2'] (Length 2)
        # Unique: {'word1', 'word2'} (Count 2)
        # Lengths: 5 + 5 = 10. Avg: 5.0
        expected = {"words": 2, "unique": 2, "avg_len": 5.0}
        result = textstats.summarize(text)
        self.assertEqual(result['words'], expected['words'])
        self.assertEqual(result['unique'], expected['unique'])
        self.assertAlmostEqual(result['avg_len'], expected['avg_len'], places=2)

if __name__ == '__main__':
    unittest.main()