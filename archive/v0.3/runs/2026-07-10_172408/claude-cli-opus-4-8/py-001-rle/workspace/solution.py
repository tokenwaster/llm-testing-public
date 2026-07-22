def encode(text: str) -> str:
    if not text:
        return ""
    result = []
    prev = text[0]
    count = 1
    for ch in text[1:]:
        if ch == prev:
            count += 1
        else:
            result.append(f"{count}{prev}")
            prev = ch
            count = 1
    result.append(f"{count}{prev}")
    return "".join(result)


def decode(encoded: str) -> str:
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
