import subprocess
import os

def run_tool(file_path):
    result = subprocess.run(['python3', 'wordstats.py', file_path], capture_output=True, text=True)
    return result.stdout.strip()

def test():
    # Test 1: Simple text
    with open('test1.txt', 'w') as f:
        f.write("Hello world\nHello again")
    res1 = run_tool('test1.txt')
    expected1 = "lines: 2\nwords: 4\ntop: hello 2"
    assert res1 == expected1, f"Test 1 failed: expected {repr(expected1)}, got {repr(res1)}"

    # Test 2: Punctuation and numbers
    with open('test2.txt', 'w') as f:
        f.write("Hello, world! 123_abc...def")
    res2 = run_tool('test2.txt')
    expected2 = "lines: 1\nwords: 4\ntop: abc 1"
    assert res2 == expected2, f"Test 2 failed: expected {repr(expected2)}, got {repr(res2)}"

    # Test 3: Empty file
    with open('test3.txt', 'w') as f:
        f.write("")
    res3 = run_tool('test3.txt')
    expected3 = "lines: 0\nwords: 0\ntop: - 0"
    assert res3 == expected3, f"Test 3 failed: expected {repr(expected3)}, but got {repr(res3)}"

    # Test 4: Only non-word characters
    with open('test4.txt', 'w') as f:
        f.write("123 !!! ___ ---")
    res4 = run_tool('test4.txt')
    expected4 = "lines: 1\nwords: 0\ntop: - 0"
    assert res4 == expected4, f"Test 4 failed: expected {repr(expected4)}, got {repr(res4)}"

    # Test 5: Tie breaking (alphabetical)
    with open('test5.txt', 'w') as f:
        f.write("b a c b a")
    res5 = run_tool('test5.txt')
    expected5 = "lines: 1\nwords: 5\ntop: a 2"
    assert res5 == expected5, f"Test 5 failed: expected {repr(expected5)}, got {repr(res5)}"

    print("All tests passed!")

if __name__ == "__main__":
    # Clean up previous runs if any
    for f in ['test1.txt', 'test2.txt', 'test3.txt', 'test4.txt', 'test5.txt']:
        if os.path.exists(f):
            os.remove(f)

    try:
        test()
    finally:
        # Clean up after tests
        for f in ['test1.txt', 'test2.txt', 'test3.txt', 'test4.txt', 'test5.txt']:
            if os.path.exists(f):
                os.remove(f)
