def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char> format."""
    if not text:
        return ""
    
    result = []
    count = 1
    
    for i in range(1, len(text)):
        if text[i] == text[i-1]:
            count += 1
        else:
            result.append(str(count) + text[i-1])
            count = 1
    
    # Add the last run
    result.append(str(count) + text[-1])
    
    return "".join(result)


def decode(encoded: str) -> str:
    """Decode <count><char> format back to original string."""
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        # Extract the count (may be multi-digit)
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if not count_str:
            # No digits found, which shouldn't happen for valid encoding
            break
            
        count = int(count_str)
        
        # Extract the character to repeat
        if i < len(encoded):
            char = encoded[i]
            result.append(char * count)
            i += 1
    
    return "".join(result)
