import subprocess
import os
import sys

def test_wordstats():
    test_cases = [
        {
            "name": "normal",
            "content": "Hello world!\nThis is a test.\nHello again, world.",
            "expected": "lines: 3\nwords: 9\ntop: hello 2"
        },
        {
            "name": "empty",
            "content": "",
            "expected": "lines: 0\nwords: 0\ntop: - 0"
        },
        {
            "name": "no_words",
            "content": "123 456\n!!! ???\n___",
            "expected": "lines: 3\nwords: 0\ntop: - 0"
        },
        {
            "name": "trailing_newline",
            "content": "Line 1\nLine 2\n",
            "expected": "lines: 2\nwords: 2\ntop: line 2"
        },
        {
            "name": "tie_break",
            "content": "Apple Banana Apple Banana Cherry",
            "expected": "lines: 1\nwords: 5\ntop: apple 2"
        }
    ]

    for case in test_cases:
        filename = f"test_{case['name']}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(case['content'])
        
        result = subprocess.run([sys.executable, 'wordstats.py', filename], capture_output=True, text=True)
        actual = result.stdout.strip()
        
        if actual == case['expected']:
            print(f"Test {case['name']}: PASSED")
        else:
            print(f"Test {case['name']}: FAILED")
            print(f"  Expected:\n{case['expected']}")
            print(f"  Actual:\n{actual}")
        
        os.remove(filename)

if __name__ == "__main__":
    test_wordstats()
