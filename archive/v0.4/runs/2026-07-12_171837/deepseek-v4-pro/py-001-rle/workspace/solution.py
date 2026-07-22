def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
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
    """Decode a run-length encoded string back to the original."""
    if not encoded:
        return ""
    result = []
    i = 0
    while i < len(encoded):
        # Parse the count (one or more digits)
        j = i
        while j < len(encoded) and encoded[j].isdigit():
            j += 1
        count = int(encoded[i:j])
        # The next character is the letter to repeat
        char = encoded[j]
        result.append(char * count)
        i = j + 1
    return "".join(result)
