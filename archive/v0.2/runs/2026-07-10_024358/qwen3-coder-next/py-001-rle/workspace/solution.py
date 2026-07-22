def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char> format."""
    if not text:
        return ""
    
    result = []
    count = 1
    current_char = text[0]
    
    for i in range(1, len(text)):
        if text[i] == current_char:
            count += 1
        else:
            result.append(str(count) + current_char)
            current_char = text[i]
            count = 1
    
    # Don't forget the last run
    result.append(str(count) + current_char)
    
    return ''.join(result)


def decode(encoded: str) -> str:
    """Decode <count><char> format back to original string."""
    if not encoded:
        return ""
    
    result = []
    i = 0
    
    while i < len(encoded):
        # Collect all digits to form the count
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        # After digits should be a character
        if i < len(encoded):
            char = encoded[i]
            count = int(count_str)
            result.append(char * count)
            i += 1
    
    return ''.join(result)
