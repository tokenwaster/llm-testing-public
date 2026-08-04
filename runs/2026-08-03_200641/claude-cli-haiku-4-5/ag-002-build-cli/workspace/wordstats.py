import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python wordstats.py <path-to-text-file>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Count lines (trailing newline does not add an extra line)
    lines_count = content.count('\n')
    if content and not content.endswith('\n'):
        lines_count += 1

    # Extract words: maximal run of ASCII letters after lowercasing
    content_lower = content.lower()
    words = re.findall(r'[a-z]+', content_lower)
    words_count = len(words)

    # Find most frequent word (ties broken alphabetically - earliest wins)
    if words:
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by count (descending), then by word (ascending for tie-breaking)
        top_word = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))[0]
        top_word_str = f"{top_word[0]} {top_word[1]}"
    else:
        top_word_str = "- 0"

    print(f"lines: {lines_count}")
    print(f"words: {words_count}")
    print(f"top: {top_word_str}")

if __name__ == "__main__":
    main()
