def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
    if not text:
        return ""
    result = []
    count = 1
    prev = text[0]
    for char in text[1:]:
        if char == prev:
            count += 1
        else:
            result.append(str(count))
            result.append(prev)
            prev = char
            count = 1
    result.append(str(count))
    result.append(prev)
    return "".join(result)


def decode(encoded: str) -> str:
    """Expand an encoded string back to the original."""
    if not encoded:
        return ""
    result = []
    i = 0
    n = len(encoded)
    while i < n:
        j = i
        while j < n and encoded[j].isdigit():
            j += 1
        count = int(encoded[i:j])
        char = encoded[j]
        result.append(char * count)
        i = j + 1
    return "".join(result)
