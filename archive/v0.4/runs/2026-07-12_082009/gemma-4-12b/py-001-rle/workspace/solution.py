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
        count = 1
        current_char = text[i]
        # Count consecutive occurrences of the current character
        while i + 1 < n and text[i+1] == current_char:
            count += 1
            i += 1
        
        result.append(f"{count}{current_char}")
        i += 1
        
    return "".join(result)

def decode(encoded: str) -> str:
    """
    The exact inverse of encode. Handles multi-digit counts.
    Example: decode("12a") returns "aaaaaaaaaaaa".
    """
    if not encoded:
        return ""
    
    result = []
    i = 0
    n = len(encoded)
    
    while i < n:
        count_str = ""
        # Collect all digits to form the count
        while i < n and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        # The character immediately following the digits is the one to repeat
        count = int(count_str)
        char = encoded[i]
        result.append(char * count)
        i += 1
        
    return "".join(result)
