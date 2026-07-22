import subprocess

def run_test(filename, content, expected):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    result = subprocess.run(['python3', 'wordstats.py', filename], capture_output=True, text=True)
    actual = result.stdout.strip()
    print(f"Testing {filename}:")
    print(f"Expected:\n{expected}")
    print(f"Actual:\n{actual}")
    assert actual == expected, f"Test failed for {filename}"
    print("Passed!")
    print("-" * 20)

# Test Case 1: Standard file
run_test('test1.txt', 'Hello world!\nHello again.', 'lines: 2\nwords: 4\ntop: hello 2')

# Test Case 2: Empty file
run_test('test2.txt', '', 'lines: 0\nwords: 0\ntop: - 0')

# Test Case 3: No words (only digits/punctuation)
run_test('test3.txt', '123 456\n!!! ???', 'lines: 2\nwords: 0\ntop: - 0')

# Test Case 4: Ties in frequency (alphabetical order)
run_test('test4.txt', 'apple banana apple banana cherry', 'lines: 1\nwords: 5\ntop: apple 2')

# Test Case 5: Trailing newline
run_test('test5.txt', 'line one\nline two\n', 'lines: 2\nwords: 4\ntop: line 2')

# Test Case 6: Only newlines
run_test('test6.txt', '\n\n', 'lines: 2\nwords: 0\ntop: - 0')
