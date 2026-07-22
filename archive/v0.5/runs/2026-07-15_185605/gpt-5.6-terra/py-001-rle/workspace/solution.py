def encode(text: str) -> str:
    if not text:
        return ""

    parts = []
    count = 1

    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            count += 1
        else:
            parts.append(f"{count}{text[i - 1]}")
            count = 1

    parts.append(f"{count}{text[-1]}")
    return "".join(parts)


def decode(encoded: str) -> str:
    if not encoded:
        return ""

    parts = []
    digits = []

    for char in encoded:
        if char.isdigit():
            digits.append(char)
        else:
            parts.append(char * int("".join(digits)))
            digits = []

    return "".join(parts)
