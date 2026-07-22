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
        char = text[i]
        count = 0
        # Count consecutive occurrences of the same character
        while i < n and text[i] == char:
            count += 1
            i += 1
        res.append(f"{count}{char}")
    
    return "".join(res)


def decode(encoded: str) -> str:
    """
    The exact inverse of encode. Decodes <count><char> format.
    Example: decode("12a3b") returns "aaaaaaaaaaaabbb".
    """
    if not encoded:
        return ""
    
    res = []
    count_str = ""
    for char in encoded:
        if char.isdigit():
            # Accumulate digits for multi-digit counts
            count_str += char
        else:
            # When a non-digit character is found, it's the target character
            # to be repeated by the accumulated count.
            count = int(count_str)
            res.append(char * count)
            count_str = ""
            
    return "".join(res)
