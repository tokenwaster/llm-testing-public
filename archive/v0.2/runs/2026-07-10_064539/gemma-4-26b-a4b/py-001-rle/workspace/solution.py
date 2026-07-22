def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: encode("aaabcc") returns "3a1b2c".
    """
    if not text:
        return ""

    encoded_parts = []
    current_char = text[0]
    count = 0

    for char in text:
        if char == current_char:
            count += 1
        else:
            encoded_parts.append(f"{count}{current_char}")
            current_char = char
            count = 1

    # Append the final group after the loop finishes
    encoded_parts.append(f"{count}{current_char}")

    return "".join(encoded_parts)


def decode(encoded: str) -> str:
    """
    The exact inverse of encode. Decodes <count><char> format.
    Example: decode("12a3b") returns "aaaaaaaaaaaabbb".
    """
    if not encoded:
        return ""

    decoded_parts = []
    num_str = ""

    for char in encoded:
        if char.isdigit():
            # Accumulate digits for multi-digit counts
            num_str += char
        else:
            # When a non-digit character is encountered, parse the count and repeat the char
            count = int(num_str)
            decoded_parts.append(char * count)
            num_str = ""

    return "".join(decoded_parts)
