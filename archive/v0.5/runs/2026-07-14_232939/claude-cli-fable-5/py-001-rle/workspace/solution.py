"""Run-length encoding: compress runs of repeated characters as <count><char>."""


def encode(text: str) -> str:
    """Encode text with run-length encoding, e.g. "aaabcc" -> "3a1b2c"."""
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
    """Decode run-length encoded text, e.g. "3a1b2c" -> "aaabcc"."""
    parts = []
    count = 0
    for char in encoded:
        if char.isdigit():
            count = count * 10 + int(char)
        else:
            parts.append(char * count)
            count = 0
    return "".join(parts)
