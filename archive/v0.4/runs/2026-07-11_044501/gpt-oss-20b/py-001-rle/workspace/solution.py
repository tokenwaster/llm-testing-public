# solution.py

def encode(text: str) -> str:
    """
    Encode a string using run-length encoding.
    Each run of repeated characters is replaced by <count><char>.
    Single characters are encoded with count 1.

    Parameters
    ----------
    text : str
        Input string containing only letters (a-z, A-Z).

    Returns
    -------
    str
        Run‑length encoded representation.
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
    Decode a run-length encoded string back to its original form.
    Counts may be multi‑digit.

    Parameters
    ----------
    encoded : str
        Run‑length encoded string produced by `encode`.

    Returns
    -------
    str
        Decoded original string.
    """
    if not encoded:
        return ""

    result = []
    i = 0
    n = len(encoded)

    while i < n:
        # Parse the count (one or more digits)
        start = i
        while i < n and encoded[i].isdigit():
            i += 1
        count_str = encoded[start:i]
        if not count_str:  # Should never happen for valid input
            raise ValueError("Invalid encoding: missing count")
        count = int(count_str)

        if i >= n:
            raise ValueError("Invalid encoding: missing character after count")

        char = encoded[i]
        result.append(char * count)
        i += 1

    return "".join(result)
