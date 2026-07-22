def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: encode("aaabcc") returns "3a1b2c".
    """
    if not text:
        return ""

    result = []
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        count = 0
        while i < n and text[i] == char:
            count += 1
            i += 1
        result.append(f"{count}{char}")
    return "".join(result)


def decode(encoded: str) -> str:
    """
    Decodes the run-length encoded string back to its original form.
    Example: decode("3a1b2c") returns "aaabcc".
    """
    if not encoded:
        return ""

    result = []
    current_digit_str = ""
    for char in encoded:
        if char.isdigit():
            current_digit_str += char
        else:
            # The character is a letter, so it marks the end of the current count
            count = int(current_digit_str)
            result.append(char * count)
            current_digit_str = ""
    return "".join(result)
