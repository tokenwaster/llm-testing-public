def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char> format."""
    if not text:
        return ""
    
    result = []
    current_char = text[0]
    count = 1
    
    for char in text[1:]:
        if char == current_char:
            count += 1
        else:
            result.append(f"{count}{current_char}")
            current_char = char
            count = 1
    
    # Append the final run
    result.append(f"{count}{current_char}")
    
    return "".join(result)


def decode(encoded: str) -> str:
    """Decode <count><char> format back to original string."""
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        # Parse the count (may be multi-digit)
        num_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            num_str += encoded[i]
            i += 1
        
        if not num_str:
            break
            
        count = int(num_str)
        
        # Parse the character
        if i < len(encoded):
            char = encoded[i]
            result.append(char * count)
            i += 1
    
    return "".join(result)
