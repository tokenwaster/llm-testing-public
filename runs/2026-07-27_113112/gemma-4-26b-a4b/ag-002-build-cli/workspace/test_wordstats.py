import os
import subprocess

def run_test(filename, content, expected_output):
    with open(filename, 'w') as f:
        f.write(content)
    
    result = subprocess.run(['python3', 'wordstats.py', filename], capture_output=True, text=True)
    actual_output = result.stdout.strip()
    expected_output = expected_output.strip()
    
    if actual_output == expected_output:
        print(f"PASS: {filename}")
    else:
        print(f"FAIL: {filename}")
        print(f"  Expected:\n{expected_output}")
        print(f"  Actual:\n{actual_output}")

test_cases = [
    ("empty.txt", "", "lines: 0\nwords: 0\ntop: - 0"),
    ("single.txt", "hello", "lines: 1\nwords: 1\ntop: hello 1"),
    ("newline.txt", "line1\nline2\n", "lines: 2\nwords: 2\ntop: line 2"),
    ("tie.txt", "b a", "lines: 1\nwords: 2\ntop: a 1"),
    ("complex_fixed.txt", "Hello, world! 123_test. This is a test.", "lines: 1\nwords: 7\ntop: test 2"),
    ("multi_line.txt", "Line one\nLine two\nLine three", "lines: 3\nwords: 6\ntop: line 3"),
]

for filename, content, expected in test_cases:
    run_test(filename, content, expected)

# Clean up
for filename, _, _ in test_cases:
    if os.path.exists(filename):
        os.remove(filename)
