def encode(text: str) -> str:
    if not text:
        return ""

    parts = []
    current = text[0]
    count = 1

    for char in text[1:]:
        if char == current:
            count += 1
        else:
            parts.append(f"{count}{current}")
            current = char
            count = 1

    parts.append(f"{count}{current}")
    return "".join(parts)


def decode(encoded: str) -> str:
    parts = []
    index = 0

    while index < len(encoded):
        start = index
        while index < len(encoded) and encoded[index].isdigit():
            index += 1

        count = int(encoded[start:index])
        char = encoded[index]
        parts.append(char * count)
        index += 1

    return "".join(parts)
