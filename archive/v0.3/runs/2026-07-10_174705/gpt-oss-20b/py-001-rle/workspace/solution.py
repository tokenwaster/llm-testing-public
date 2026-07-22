# solution.py

import re
from typing import List


def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char> format.
    Example: "aaabcc" -> "3a1b2c".
    Empty string returns empty string.
    """
    if not text:
        return ""

    result: List[str] = []
    count = 1
    prev_char = text[0]

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
    Decode a string encoded by `encode`.
    Counts may be multi-digit.
    Example: "12a" -> "aaaaaaaaaaaa".
    Empty string returns empty string.
    """
    if not encoded:
        return ""

    # Pattern matches one or more digits followed by a single character
    pattern = re.compile(r'(\d+)([A-Za-z])')
    parts = pattern.findall(encoded)

    # Validate that the entire string was matched
    reconstructed = "".join(f"{cnt}{ch}" for cnt, ch in parts)
    if reconstructed != encoded:
        raise ValueError("Invalid encoded format")

    decoded_parts: List[str] = [int(cnt) * ch for cnt, ch in parts]
    return "".join(decoded_parts)


# The following tests are only executed when running this file directly.
if __name__ == "__main__":
    # Basic sanity checks
    assert encode("") == ""
    assert decode("") == ""

    test_strings = [
        "a",
        "aaabcc",
        "abc",
        "AaaBBBcC",
        "zzZZZzz",
        "x" * 12 + "y" * 3,
    ]

    for s in test_strings:
        enc = encode(s)
        dec = decode(enc)
        assert dec == s, f"Failed round-trip: {s} -> {enc} -> {dec}"
    print("All tests passed.")
