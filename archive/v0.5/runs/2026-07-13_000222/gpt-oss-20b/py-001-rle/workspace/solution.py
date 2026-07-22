# solution.py

import re
from typing import List


def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char>.

    Parameters
    ----------
    text : str
        Input string consisting only of letters (a-z, A-Z).

    Returns
    -------
    str
        Run‑length encoded representation.
    """
    if not text:
        return ""

    result: List[str] = []
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
    Decode a run‑length encoded string back to its original form.

    Parameters
    ----------
    encoded : str
        Encoded string where counts may be multi‑digit.

    Returns
    -------
    str
        Decoded original string.
    """
    if not encoded:
        return ""

    # Use regex to find all occurrences of a number followed by a letter
    pattern = re.compile(r"(\d+)([A-Za-z])")
    parts = pattern.findall(encoded)

    decoded_parts: List[str] = []
    for count_str, char in parts:
        decoded_parts.append(char * int(count_str))

    return "".join(decoded_parts)
