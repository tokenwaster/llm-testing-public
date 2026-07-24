def encode(text: str) -> str:
    if not text:
        return ""
    parts = []
    current = text[0]
    count = 1
    for ch in text[1:]:
        if ch == current:
            count += 1
        else:
            parts.append(f"{count}{current}")
            current = ch
            count = 1
    parts.append(f"{count}{current}")
    return "".join(parts)


def decode(encoded: str) -> str:
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
