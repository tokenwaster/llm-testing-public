# solution.py

import re
from typing import Tuple


def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char> format.
    Example: "aaabcc" -> "3a1b2c"
    Empty string returns empty string.
    """
    if not text:
        return ""

    result = []
    count = 1
    prev_char = text[0]

    for char in text[1:]:
        if char == prev_char:
            count += 1
        else:
            result.append(f"{count}{prev_char}")
            prev_char = char
            count = 1

    # Append the last run
    result.append(f"{count}{prev_char}")

    return "".join(result)


def _parse_pair(encoded: str, index: int) -> Tuple[int, str, int]:
    """
    Parse a <count><char> pair starting at position `index` in `encoded`.
    Returns (count, char, new_index).
    Raises ValueError if the format is invalid.
    """
    # Extract digits for count
    start = index
    while index < len(encoded) and encoded[index].isdigit():
        index += 1

    if start == index:
        raise ValueError(f"Expected digit at position {start} in '{encoded}'")

    count_str = encoded[start:index]
    count = int(count_str)

    if index >= len(encoded):
        raise ValueError(f"Missing character after count at position {index} in '{encoded}'")

    char = encoded[index]
    index += 1

    return count, char, index


def decode(encoded: str) -> str:
    """
    Decode a string produced by encode().
    Counts may be multi-digit. Empty string returns empty string.
    Raises ValueError for malformed input.
    """
    if not encoded:
        return ""

    result = []
    i = 0
    while i < len(encoded):
        count, char, i = _parse_pair(encoded, i)
        result.append(char * count)

    return "".join(result)


# If this module is run directly, perform a simple sanity check.
if __name__ == "__main__":
    test_strings = ["", "a", "aaabcc", "XYZ", "12a3b"]
    for s in test_strings:
        encoded = encode(s)
        decoded = decode(encoded)
        assert decoded == s, f"Failed round-trip: {s} -> {encoded} -> {decoded}"
    print("All tests passed.")
