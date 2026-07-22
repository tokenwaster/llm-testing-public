# solution.py

import re
from typing import List


def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char> format.
    Example: "aaabcc" -> "3a1b2c"
    Empty string returns empty string.
    """
    if not text:
        return ""

    result = []
    prev_char = text[0]
    count = 1

    for ch in text[1:]:
        if ch == prev_char:
            count += 1
        else:
            result.append(f"{count}{prev_char}")
            prev_char = ch
            count = 1

    # Append the last run
    result.append(f"{count}{prev_char}")

    return "".join(result)


def decode(encoded: str) -> str:
    """
    Decode a string encoded by encode().
    Counts may be multi-digit.
    Example: "3a1b2c" -> "aaabcc"
    Empty string returns empty string.
    """
    if not encoded:
        return ""

    # Pattern matches one or more digits followed by a single character
    pattern = re.compile(r'(\d+)([A-Za-z])')
    parts: List[str] = []

    for count_str, char in pattern.findall(encoded):
        count = int(count_str)
        parts.append(char * count)

    return "".join(parts)


# Basic sanity check (can be removed or commented out in production)
if __name__ == "__main__":
    test_strings = ["", "a", "aaabcc", "XYZ", "12a3b"]
    for s in test_strings:
        encoded = encode(s)
        decoded = decode(encoded)
        assert decoded == s, f"Failed on {s}"
    print("All tests passed.")
