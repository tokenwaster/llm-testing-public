import subprocess

def run_test(file_content, expected_output):
    with open("test_input.txt", "w") as f:
        f.write(file_content)
    
    result = subprocess.run(["python3", "wordstats.py", "test_input.txt"], capture_output=True, text=True)
    
    if result.stdout.strip() == expected_output.strip():
        print(f"PASS\nInput:\n{file_content}\nExpected:\n{expected_output}\n")
    else:
        print(f"FAIL\nInput:\n{file_content}\nExpected:\n{expected_output}\nActual:\n{result.stdout}")

# Test 1: Normal text
run_test(
    "Hello world!\nHello again.",
    "lines: 2\nwords: 4\ntop: hello 2"
)

# Test 2: Case sensitivity and punctuation
run_test(
    "Apple, apple, APPLE! 123_banana",
    "lines: 1\nwords: 4\ntop: apple 3"
)

# Test 3: Ties in word counts (alphabetical tie-break)
run_test(
    "b a b a c c",
    "lines: 1\nwords: 6\ntop: a 2"
)

# Test 4: Empty file
run_test(
    "",
    "lines: 0\nwords: 0\ntop: - 0"
)

# Test 5: File with no words (only digits/punctuation)
run_test(
    "123 !!! ___",
    "lines: 1\nwords: 0\ntop: - 0"
)

# Test 6: Trailing newline and digits
run_test(
    "line1\nline2\n",
    "lines: 2\nwords: 2\ntop: line 2"
)

# Test 7: Mixed characters
run_test(
    "a-b_c.d!e",
    "lines: 1\nwords: 5\ntop: a 1"
)
