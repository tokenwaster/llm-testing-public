def encode(text: str) -> str:
    """Run-length encode a string of letters."""
    if not text:
        return ""

    parts = []
    count = 1

    for index in range(1, len(text)):
        if text[index] == text[index - 1]:
            count += 1
        else:
            parts.append(f"{count}{text[index - 1]}")
            count = 1

    parts.append(f"{count}{text[-1]}")
    return "".join(parts)


def decode(encoded: str) -> str:
    """Decode a run-length encoded string."""
    if not encoded:
        return ""

    parts = []
    index = 0

    while index < len(encoded):
        start = index
        while index < len(encoded) and encoded[index].isdigit():
            index += 1

        if start == index or index >= len(encoded):
            raise ValueError("Invalid run-length encoded string")

        count = int(encoded[start:index])
        parts.append(encoded[index] * count)
        index += 1

    return "".join(parts)
