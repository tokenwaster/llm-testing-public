import subprocess
import os

def run_test(filename, content, expected_output):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    result = subprocess.run(['python3', 'wordstats.py', filename], capture_output=True, text=True)
    actual_output = result.stdout.strip()
    expected_output_stripped = expected_output.strip()
    
    if actual_output == expected_output_stripped:
        print(f"PASS: {filename}")
    else:
        print(f"FAIL: {filename}")
        print(f"  Expected:\n{expected_output_stripped}")
        print(f"  Actual:\n{actual_output}")

if __name__ == "__main__":
    test_cases = [
        ("empty.txt", "", "lines: 0\nwords: 0\ntop: - 0"),
        ("newline.txt", "\n", "lines: 1\nwords: 0\ntop: - 0"),
        ("simple.txt", "Hello world\nHello again", "lines: 2\nwords: 4\ntop: hello 2"),
        ("punctuation.txt", "apple, banana; cherry! apple.", "lines: 1\nwords: 4\ntop: apple 2"),
        ("ties.txt", "b a b a", "lines: 1\nwords: 4\ntop: a 2"), # Wait, 'a' and 'b' both have count 2. Alphabetical tie-break: 'a' wins.
        ("digits_underscores.txt", "word1_word2 word3", "lines: 1\nwords: 3\ntop: word 1"), # Wait, let me re-read the definition of a word.
    ]
    # Re-reading definition: "A word is a maximal run of ASCII letters (a–z) after lowercasing the whole text. Digits, punctuation and underscores separate words."
    # So 'word1_word2' should be 'word', 'word'. 
    # Let me re-check my regex: r'[a-zA-Z]+'
    # If content is "word1_word2", findall(r'[a-zA-Z]+', "word1_word2") -> ['word', 'word']
    # So words count would be 2. Let me adjust my test case expectation.

    test_cases = [
        ("empty.txt", "", "lines: 0\nwords: 0\ntop: - 0"),
        ("newline.txt", "\n", "lines: 1\nwords: 0\ntop: - 0"),
        ("simple.txt", "Hello world\nHello again", "lines: 2\nwords: 4\ntop: hello 2"),
        ("punctuation.txt", "apple, banana; cherry! apple.", "lines: 1\nwords: 4\ntop: apple 2"),
        ("ties.txt", "b a b a", "lines: 1\nwords: 4\ntop: a 2"),
        ("digits_underscores.txt", "word1_word2 word3", "lines: 1\nwords: 3\ntop: word 1"), # Wait, 'word' appears twice in 'word1_word2'. Let me re-calculate.
    ]
    # In "word1_word2 word3":
    # words are ['word', 'word', 'word'] -> count is 3, top is 'word' 3.
    # Wait, let's be careful.
    # content: "word1_word2 word3"
    # findall(r'[a-zA-Z]+', "word1_word2 word3") -> ['word', 'word', 'word']
    # So words count is 3. top is 'word' 3.

    test_cases = [
        ("empty.txt", "", "lines: 0\nwords: 0\ntop: - 0"),
        ("newline.txt", "\n", "lines: 1\nwords: 0\ntop: - 0"),
        ("simple.txt", "Hello world\nHello again", "lines: 2\nwords: 4\ntop: hello 2"),
        ("punctuation.txt", "apple, banana; cherry! apple.", "lines: 1\nwords: 4\ntop: apple 2"),
        ("ties.txt", "b a b a", "lines: 1\nwords: 4\ntop: a 2"),
        ("digits_underscores.txt", "word1_word2 word3", "lines: 1\nwords: 3\ntop: word 3"),
    ]

    for filename, content, expected in test_cases:
        run_test(filename, content, expected)
    
    # Cleanup
    for filename, _, _ in test_cases:
        if os.path.exists(filename):
            os.remove(filename)
