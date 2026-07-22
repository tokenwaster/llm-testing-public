"""Run-length encoding and decoding for letter-only strings."""


def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
    if not text:
        return ""
    result = []
    prev = text[0]
    count = 1
    for char in text[1:]:
        if char == prev:
            count += 1
        else:
            result.append(f"{count}{prev}")
            prev = char
            count = 1
    result.append(f"{count}{prev}")
    return "".join(result)


def decode(encoded: str) -> str:
    """Inverse of encode; expands <count><char> pairs, counts may be multi-digit."""
    result = []
    digits = ""
    for ch in encoded:
        if ch.isdigit():
            digits += ch
        else:
            result.append(ch * int(digits))
            digits = ""
    return "".join(result)
