# solution.py

import re
from typing import List


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
        Run‑length encoded representation.
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
    Decode a run‑length encoded string back to its original form.

    Parameters
    ----------
    encoded : str
        Encoded string produced by `encode`. May be empty.

    Returns
    -------
    str
        Decoded original string.
    """
    if not encoded:
        return ""

    # Use regex to find all occurrences of <digits><letter>
    pattern = re.compile(r"(\d+)([a-zA-Z])")
    decoded_parts: List[str] = []

    for count_str, char in pattern.findall(encoded):
        decoded_parts.append(char * int(count_str))

    return "".join(decoded_parts)
