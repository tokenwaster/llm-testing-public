import subprocess
import os

def run_wordstats(filepath):
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
            "name": "Single word",
            "content": "Hello",
            "expected": "lines: 1\nwords: 1\ntop: hello 1"
        },
        {
            "name": "Multiple words, different casing",
            "content": "Hello world HELLO",
            "expected": "lines: 1\nwords: 3\ntop: hello 2"
        },
        {
            "name": "Punctuation and digits",
            "content": "word1, word_2. word-3! word4",
            "expected": "lines: 1\nwords: 4\ntop: word 4"
        },
        {
            "name": "Trailing newline",
            "content": "line1\nline2\n",
            "expected": "lines: 2\nwords: 2\ntop: line 2"
        },
        {
            "name": "Ties in frequency",
            "content": "b a c b a",
            "expected": "lines: 1\nwords: 5\ntop: a 2"
        },
        {
            "name": "Only non-letters",
            "content": "123!@#_$%^&*()",
            "expected": "lines: 1\nwords: 0\ntop: - 0"
        },
        {
            "name": "Multiple lines with different words",
            "content": "First line\nSecond line\nThird line",
            "expected": "lines: 3\nwords: 6\ntop: line 3"
        }
    ]

    passed = 0
    for case in test_cases:
        # Create temporary file
        filename = "temp_test.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(case["content"])
        
        output = run_wordstats(filename)
        if output == case["expected"]:
            print(f"PASS: {case['name']}")
            passed += 1
        else:
            print(f"FAIL: {case['name']}")
            print(f"  Expected:\n{case['expected']}")
            print(f"  Got:\n{output}")
        
        if os.path.exists(filename):
            os.remove(filename)

    print(f"\nPassed {passed}/{len(test_cases)} tests.")
    if passed != len(test_cases):
        exit(1)

if __name__ == "__main__":
    test()
