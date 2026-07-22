def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: encode("aaabcc") returns "3a1b2c".
    """
    if not text:
        return ""
    
    res = []
    i = 0
    n = len(text)
    while i < n:
        count = 1
        char = text[i]
        # Check for consecutive identical characters
        while i + 1 < n and text[i + 1] == char:
            count += 1
            i += 1
        res.append(f"{count}{char}")
        i += 1
    return "".join(res)


def decode(encoded: str) -> str:
    """
    The exact inverse of encode. Decodes <count><char> format.
    Example: decode("3a1b2c") returns "aaabcc".
    """
    if not encoded:
        return ""
    
    res = []
    digits = ""
    for char in encoded:
        if char.isdigit():
            # Accumulate digits for multi-digit counts
            digits += char
        else:
            # Once a non-digit character is found, parse the count and repeat the char
            count = int(digits)
            res.append(char * count)
            digits = ""
    return "".join(res)
