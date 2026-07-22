import subprocess
import os

def run_test(input_content, expected_output):
    test_file = "test_input.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(input_content)
    
    try:
        result = subprocess.run(["python3", "wordstats.py", test_file], capture_output=
True, text=True)
        actual_output = result.stdout.strip()
        expected_output = expected_output.strip()
        
        if result.returncode != 0:
            print(f"FAIL: Command returned non-zero exit code {result.returncode}")
            print(f"Stderr: {result.stderr}")
            return False

        if actual_output == expected_output:
            print(f"PASS: Input:\n{repr(input_content)}\nExpected:\n{expected_output}\nActual:\n{actual_output}")
            return True
        else:
            print(f"FAIL: Input:\n{repr(input_content)}\nExpected:\n{expected_output}\nActual:\n{actual_output}")
            return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
    return True

def main():
    tests = [
        ("", "lines: 0\nwords: 0\ntop: - 0"),
        ("hello", "lines: 1\nwords: 1\ntop: hello 1"),
        ("Hello, world!\nWorld is great.", "lines: 2\nwords: 5\ntop: world 2"),
        ("apple banana apple cherry banana", "lines: 1\nwords: 5\ntop: apple 2"),
        ("zebra alpha zebra alpha", "lines: 1\nwords: 4\ntop: alpha 2"),
        ("123_abc!def", "lines: 1\nwords: 2\ntop: abc 1"),
        ("   ", "lines: 1\nwords: 0\ntop: - 0"),
        ("\n\n", "lines: 2\nwords: 0\ntop: - 0"),
    ]

    all_passed = True
    for i, (input_content, expected) in enumerate(tests):
        if not run_test(input_content, expected):
            all_passed = False
            print(f"Test case {i} failed.")
    
    if all_passed:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed.")

if __name__ == "__main__":
    main()
