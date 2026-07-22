def encode(text: str) -> str:
    if not text:
        return ""
    result = []
    count = 1
    current = text[0]
    for char in text[1:]:
        if char == current:
            count += 1
        else:
            result.append(f"{count}{current}")
            current = char
            count = 1
    result.append(f"{count}{current}")
    return "".join(result)


def decode(encoded: str) -> str:
    if not encoded:
        return ""
    result = []
    i = 0
    n = len(encoded)
    while i < n:
        num_str = ""
        while i < n and encoded[i].isdigit():
            num_str += encoded[i]
            i += 1
        count = int(num_str)
        char = encoded[i]
        i += 1
        result.append(char * count)
    return "".join(result)
