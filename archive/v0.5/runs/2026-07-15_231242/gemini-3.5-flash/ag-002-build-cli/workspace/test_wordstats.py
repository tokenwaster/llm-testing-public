import unittest
import subprocess
import os

class TestWordStats(unittest.TestCase):
    def run_tool(self, content):
        with open("temp_test.txt", "w", encoding="utf-8") as f:
            f.write(content)
        res = subprocess.run(["python", "wordstats.py", "temp_test.txt"], capture_output=True, text=True)
        if os.path.exists("temp_test.txt"):
            os.remove("temp_test.txt")
        return res.stdout

    def test_empty(self):
        out = self.run_tool("")
        self.assertEqual(out, "lines: 0\nwords: 0\ntop: - 0\n")

    def test_single_newline(self):
        out = self.run_tool("\n")
        self.assertEqual(out, "lines: 1\nwords: 0\ntop: - 0\n")

    def test_two_newlines(self):
        out = self.run_tool("\n\n")
        self.assertEqual(out, "lines: 2\nwords: 0\ntop: - 0\n")

    def test_no_newline(self):
        out = self.run_tool("hello")
        self.assertEqual(out, "lines: 1\nwords: 1\ntop: hello 1\n")

    def test_trailing_newline(self):
        out = self.run_tool("hello\n")
        self.assertEqual(out, "lines: 1\nwords: 1\ntop: hello 1\n")

    def test_multiple_lines(self):
        out = self.run_tool("hello\nworld")
        self.assertEqual(out, "lines: 2\nwords: 2\ntop: hello 1\n")

    def test_multiple_lines_trailing(self):
        out = self.run_tool("hello\nworld\n")
        self.assertEqual(out, "lines: 2\nwords: 2\ntop: hello 1\n")

    def test_ties(self):
        out = self.run_tool("b a b a")
        self.assertEqual(out, "lines: 1\nwords: 4\ntop: a 2\n")

    def test_non_ascii_and_digits(self):
        out = self.run_tool("hello_world 123abc456def!!!")
        # words: hello, world, abc, def (4 words)
        self.assertEqual(out, "lines: 1\nwords: 4\ntop: abc 1\n")

if __name__ == "__main__":
    unittest.main()
