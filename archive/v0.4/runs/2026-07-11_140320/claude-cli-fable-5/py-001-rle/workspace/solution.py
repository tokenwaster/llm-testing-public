"""Run-length encoding and decoding for alphabetic strings."""


def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
    if not text:
        return ""
    parts = []
    prev = text[0]
    count = 1
    for char in text[1:]:
        if char == prev:
            count += 1
        else:
            parts.append(f"{count}{prev}")
            prev = char
            count = 1
    parts.append(f"{count}{prev}")
    return "".join(parts)


def decode(encoded: str) -> str:
    """Expand <count><char> pairs back into the original string."""
    parts = []
    count_digits = []
    for char in encoded:
        if char.isdigit():
            count_digits.append(char)
        else:
            parts.append(char * int("".join(count_digits)))
            count_digits = []
    return "".join(parts)
