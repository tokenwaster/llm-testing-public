def encode(text: str) -> str:
    """
    Compress runs of repeated characters into <count><char> format.
    
    Args:
        text: Input string containing only letters (a-z, A-Z)
        
    Returns:
        Encoded string where each run is represented as count followed by character
    """
    if not text:
        return ""
    
    result = []
    count = 1
    
    for i in range(len(text)):
        if i + 1 < len(text) and text[i] == text[i + 1]:
            count += 1
        else:
            result.append(f"{count}{text[i]}")
            count = 1
    
    return "".join(result)


def decode(encoded: str) -> str:
    """
    Decompress run-length encoded string back to original text.
    
    Args:
        encoded: String in <count><char> format (e.g., "3a1b2c")
        
    Returns:
        Decoded original string
    """
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        if encoded[i].isdigit():
            # Parse the full number (may be multi-digit)
            j = i
            while j < len(encoded) and encoded[j].isdigit():
                j += 1
            
            count = int(encoded[i:j])
            char = encoded[j]
            result.append(char * count)
            i = j + 1
        else:
            # Single character (shouldn't occur in valid RLE output but handle gracefully)
            result.append(encoded[i])
            i += 1
    
    return "".join(result)
