import subprocess
import os

def run_script(filename):
    result = subprocess.run(['python', 'wordstats.py', filename], capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def test():
    tests = [
        {
            "name": "Standard",
            "content": "Hello, World!\nThis is a test_of the wordstats tool.\nabc abc def def\n",
            "expected": "lines: 3\nwords: 14\ntop: abc 2"
        },
        {
            "name": "No words",
            "content": "123!@#$%\n   \n",
            "expected": "lines: 2\nwords: 0\ntop: - 0"
        },
        {
            "name": "Single word",
            "content": "word\n",
            "expected": "lines: 1\nwords: 1\ntop: word 1"
        },
        {
            "name": "Tie breaking",
            "content": "b a c\n",
            "expected": "lines: 1\nwords: 3\ntop: a 1"
        },
        {
            "name": "Empty file",
            "content": "",
            "expected": "lines: 0\nwords: 0\ntop: - 0"
        }
    ]

    for test in tests:
        filename = f"test_{test['name'].replace(' ', '_')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test['content'])
        
        out, code = run_script(filename)
        if out == test['expected']:
            print(f"PASS: {test['name']}")
        else:
            print(f"FAIL: {test['name']}\n  Expected:\n{test['expected']}\n  Got:\n{out}")
        os.remove(filename)

if __name__ == "__main__":
    test()
