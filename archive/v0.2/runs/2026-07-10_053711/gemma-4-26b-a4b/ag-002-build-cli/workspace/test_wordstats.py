import subprocess
import os

def run_test(filename, expected_output):
    print(f"Testing file: {filename}")
    try:
        result = subprocess.run(['python3', 'wordstats.py', filename], capture_output=True, text=True)
        actual_output = result.stdout.strip()
        if actual_output == expected_output.strip():
            print(f"PASS\n  Expected:\n{expected_output}\n  Actual:\n{actual_output}")
        else:
            print(f"FAIL\n  Expected:\n{expected_output}\n  Actual:\n{actual_output}")
    except Exception as e:
        print(f"Error running test on {filename}: {e}")

def create_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    # Test 1: Empty file
    create_file('test1.txt', '')
    run_test('test1.txt', "lines: 0\nwords: 0\ntop: - 0")

    # Test 2: Single line, no words (only digits/punctuation)
    create_file('test2.txt', '123!@#_')
    run_test('test2.txt', "lines: 1\nwords: 0\ntop: - 0")

    # Test 3: Multiple lines, words and punctuation
    create_file('test3.txt', 'Hello world!\nThis is a test.\nTesting, testing, 1, 2, 3.')
    # Words (letters only): hello, world, this, is, a, test, testing, testing
    # Total words: 8
    # Top: testing 2
    run_test('test3.txt', "lines: 3\nwords: 8\ntop: testing 2")

    # Test 4: Ties in word frequency (alphabetical tie-break)
    create_file('test4.txt', 'b a b a')
    # Lines: 1
    # Words: b, a, b, a
    # Counts: a: 2, b: 2
    # Top: a 2 (a comes before b)
    run_test('test4.txt', "lines: 1\nwords: 4\ntop: a 2")

    # Test 5: Trailing newline and digits as separators
    create_file('test5.txt', 'line1\nline2\n')
    # Words (letters only): line, line
    # Total words: 2
    # Top: line 2
    run_test('test5.txt', "lines: 2\nwords: 2\ntop: line 2")

    # Test 6: Underscores and digits as separators
    create_file('test6.txt', 'word_one1two')
    # Words: word, one, two
    run_test('test6.txt', "lines: 1\nwords: 3\ntop: one 1")

    # Cleanup
    for i in range(1, 7):
        if os.path.exists(f'test{i}.txt'):
            os.remove(f'test{i}.txt')
