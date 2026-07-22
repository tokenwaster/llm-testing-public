import subprocess
import os

def run_script(filepath):
    result = subprocess.run(['python3', 'wordstats.py', filepath], capture_output=True, text=True)
    return result.stdout.strip()

def test():
    test_files = {
        "empty.txt": "",
        "one_word.txt": "Hello",
        "multiple_words.txt": "Hello world! Hello again.",
        "punctuation.txt": "abc, def; ghi_jkl 123 mno",
        "ties.txt": "b a b a c",
        "trailing_newline.txt": "line1\nline2\n",
        "only_non_letters.txt": "123!@#_$%^&*()"
    }

    for filename, content in test_files.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        output = run_script(filename)
        print(f"Testing {filename}:")
        print(f"Content: {repr(content)}")
        print(f"Output:\n{output}")
        print("-" * 20)

        # Verification logic
        if filename == "empty.txt":
            assert output == "lines: 0\nwords: 0\ntop: - 0"
        elif filename == "one_word.txt":
            assert output == "lines: 1\nwords: 1\ntop: hello 1"
        elif filename == "multiple_words.txt":
            assert output == "lines: 1\nwords: 4\ntop: hello 2"
        elif filename == "punctuation.txt":
            assert output == "lines: 1\nwords: 5\ntop: abc 1"
        elif filename == "ties.txt":
            assert output == "lines: 1\nwords: 5\ntop: a 2"
        elif filename == "trailing_newline.txt":
            # content = "line1\nline2\n" -> words are ["line", "line"]
            assert output == "lines: 2\nwords: 2\ntop: line 2"
        elif filename == "only_non_letters.txt":
            assert output == "lines: 1\nwords: 0\ntop: - 0"

    print("All tests passed!")

if __name__ == "__main__":
    test()
