def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: "aaabcc" -> "3a1b2c"
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
    Decodes the run-length encoded string back to its original form.
    Example: "3a1b2c" -> "aaabcc"
    """
    if not encoded:
        return ""
    
    res = []
    num_str = ""
    for char in encoded:
        if char.isdigit():
            # Accumulate digits to handle multi-digit counts
            num_str += char
        else:
            # When a non-digit character is encountered, it's the target character
            count = int(num_str)
            res.append(char * count)
            num_str = ""
            
    return "".join(res)
