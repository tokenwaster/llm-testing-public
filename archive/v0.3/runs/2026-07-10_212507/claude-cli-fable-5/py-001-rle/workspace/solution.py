"""Run-length encoding: compress runs of repeated characters."""


def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char>."""
    if not text:
        return ""
    parts = []
    run_char = text[0]
    run_len = 1
    for ch in text[1:]:
        if ch == run_char:
            run_len += 1
        else:
            parts.append(f"{run_len}{run_char}")
            run_char = ch
            run_len = 1
    parts.append(f"{run_len}{run_char}")
    return "".join(parts)


def decode(encoded: str) -> str:
    """Inverse of encode: expand <count><char> pairs back to the original string."""
    parts = []
    count_digits = []
    for ch in encoded:
        if ch.isdigit():
            count_digits.append(ch)
        else:
            parts.append(ch * int("".join(count_digits)))
            count_digits = []
    return "".join(parts)
