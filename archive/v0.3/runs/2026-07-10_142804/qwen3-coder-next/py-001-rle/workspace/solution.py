def encode(text: str) -> str:
    """Compress runs of repeated characters into <count><char> format."""
    if not text:
        return ""
    
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        count = 1
        # Count consecutive occurrences
        while i + count < len(text) and text[i + count] == char:
            count += 1
        result.append(str(count) + char)
        i += count
    
    return "".join(result)


def decode(encoded: str) -> str:
    """Decode run-length encoded string back to original."""
    if not encoded:
        return ""
    
    result = []
    i = 0
    while i < len(encoded):
        # Extract the count (may be multiple digits)
        count_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            count_str += encoded[i]
            i += 1
        
        if i < len(encoded):
            char = encoded[i]
            count = int(count_str) if count_str else 1
            result.append(char * count)
            i += 1
    
    return "".join(result)
