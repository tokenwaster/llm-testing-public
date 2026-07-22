"""
solution.py

Run-length encoding utilities.

Functions
---------
encode(text: str) -> str
    Compress runs of repeated characters into "<count><char>" format.
decode(encoded: str) -> str
    Expand an encoded string back to its original form.

Both functions treat input as case‑sensitive and handle empty strings.
"""

from __future__ import annotations


def encode(text: str) -> str:
    """
    Encode ``text`` using run‑length encoding.

    Each maximal run of the same character is replaced by the length of the
    run followed by the character itself.  Single characters are encoded with
    a count of ``1``.

    Parameters
    ----------
    text: str
        The string to encode.  May be empty and contains only letters
        (a‑z, A‑Z).  The function is case‑sensitive.

    Returns
    -------
    str
        The encoded representation.  ``encode("")`` returns ``""``.
    """
    if not text:
        return ""

    parts: list[str] = []
    prev = text[0]
    count = 1

    for ch in text[1:]:
        if ch == prev:
            count += 1
        else:
            parts.append(str(count))
            parts.append(prev)
            prev = ch
            count = 1

    # Append the final run
    parts.append(str(count))
    parts.append(prev)

    return "".join(parts)


def decode(encoded: str) -> str:
    """
    Decode a run‑length encoded string.

    The function expects a sequence of ``<count><char>`` pairs where
    ``count`` may consist of one or more decimal digits.  It raises
    ``ValueError`` if the format is invalid.

    Parameters
    ----------
    encoded: str
        The encoded string.  May be empty.

    Returns
    -------
    str
        The original uncompressed string.
    """
    if not encoded:
        return ""

    result: list[str] = []
    i = 0
    n = len(encoded)

    while i < n:
        # Extract the numeric count
        j = i
        while j < n and encoded[j].isdigit():
            j += 1
        if j == i:
            raise ValueError("Invalid encoded string: expected a digit at position {}".format(i))

        count = int(encoded[i:j])

        if j >= n:
            raise ValueError("Invalid encoded string: missing character after count at position {}".format(j))

        char = encoded[j]
        result.append(char * count)

        i = j + 1

    return "".join(result)


__all__ = ["encode", "decode"]
