import sys
import re


def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Count lines: split by newline. A trailing final newline does not add an
    # extra line, which is exactly what str.splitlines(True) or counting '\n'
    # gives us. But more straightforward: count newline characters.
    if content == "":
        line_count = 0
    elif content[-1] == "\n":
        # The last newline doesn't create an extra line
        line_count = content.count("\n")
    else:
        line_count = content.count("\n") + 1

    # Lowercase the whole text
    lower_content = content.lower()

    # Extract words: maximal run of ASCII letters a-z
    words = re.findall(r"[a-z]+", lower_content)

    total_words = len(words)

    if total_words == 0:
        print(f"lines: {line_count}")
        print(f"words: {total_words}")
        print("top: - 0")
        return

    # Count frequencies
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1

    # Find top: ties broken alphabetically (earliest/smallest word wins)
    max_count = max(freq.values())
    # Among words with max_count, pick the alphabetically smallest
    top_word = min(w for w, c in freq.items() if c == max_count)

    print(f"lines: {line_count}")
    print(f"words: {total_words}")
    print(f"top: {top_word} {max_count}")


if __name__ == "__main__":
    main()