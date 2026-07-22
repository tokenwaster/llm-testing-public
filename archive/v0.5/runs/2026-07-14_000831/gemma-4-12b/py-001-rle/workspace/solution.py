def encode(text: str) -> str:
    """
    Compresses runs of repeated characters into <count><char>.
    Example: encode("aaabcc") returns "3a1b2c".
    """
    if not text:
        return ""

    encoded_parts = []
    current_count = 1
    
    # Iterate through the string starting from the second character
    for i in range(1, len(text)):
        if text[i] == text[i - 1]:
            current_count += 1
        else:
            # Append the count and the previous character to the result list
            encoded_parts.append(str(current_count) + text[i - 1])
            current_count = 1
            
    # Handle the final run of characters
    encoded_parts.append(str(current_count) + text[-1])
    
    return "".join(encoded_parts)

def decode(encoded: str) -> str:
    """
    The exact inverse of encode. Handles multi-digit counts.
    Example: decode("12a") returns 12 copies of "a".
    """
    if not encoded:
        return ""

    decoded_chars = []
    i = 0
    n = len(encoded)
    
    while i < n:
        count_str = ""
        # Collect all digits to handle multi-digit counts (e.g., "12a")
        while i < n and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        # The character immediately following the digits is the one to repeat
        count = int(count_str)
        char = encoded[i]
        decoded_chars.append(char * count)
        
        # Move to the next segment
        i += 1
        
    return "".join(decoded_chars)
