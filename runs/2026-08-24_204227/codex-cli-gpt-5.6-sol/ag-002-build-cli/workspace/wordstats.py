import re
import sys
from collections import Counter
from pathlib import Path


def main() -> None:
    text = Path(sys.argv[1]).read_text()
    line_count = text.count("\n") + int(bool(text) and not text.endswith("\n"))
    counts = Counter(re.findall(r"[a-z]+", text.lower(), flags=re.ASCII))

    if counts:
        top_word, top_count = min(counts.items(), key=lambda item: (-item[1], item[0]))
    else:
        top_word, top_count = "-", 0

    print(f"lines: {line_count}")
    print(f"words: {sum(counts.values())}")
    print(f"top: {top_word} {top_count}")


if __name__ == "__main__":
    main()
