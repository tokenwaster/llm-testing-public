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
        while i < n and text[i] == char:
            count += 1
            i += 1
        res.append(f"{count}{char}")
    return "".join(res)

def decode(encoded: str) -> str:
    """
    Decodes the run-length encoded string back to its original form.
    Example: decode("12a3b") returns "aaaaaaaaaaaabbb".
    """
    if not encoded:
        return ""
    
    res = []
    num_str = ""
    for char in encoded:
        if char.isdigit():
            num_str += char
        else:
            # When a non-digit character is encountered, parse the accumulated count
            count = int(num_str)
            res.append(char * count)
            num_str = ""
    return "".join(res)
