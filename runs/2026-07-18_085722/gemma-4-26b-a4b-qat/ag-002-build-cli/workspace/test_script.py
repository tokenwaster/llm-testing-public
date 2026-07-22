import subprocess

def run_test(file_content, expected_output):
    with open("test_input.txt", "w") as f:
        f.write(file_content)
    
    result = subprocess.run(["python3", "wordstats.py", "test_input.txt"], capture_output=True, text=True)
    
    if result.stdout.strip() == expected_output.strip():
        print(f"PASS\nInput:\n{file_content}\nExpected:\n{expected_output}\n")
    else:
        print(f"FAIL\nInput:\n{file_content}\nExpected:\n{expected_output}\nActual:\n{result.stdout}\n")

test_cases = [
    # Case 1: Simple file
    ("hello world\nhello again", "lines: 2\nwords: 4\ntop: hello 2"),
    
    # Case 2: Trailing newline
    ("hello world\nhello again\n", "lines: 2\nwords: 4\ntop: hello 2"),
    
    # Case 3: Punctuation and digits
    ("Hello, world! 123_test. This is a test.", "lines: 1\nwords: 7\ntop: test 2"),
    
    # Case 4: Ties (alphabetical)
    ("b a b a c", "lines: 1\nwords: 5\ntop: a 2"),
    ("b a a b c", "lines: 1\nwords: 5\ntop: a 2"),
    ("c b a", "lines: 1\nwords: 3\ntop: a 1"),
    
    # Case 5: No words
    ("123!@#_ \n456", "lines: 2\nwords: 0\ntop: - 0"),
    
    # Case 6: Empty file
    ("", "lines: 0\nwords: 0\ntop: - 0"),
    
    # Case 7: Case sensitivity and underscores
    ("Apple apple APPLE_pie", "lines: 1\nwords: 4\ntop: apple 3"),
]

for content, expected in test_cases:
    run_test(content, expected)
