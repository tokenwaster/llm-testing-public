# solution.py

import re
from typing import Tuple


def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char>.

    Parameters
    ----------
    text : str
        Input string containing only letters (a-z, A-Z). May be empty.

    Returns
    -------
    str
        Run-length encoded representation. Single characters are prefixed with '1'.
    """
    if not text:
        return ""

    result = []
    current_char = text[0]
    count = 1

    for ch in text[1:]:
        if ch == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = ch
            count = 1

    # Append the last run
    result.append(f"{count}{current_char}")

    return "".join(result)


def _parse_encoded(encoded: str) -> Tuple[int, str]:
    """
    Helper to parse a single <count><char> segment from the encoded string.

    Returns a tuple (count, char). Assumes input is valid.
    """
    # Find where digits end and letter begins
    i = 0
    while i < len(encoded) and encoded[i].isdigit():
        i += 1
    count_str = encoded[:i]
    char = encoded[i] if i < len(encoded) else ""
    return int(count_str), char


def decode(encoded: str) -> str:
    """
    Decode a run-length encoded string back to the original text.

    Parameters
    ----------
    encoded : str
        Encoded string produced by `encode`. May be empty.

    Returns
    -------
    str
        Original uncompressed string.
    """
    if not encoded:
        return ""

    result = []
    i = 0
    n = len(encoded)

    while i < n:
        # Extract digits for count
        j = i
        while j < n and encoded[j].isdigit():
            j += 1

        count_str = encoded[i:j]
        if not count_str:
            raise ValueError("Invalid encoding: missing count")
        count = int(count_str)

        if j >= n:
            raise ValueError("Invalid encoding: missing character after count")

        char = encoded[j]
        result.append(char * count)
        i = j + 1

    return "".join(result)


# If run as a script, perform simple tests
if __name__ == "__main__":
    test_strings = ["", "a", "aaabcc", "abcABC", "zzZZz"]
    for s in test_strings:
        enc = encode(s)
        dec = decode(enc)
        assert dec == s, f"Failed round-trip: {s} -> {enc} -> {dec}"
    print("All tests passed.")
