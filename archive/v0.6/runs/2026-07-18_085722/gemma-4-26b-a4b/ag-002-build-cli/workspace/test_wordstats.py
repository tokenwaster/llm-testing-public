import subprocess
import os

def run_script(filepath):
    result = subprocess.run(['python3', 'wordstats.py', filepath], capture_output=True, text=True)
    return result.stdout.strip()

def test():
    test_cases = [
        {
            "name": "Empty file",
            "content": "",
            "expected": "lines: 0\nwords: 0\ntop: - 0"
        },
        {
            "name": "Single line, single word",
            "content": "Hello",
            "expected": "lines: 1\nwords: 1\ntop: hello 1"
        },
        {
            "name": "Multiple lines and words",
            "content": "Hello world!\nThis is a test.\nTest, test, test.",
            "expected": "lines: 3\nwords: 9\ntop: test 4"
        },
        {
            "name": "Tie breaking (alphabetical)",
            "content": "b a b a",
            "expected": "lines: 1\nwords: 4\ntop: a 2"
        },
        {
            "name": "Digits and punctuation",
            "content": "word1_word2.word3!word4",
            "expected": "lines: 1\nwords: 4\ntop: word 4"
        },
        {
            "name": "Trailing newline doesn't add line",
            "content": "line1\nline2\n",
            "expected": "lines: 2\nwords: 2\ntop: line 2"
        }
    ]

    for case in test_cases:
        filename = "test_case.txt"
        with open(filename, "w") as f:
            f.write(case["content"])
        
        output = run_script(filename)
        print(f"Testing {case['name']}...")
        if output == case["expected"]:
            print("  PASSED")
        else:
            print(f"  FAILED")
            print(f"    Expected:\n{case['expected']}")
            print(f"    Got:\n{output}")
        
        os.remove(filename)

if __name__ == "__main__":
    test()
