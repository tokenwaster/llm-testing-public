def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char>.
    Example: encode("aaabcc") returns "3a1b2c".
    Single characters get count 1. Empty input returns empty string.
    Input contains only letters (a-z, A-Z); encoding is case-sensitive.
    """
    if not text:
        return ""
    result = []
    count = 1
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            result.append(f"{count}{text[i - 1]}")
            count = 1
    result.append(f"{count}{text[-1]}")
    return "".join(result)


def decode(encoded: str) -> str:
    """
    Exact inverse of encode. Counts may be multi-digit (e.g., "12a" -> 12 copies of 'a').
    Empty string returns empty string.
    For any valid input, decode(encode(s)) == s holds.
    """
    if not encoded:
        return ""
    result = []
    i = 0
    while i < len(encoded):
        j = i
        while j < len(encoded) and encoded[j].isdigit():
            j += 1
        count = int(encoded[i:j])
        char = encoded[j]  # j is the position of the character
        result.append(char * count)
        i = j + 1
    return "".join(result)
